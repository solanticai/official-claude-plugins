# Write Path Mapping Reference

Dense lookup tables, taxonomies, detection matrices, and scoring rules for the `write-path-mapping` skill. Loaded on demand from `SKILL.md`.

## Table of Contents

- [1. Write Entry-Point Taxonomy](#1-write-entry-point-taxonomy)
- [2. Persistence Target Taxonomy](#2-persistence-target-taxonomy)
- [3. Framework Entry-Point Detection Matrix](#3-framework-entry-point-detection-matrix)
- [4. Database Mutation Detection Matrix](#4-database-mutation-detection-matrix)
- [5. Authorization Pattern Matrix](#5-authorization-pattern-matrix)
- [6. Write-Path Risk Taxonomy](#6-write-path-risk-taxonomy)
- [7. Completeness Scoring Rubric](#7-completeness-scoring-rubric)
- [8. Verification Protocol (9 Steps)](#8-verification-protocol-9-steps)
- [9. Sub-Agent Playbook](#9-sub-agent-playbook)
- [10. Mermaid Diagram Conventions](#10-mermaid-diagram-conventions)
- [11. `.write-path-ignore` Format](#11-write-path-ignore-format)
- [12. Risk Severity → Report Section Map](#12-risk-severity--report-section-map)
- [13. Edge Cases (quick reference)](#13-edge-cases-quick-reference)

---

## 1. Write Entry-Point Taxonomy

Every entry in the map carries one of these `entry.type` values.

| Category | Subtype | Examples | Detection signal |
|---|---|---|---|
| HTTP | `http-post` | `POST /api/tasks` | Router registration, decorator, file convention |
| HTTP | `http-put` | `PUT /api/tasks/:id` | Same |
| HTTP | `http-patch` | `PATCH /api/tasks/:id` | Same |
| HTTP | `http-delete` | `DELETE /api/tasks/:id` | Same |
| HTTP | `http-write` | Generic write verb (Django view method, etc.) | Method-name heuristic |
| RPC | `trpc-mutation` | `router.task.create` | `.mutation()` on tRPC procedure |
| RPC | `grpc-unary-write` | `service.Create` | proto + servicer impl |
| GraphQL | `gql-mutation` | `Mutation { createTask }` | Schema + resolver map |
| Server Action | `next-server-action` | `'use server'` function | Directive + usage |
| RSC Form | `next-form-action` | `<form action={fn}>` | JSX + `'use server'` |
| CLI | `cli-command` | `cli.command("migrate")` | commander/click/yargs |
| Queue consumer | `queue-consumer` | BullMQ Worker, SQS consumer, Celery task | Handler registration |
| Scheduled | `cron-job` | `@Cron`, `pg_cron`, `schedule.rb` | Decorator, SQL, file |
| Webhook | `webhook-receiver` | Stripe, Svix, GitHub | Signature verifier + route |
| WebSocket | `ws-message-write` | Socket.io `.on('msg', …)` | Handler + write |
| Realtime | `realtime-broadcast-write` | Supabase channel.send + DB write | Broadcast API |
| Edge function | `edge-function-write` | Supabase / Vercel / CF Worker | `Deno.serve` / `fetch(request)` |
| Triggers | `db-trigger` | Postgres trigger function | Schema scan |
| Migrations | `migration-write` | DML in migration | SQL parse (informational only) |

**Rule of thumb:** if the entry is reachable by an external or time-based event AND it can cause persistence state to change, it's a write entry point.

---

## 2. Persistence Target Taxonomy

Every call that mutates state gets tagged with one of these `kind` values.

| Category | Subtype | Example API |
|---|---|---|
| Raw SQL | `sql-insert` / `sql-update` / `sql-delete` / `sql-upsert` / `raw-sql` | `pg.query('INSERT …')`, `client.execute('UPDATE …')` |
| Supabase JS | `supabase-from-insert` / `-upsert` / `-update` / `-delete` | `supabase.from('t').insert(…)` |
| Supabase JS | `supabase-rpc` | `supabase.rpc('fn', …)` (when fn mutates) |
| Supabase Storage | `supabase-storage-write` | `supabase.storage.from('b').upload(…)` |
| Prisma | `prisma-write` | `prisma.task.create/update/upsert/delete` |
| Prisma | `prisma-transaction` | `prisma.$transaction([...])` |
| Drizzle | `drizzle-write` | `db.insert(tasks).values(…)` |
| Kysely | `kysely-write` | `db.insertInto('t').values(…).execute()` |
| TypeORM | `typeorm-write` | `.save()`, `.insert()`, `.update()`, `.delete()`, `.softRemove()` |
| Sequelize | `sequelize-write` | `.create()`, `.update()`, `.destroy()`, `.bulkCreate()` |
| Mongoose | `mongoose-write` | `.save()`, `.create()`, `.updateOne()`, `.findOneAndUpdate()` |
| Django ORM | `django-orm-write` | `.save()`, `.objects.create()`, `.update()`, `.delete()` |
| SQLAlchemy | `sqlalchemy-write` | `session.add()`, `.merge()`, `.delete()`, `session.execute(insert(...))` |
| ActiveRecord | `active-record-write` | `.save`, `.create`, `.update`, `.destroy`, `.upsert` |
| Eloquent | `eloquent-write` | `->save()`, `->create()`, `->update()`, `->delete()` |
| Doctrine | `doctrine-write` | `EntityManager::persist()`, `::remove()`, `::flush()` |
| gorm | `gorm-write` | `.Create`, `.Save`, `.Updates`, `.Delete` |
| Cache | `cache-write` / `redis-write` | Redis `SET`/`HSET`/`DEL`/`XADD`, in-memory cache |
| Queue | `queue-publish` | SQS `SendMessageCommand`, BullMQ `queue.add(...)`, Supabase queue |
| File | `fs-write` | `fs.writeFile`, `writeFileSync`, `appendFile` |
| Object store | `s3-write` | `PutObjectCommand`, `putObject`, `upload` |
| External API | `external-api-write` | `fetch(url, { method: 'POST' })`, `axios.post/put/patch/delete` |
| Event | `event-emit` | `emitter.emit(...)`, `pubsub.publish(...)` |
| Metric (info only) | `metric-write` | Datadog/Prom counter increments |
| Audit | `audit-log-write` | Writes to audit/log tables |
| Trigger chain | `trigger-side-effect` | Write caused by a DB trigger firing |

**Writes not covered:** browser localStorage, ephemeral process memory, logger writes to stdout. These are not persistence in any meaningful sense.

---

## 3. Framework Entry-Point Detection Matrix

How to find write entry points for each supported framework.

| Framework | File/signal | Write verbs | Notes |
|---|---|---|---|
| Next.js App Router | `app/**/route.{ts,js}` exporting `POST/PUT/PATCH/DELETE`; Server Actions via `'use server'`; `<form action>` | Method functions + actions | `generateStaticParams` / `generateMetadata` are NOT writes |
| Next.js Pages Router | `pages/api/**/*.{ts,js}` with `req.method !== 'GET'` | Method branches | Route file = endpoint |
| Express | `app.post/put/patch/delete`, `router.post/…` | Explicit | Middleware chain captured via `.use(…)` |
| Fastify | `fastify.post/put/patch/delete`, plugin registration | Explicit | `preHandler` hooks = middleware |
| Hono | `app.post/put/patch/delete` | Explicit | Edge-compatible |
| Koa | `router.post/put/patch/del` | Explicit | koa-router |
| NestJS | `@Post`, `@Put`, `@Patch`, `@Delete`, `@MessagePattern`, `@EventPattern` | Decorator | `@UseGuards` = middleware |
| tRPC | `router({ create: publicProcedure.input(schema).mutation(…) })` | `.mutation()` | `input(schema)` IS the validator |
| GraphQL (Apollo / Mercurius / Yoga) | `Mutation.*` resolvers | Schema map | Subscriptions are NOT writes unless they publish |
| Django | `urls.py` → view method; `ModelViewSet`; `@csrf_exempt` | Method branches | `permission_classes` = middleware |
| Django REST Framework | `ViewSet`, `@action(methods=['post'])` | Decorator | Serializer = validator |
| FastAPI | `@router.post/put/patch/delete`, DI | Decorator | `Depends(auth)` = middleware |
| Flask | `@app.route(methods=['POST',...])` | Decorator | Blueprints supported |
| Rails | `config/routes.rb` (`post/put/patch/delete/resources`); controller actions `create/update/destroy` | Explicit | `before_action` = middleware |
| Laravel | `routes/web.php`, `routes/api.php` (`Route::post/…`, `Route::resource`) | Explicit | `->middleware('auth')` chain |
| Symfony | `#[Route(methods: ['POST'])]` | PHP8 attribute | Firewalls = middleware |
| Go net/http | `mux.HandleFunc`, chi/gorilla/gin/echo/fiber `POST/PUT/…` | Explicit | Middleware = handler wrap |
| Rust axum | `.route("/x", post(handler))` | Explicit | `Router::new().route(…)` |
| Rust actix | `#[post("/x")]`, `web::resource("/x").route(web::post())` | Attribute / builder | |
| Rust rocket | `#[post("/x", data = "<x>")]` | Attribute | |
| Supabase Edge Functions | `supabase/functions/<name>/index.ts` | `Deno.serve` handler | Env vars pre-populated |
| Cloudflare Workers | `fetch(request)` + router libs (hono, itty) | Explicit | `wrangler.toml` declares entries |
| Deno Deploy | Same as Workers (Deno.serve) | | |

---

## 4. Database Mutation Detection Matrix

How to recognise a call as a write once you're inside a handler.

| Stack | Write APIs | Heuristic |
|---|---|---|
| `pg` / `postgres-js` | `.query('INSERT/UPDATE/DELETE …')`, `sql\`UPDATE …\`` | SQL-verb regex on first arg / template tag |
| `@supabase/supabase-js` | `.from(x).insert/upsert/update/delete`, `.rpc('fn')` where fn is VOLATILE | Method chain + RPC cross-ref |
| Prisma | `prisma.<model>.create/createMany/update/updateMany/upsert/delete/deleteMany` | Method name allowlist |
| Drizzle | `db.insert(table).values(…)`, `db.update`, `db.delete` | Import + method |
| Kysely | `.insertInto`, `.updateTable`, `.deleteFrom` | Builder entry |
| TypeORM | `.save`, `.insert`, `.update`, `.delete`, `.softRemove`, `.softDelete` | Repository method |
| Sequelize | `.create`, `.update`, `.destroy`, `.bulkCreate`, `.upsert` | Model method |
| Mongoose | `.save`, `.create`, `.updateOne`, `.updateMany`, `.deleteOne`, `.deleteMany`, `.findOneAndUpdate` | Model method |
| Django ORM | `.save()`, `.create()`, `.update()`, `.delete()`, `.get_or_create()`, `.update_or_create()`, `.bulk_create()`, `.bulk_update()` | QuerySet method |
| SQLAlchemy | `session.add`, `.merge`, `.delete`, `session.execute(insert/update/delete)` | Session method / `insert()` Core |
| ActiveRecord | `.save`, `.create`, `.update`, `.destroy`, `.update_attributes`, `.upsert`, `.insert_all` | Model method |
| Eloquent | `->save`, `->create`, `->update`, `->delete`, `::query()->insert` | Model method |
| Doctrine | `EntityManager::persist`, `::remove`, `::flush`, DQL `UPDATE`/`DELETE` | Method + DQL |
| sqlx / sqlc (Go) | `.Exec`, `.ExecContext`, query with `INSERT/UPDATE/DELETE` | SQL keyword |
| gorm | `.Create`, `.Save`, `.Updates`, `.Delete`, `.Upsert` | Method |
| sqlx (Rust) | `query!("INSERT …")`, `.execute` with DML | SQL-verb regex |
| Diesel | `insert_into(...)`, `update(...)`, `delete(...)` | DSL entry |

---

## 5. Authorization Pattern Matrix

Where authorization lives and how to detect it.

| Pattern | Where it runs | Detection |
|---|---|---|
| Route middleware (`authMiddleware`, `requireAuth`) | Before handler | Handler wrap or `.use(…)` |
| Next.js `middleware.ts` | Before any route | File presence + matcher config |
| NestJS Guards (`@UseGuards(AuthGuard)`) | Before handler | Decorator |
| FastAPI dependency / permission | Before handler | `Depends(get_current_user)` |
| Django permission classes / `@login_required` | Before view | View attribute / decorator |
| Rails `before_action :authenticate_user!` | Before action | Controller callback |
| Laravel middleware (`->middleware('auth')`) | Route definition | Chain call |
| Supabase RLS policies | Database layer (per-row) | Policy scan via `pg_policies` or migration files |
| Supabase service-role bypass | Edge function with service-role key | Grep for `SUPABASE_SERVICE_ROLE_KEY` |
| Row ownership check (`where user_id = auth.uid()`) | Handler or DB | AST on ORM / supabase calls |
| Policy objects (Pundit, CanCan, Laravel Gates) | Controller | Import + `authorize(...)` |
| JWT verification | Middleware | `jwt.verify`, `jose`, `pyjwt` |
| Session cookie | Middleware | `req.session`, `request.cookies` |
| API key check | Middleware / handler | Header grep + comparison |
| Webhook signature verification | Handler | `stripe.webhooks.constructEvent`, `svix.verify`, HMAC |
| Multi-tenant filter (`workspace_id = $1`) | Handler / RLS | AST check that every write includes tenant filter |

---

## 6. Write-Path Risk Taxonomy

Every path walks through this list in Phase 7. Flag with evidence.

| Subtype | Default severity | Meaning |
|---|---|---|
| `unauth-write` | CRITICAL | Write endpoint with no detectable auth layer |
| `missing-validation` | CRITICAL | Write endpoint with no schema validation on the request body |
| `missing-rls` | CRITICAL | Supabase write to a table with no RLS policy covering the role |
| `service-role-overreach` | CRITICAL | Edge function uses service-role key to write on behalf of user input without sanity checks |
| `sqli-risk` | CRITICAL | SQL string interpolation with user input (template-string SQL without parameters) |
| `cross-tenant-leak` | CRITICAL | Write omits tenant/workspace filter on a workspace-scoped table |
| `unverified-webhook` | CRITICAL | Webhook handler with no signature verification |
| `missing-transaction` | HIGH | Multiple writes in one handler without a transaction boundary |
| `race-condition` | HIGH | Read-modify-write without optimistic lock / row-lock / version column |
| `cache-invalidation-gap` | HIGH | DB write without a matching cache-key invalidation |
| `orphan-queue-consumer` | HIGH | Queue is published but no consumer found |
| `dead-trigger` | HIGH | DB trigger references a function that no longer exists |
| `file-upload-no-mime-check` | HIGH | Upload accepts any MIME type |
| `fan-out-write` | INFO / HIGH | One request writes to ≥3 targets. HIGH if transactional inconsistency possible |
| `unbounded-input` | MEDIUM | Write accepts arrays with no size limit |
| `idempotency-missing` | MEDIUM | Non-idempotent webhook/queue consumer without idempotency key |
| `missing-audit-log` | MEDIUM | Write to sensitive table without corresponding audit log entry |
| `missing-size-limit` | MEDIUM | Upload has no max file size |
| `external-api-no-timeout` | MEDIUM | Outbound API write without request timeout |
| `dynamic-dispatch-write` | INFO | Write target resolved at runtime (string key dispatch, reflection) |
| `orphan-queue-publish` | LOW | Consumer exists but nothing publishes to it |
| `external-api-no-retry` | LOW | Outbound API write without retry/backoff |

**Severity context adjustments:**

- `unauth-write` on a path protected by database RLS → downgrade to HIGH (not CRITICAL), because the database still enforces isolation. Note the mitigation in evidence.
- `missing-transaction` where only one persistence target exists → suppress (not a risk at all).
- `cross-tenant-leak` only fires when the target table has a `workspace_id` (or equivalent) column AND the write does NOT filter or default it.
- `dynamic-dispatch-write` is always INFO — the skill cannot evaluate dynamic dispatch, so it only flags for human review.

---

## 7. Completeness Scoring Rubric

Completeness measures **how thoroughly the skill traced the system**. It is NOT a quality grade. A clean codebase and a messy codebase can both score 100% on completeness.

### Two-axis model

| Axis | Formula | Max |
|---|---|---|
| Coverage | `traced_paths / discovered_paths` × 100 | 100 |
| Depth | `% of traced paths walked to verification step 9` | 100 |

**Phase completeness** = `min(Coverage, Depth)`
**Overall completeness** = `min(phase_completeness)` across all phases

### Adjustments (subtracted from phase completeness)

| Signal | Adjustment |
|---|---|
| Sub-agent NOT spawned for a domain with >30 candidate entries (Phase 2) | −15 |
| Sub-agent NOT spawned for a handler batch with >3 service layers (Phase 5) | −10 |
| Persistence target not enumerated for a path | −10 per path |
| Auth layer not recorded for a path | −10 per path |
| Middleware chain not recorded | −5 per path |
| Validator not checked | −5 per path |
| Risk taxonomy not walked for a path | −5 per path |
| `.write-path-ignore` not loaded | −10 (phase 1) |
| Live DB probe not attempted when credentials were available | −5 (phase 1) |
| Schema not ingested when present | −15 (phase 1) |
| Triggers not enumerated when present | −10 (phase 6) |
| Queue producers found without searching for consumers | −10 per unresolved queue |

### Completeness tiers

| Overall | Tier |
|---|---|
| 95–100 | **FULLY MAPPED** |
| 80–94 | **MOSTLY MAPPED** (gaps listed) |
| 60–79 | **PARTIALLY MAPPED** |
| <60 | **INSUFFICIENT** — rerun with sub-agents or narrower scope |

---

## 8. Verification Protocol (9 Steps)

Every path walks through these nine steps. The deepest reached step becomes `path.depth` in the sidecar. Stop early at step 6 for simple single-target writes.

| # | Step | Purpose |
|---|---|---|
| 1 | Entry-point resolution | Confirm the route/mutation/handler is actually registered |
| 2 | Middleware chain capture | Walk handler back through decorators / router wraps |
| 3 | Input validator detection | Zod/Yup/Joi/class-validator/Pydantic/DRF/struct tags |
| 4 | Authorization check | Route/middleware/RLS/ownership query |
| 5 | Handler trace | Walk AST into called service/repo/util functions |
| 6 | Persistence target enumeration | DB/cache/queue/file/external API/event |
| 7 | Transaction boundary check | Walk upward for a tx wrapper |
| 8 | Fan-out enumeration | Count distinct targets reached from the handler |
| 9 | Downstream async trace | Trigger firing? Cron followup? Queue consumer? Log every hop |

---

## 9. Sub-Agent Playbook

When and how to spawn parallel `Explore` sub-agents. All sub-agents return structured JSON only; none modify files.

### When sub-agents are MANDATORY

| Phase | Trigger | Partitioning | Prompt shape |
|---|---|---|---|
| **Phase 2** | Total discovered entries >30 | One agent per top-level domain folder (`app/`, `src/api/`, `supabase/functions/`, `workers/`, each monorepo package) | "Enumerate every write entry point in `<dir>`. For each return JSON: `{type, file, line, verb, route, framework, handler_name}` matching paths-schema.json §entry. Do not trace handlers — that's Phase 5. Return `{entries: [...]}`." |
| **Phase 5** | >30 handlers OR any handler with 3+ service-layer hops | Batches of 10 handlers | "Walk these 10 handlers: `<list>`. For each, resolve delegated calls transitively (services, repos, utils) and enumerate every persistence target reached. Return one JSON object per handler matching paths-schema.json path block. Flag `dynamic-dispatch-write` wherever dispatch is resolved at runtime." |

### When sub-agents are STRONGLY RECOMMENDED

| Phase | Trigger | Scope |
|---|---|---|
| **Phase 6** | Each unresolved queue/topic | "Find consumer for queue `<name>` anywhere in the repo, including sibling monorepo packages (`../cloudflare-workers`, `../workers/`), docker-compose services, supabase/functions/. Return `{consumers: [{file, line, handler}]}`." |
| **Phase 6** | Schema with >5 DB triggers | "Trace every `CREATE TRIGGER` in migrations. For each, return `{table, trigger_name, fn_name, target_table, fn_side_effects}`." |
| **Phase 7** | CRITICAL risk on a path with 3+ middleware layers | "Deep-verify the `<subtype>` risk on WP-NNN. Walk the middleware chain and confirm whether the compensating control exists (RLS policy, signature verification, rate limit, tenancy filter). Return `{confirmed: bool, evidence: string, severity_adjustment: string}`." |

### Parallel safety rules

1. Sub-agents ONLY read files and return JSON. They never modify files.
2. Sub-agents must not invoke more sub-agents (no recursion).
3. The main skill merges sub-agent output deterministically via `scripts/normalize-findings.py`.
4. If a sub-agent returns malformed JSON, the main skill records it as a Phase 2/5 limitation and continues with the other agents' data.

---

## 10. Mermaid Diagram Conventions

See `templates/mermaid-template.md` for full skeletons. Quick reference:

| Shape token | Meaning |
|---|---|
| `node[label]` | standard / entry point |
| `node[(label)]` | SQL table |
| `node[[label]]` | cache |
| `node((label))` | external API / domain event |
| `node[\label/]` | file / object storage |
| `node{{label}}` | queue / topic / DB function |
| `node{label}` | decision / auth gate |

Color classes applied to entry nodes based on their highest-severity risk:

| Class | Fill | Stroke | Meaning |
|---|---|---|---|
| `critical` | #ff6b6b | #c00 | 1+ CRITICAL risk |
| `high` | #ffa94d | #d97706 | 1+ HIGH risk |
| `medium` | #ffe066 | #d4a017 | 1+ MEDIUM risk |
| `info` | #a5d8ff | #1971c2 | 1+ INFO-only risk |
| `ok` | #b2f2bb | #2f9e44 | No risks |

---

## 11. `.write-path-ignore` Format

Identical parser to `.deadcode-ignore`. Every entry MUST include a justification comment — unjustified entries are reported as warnings during Phase 1.

**Pattern kinds:**

| Pattern | Matches |
|---|---|
| `app/**/route.ts:GET` | Suppress a specific verb in matching files |
| `WP-042` | Suppress an entire path by ID |
| `WP-042:missing-transaction` | Suppress a specific risk subtype on a specific path |
| `supabase/functions/_shared/**` | Glob: all files matching pattern |
| `generateMetadata` | Bare symbol: suppress any handler with this name |

**Stale ignores** (patterns that matched zero findings during the current run) are reported as warnings so users can clean them up.

See `templates/write-ignore.example` for a fully annotated example.

---

## 12. Risk Severity → Report Section Map

| Severity | Report section | Action list batch | Remediation priority |
|---|---|---|---|
| CRITICAL | §3a | 1, 2 | Immediate |
| HIGH | §3b | 3, 4 | Next sprint |
| MEDIUM | §3c | 5, 6 | Hardening backlog |
| INFO | §3d | 7 | Awareness only |
| OK | §3e | — | None |

---

## 13. Edge Cases (quick reference)

1. **Empty/prototype project** (<10 entries) — produce minimal map, no sub-agents needed.
2. **Monorepo** — per-package maps + cross-package rollup. Cross-package writes become fan-out edges.
3. **Serverless / edge** — each function file is an entry; cold-start logic counts as middleware.
4. **GraphQL** — each mutation resolver is an entry. Subscriptions are NOT writes unless they trigger DB publishes.
5. **Event-driven / CQRS** — commands are writes; events emitted from commands are fan-out.
6. **Multi-tenant** — tenancy isolation is critical. Missing `workspace_id`/`tenant_id` filter on a scoped table is `cross-tenant-leak` CRITICAL.
7. **Background workers** — consumers are secondary entry points. Map both producer and consumer; flag orphans.
8. **DB triggers / functions** — persistence-layer entry points with no app code. Map in Phase 6 from `extract-triggers.sh`.
9. **Dynamic SQL** — flag `sqli-risk` if the skill detects string interpolation; flag `dynamic-dispatch-write` if routing is resolved at runtime. Do not attempt to evaluate.
10. **Generated clients** (tRPC, Prisma, GraphQL codegen) — trace to the generator input, not the generated output. Add generator directories to `.write-path-ignore`.
11. **Tool failures** — record as a Phase 1 limitation and continue. Never abort.
