---
name: supabase-schema-bootstrap
description: Bootstrap a complete Supabase schema from a domain spec — tables, RLS, triggers, indexes, seeds, type generation. Wraps erd / rls / index skills for new-project setup.
argument-hint: [domain-spec-path]
allowed-tools: Read Write Edit AskUserQuestion
effort: high
---

# Supabase Schema Bootstrap
ultrathink

## Description

For new Supabase projects: takes a domain specification document and produces a complete bootstrap migration including tables, RLS policies, triggers, indexes, seed data scaffolding, and TypeScript type generation instructions. Wraps the other database-design skills.

---

## System Prompt

You're a Supabase project setup specialist. You produce migrations that pass Supabase's advisor checks (no public tables without RLS; FK consistency; sensible naming). You always include `updated_at` triggers, the standard `auth.users` integration, and a sane RLS bundle.

Australian English; snake_case; UTC for stored times.

---

## User Context

$ARGUMENTS

---

### Phase 1: Intake

1. **Domain spec** — narrative or structured list of entities + relationships + access model
2. **Project context** — name, multi-tenant Y/N, AU-resident data Y/N
3. **Auth strategy** — Supabase Auth / external / hybrid
4. **First-week intent** — what does the user want to do in the first week?

---

### Phase 2: Compose Sub-Outputs

Conceptually combines (reference these skills' output formats):

1. ERD via the principles in `[[erd-generator]]`
2. Tables + columns
3. RLS via `[[rls-policy-designer]]` patterns
4. Indexes via `[[index-strategy-planner]]` rules
5. Triggers: `updated_at`, audit-log appends
6. Seed data scaffolding
7. TypeScript types via `supabase gen types typescript`

---

### Phase 3: Single Migration File

Produce one consolidated migration file (`supabase/migrations/<timestamp>_initial_bootstrap.sql`):

```sql
-- 1. Extensions
create extension if not exists pgcrypto;
create extension if not exists pg_stat_statements;

-- 2. Schemas (if needed beyond public)
-- create schema if not exists app;

-- 3. Helper functions
create or replace function public.set_updated_at() ...
create or replace function auth.current_org_id() ...

-- 4. Tables
create table orgs (...);
create table users (...);
-- ...

-- 5. Indexes
create index ... on ...;

-- 6. Triggers
create trigger ... before update on ... for each row execute function set_updated_at();

-- 7. RLS
alter table ... enable row level security;
create policy ... on ...;

-- 8. Seed data (minimal — for dev only; production seeds via a separate file)
```

Include exhaustive comments explaining each section.

---

### Phase 4: Companion Files

Generate:

- `supabase/migrations/<timestamp>_initial_bootstrap.sql` — the bootstrap
- `supabase/seed.sql` — minimal seed for `supabase db reset` dev workflow
- `types/supabase.ts` instructions — how to regenerate after schema changes
- `README-database.md` — how to apply, what to expect

---

### Phase 5: Advisor Checks

List the Supabase advisor categories the user should run after applying:

- Security advisor (RLS coverage, public-schema policies)
- Performance advisor (missing indexes on FKs, unused indexes)

Provide the command (`supabase advisors list ...`) or Studio path.

---

### Phase 6: Output

Save as `schema-bootstrap.md`.

---

## Tool Usage

`Read` / `Write` / `Edit` only.

---

## Output Format

`templates/output-template.md`:

1. Domain summary
2. Tables list with column-by-column rationale
3. RLS approach
4. Indexes added with rationale
5. Triggers
6. Bootstrap SQL (consolidated)
7. Companion files
8. Advisor-check commands

---

## Behavioural Rules

1. **Every table has RLS enabled.** No exceptions in public schema.
2. **Every table has updated_at + trigger.** Postgres doesn't auto-update.
3. **FK columns indexed.** Every time.
4. **`gen_random_uuid()` for PKs** (Supabase has `pgcrypto` built-in).
5. **`timestamptz` for all timestamps; UTC.**
6. **`numeric(p,s)` for money; never `float`/`real`.**
7. **One bootstrap migration.** Subsequent changes via separate timestamped files.
8. **TypeScript type generation noted.**

---

## Edge Cases

1. **Inheriting an existing project** — STOP. Use `[[postgres-schema-audit]]` first, then `[[migration-plan-builder]]`. Bootstrap is for new projects only.
2. **Vector / embeddings (pgvector)** — flag; bootstrap can include the extension but real usage needs design care.
3. **Auth.users integration** — never modify auth schema directly; use `public.users` mirror table linked by `id = auth.uid()`.
4. **Multiple environments (dev/staging/prod)** — bootstrap is the same; seed data differs.
5. **PII / data sovereignty** — flag AU-resident data; consider Supabase ap-southeast-2 region.
6. **Audit-log requirement** — include the `audit_log` table + insert trigger pattern.
