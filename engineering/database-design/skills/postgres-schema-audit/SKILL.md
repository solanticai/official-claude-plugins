---
name: postgres-schema-audit
description: Audit any Postgres schema (Supabase via MCP or any Postgres 13+ via read-only connection) for structural and relational design quality. Produces a markdown report, ER diagram, JSON sidecar, and draft migrations-suggested.sql. Use for database design, schema audit, FK/constraint/trigger/RPC review, or pre-migration cleanup.
argument-hint: [project-ref-or-schema-list]
allowed-tools: Read, Grep, Glob, Write, Edit, Bash(bash scripts/*:*), Bash(psql:*), Agent
effort: high
---

# Postgres Schema Audit

ultrathink

## Before You Start

1. **Detect available connection modes.** Run `scripts/check-connection.sh` to discover whether the user has a Supabase MCP connector configured, a direct-postgres profile configured, both, or neither. The skill's entire Phase 1 behaviour depends on this result.
2. **Do not invent project, connection, or schema names.** Every identifier the skill uses in queries must come from a real MCP response or a real `pg_namespace` row. Never synthesise names to fill gaps.
3. **Read-only guarantee.** Every SQL call in this audit is SELECT-only against `pg_catalog`, `information_schema`, and (rarely, for data-shape sampling) the target schema's tables with `LIMIT 100`. The skill never runs INSERT, UPDATE, DELETE, ALTER, CREATE, or DROP. Remediation is emitted as commented SQL the user applies themselves.
4. **Load `.db-design-ignore`.** If the current working directory contains this file, parse it and treat entries as suppression rules during Phase 6.
5. **Budget for sub-agents.** Phase 4 spawns one `Agent(subagent_type=Explore)` per selected schema. A project with 5 schemas means 5 parallel agents. Warn the user if they've selected more than 10 schemas and offer to narrow the scope.
6. **Never read credentials out loud.** If the user has a direct-postgres profile configured, the skill NEVER echoes the contents of `~/.config/database-design/connections/*.env` into the chat. Those files contain passwords. The skill only references connection names.

## User Context

$ARGUMENTS

Connection availability: !`bash "${CLAUDE_PLUGIN_ROOT}/skills/postgres-schema-audit/scripts/check-connection.sh"`

System schemas to exclude: !`bash "${CLAUDE_PLUGIN_ROOT}/skills/postgres-schema-audit/scripts/list-system-schemas.sh"`

---

## Audit Phases

Execute every phase in order. Each sub-agent in Phase 4 walks all ten audit categories (A–J) end-to-end. Findings are written into a structured JSON per sub-agent, then merged in Phase 6. The completeness scoring rubric in `${CLAUDE_PLUGIN_ROOT}/skills/postgres-schema-audit/reference.md` §8 measures trace thoroughness, NOT database quality — clean and messy schemas alike can score 100%. Database quality is captured in the Risk Register.

**Read-only guarantee.** This skill never writes to the database, never drops objects, and never applies migrations. It emits three local files: `database-design-audit.md`, `database-design-audit.json`, and `migrations-suggested.sql`.

---

### Phase 1: Connection Verification & Selection

**Objective:** Decide which connection mode the audit will use, confirm it works, and lock it in.

**Step 1: Read the mode from `check-connection.sh`.** The script prints a `mode:` line with one of four values: `supabase-mcp`, `direct-postgres`, `both`, or `none`. Branch on that value.

#### If `mode: none`

Neither a Supabase MCP connector nor a direct-postgres profile is configured. Offer the user both paths via `ask_user_input_v0`:

- **Option A — Supabase MCP.** Call `suggest_connectors` with the Supabase directory UUID. Stop and wait for the user's next message.
- **Option B — Any Postgres (direct).** Tell the user to run, in their own terminal:
  ```
  bash "${CLAUDE_PLUGIN_ROOT}/skills/postgres-schema-audit/scripts/setup-postgres.sh"
  ```
  and to return once the wizard reports "Setup complete." Do NOT try to collect credentials in chat — the setup wizard reads the password with silent input for a reason. Credentials in the conversation transcript are a security incident.

Once the user confirms they've completed one of the two paths, re-run `check-connection.sh` and proceed with the updated mode.

#### If `mode: supabase-mcp`

1. Call `mcp__*Supabase__list_organizations` and `mcp__*Supabase__list_projects`.
2. If `$ARGUMENTS` includes a project ref, match it. If zero or multiple match, ask via `ask_user_input_v0`.
3. If no ref was supplied and only one project is accessible, confirm with the user (`"I'll audit <project-name> — correct?"`) before continuing.
4. Record `project_ref`, `project_name`, and `execution_mode: "supabase-mcp"`.

#### If `mode: direct-postgres`

1. Run `bash scripts/list-connections.sh --format json` to enumerate configured profiles (names only — no credentials).
2. If an active connection is set, confirm with the user: `"I'll audit using the '<n>' connection (host=<host>, db=<db>, user=<user>). Correct?"` Host, db, and user come from `list-connections.sh` output — never read the env file yourself.
3. If no active connection is set but profiles exist, ask the user to pick.
4. Record `connection_name`, `execution_mode: "direct-postgres"`, and the host/db/user for the report header.

#### If `mode: both`

Ask the user which to use via `ask_user_input_v0`. Typical reasons to prefer each:
- **Supabase MCP** unlocks `get_advisors` (first-class security + performance hints) and doesn't require a custom role.
- **Direct Postgres** works with any Postgres role and lets the user audit with a dedicated read-only login.

#### Final step of Phase 1 — smoke test

- **Supabase MCP:** call `mcp__*Supabase__execute_sql` with `SELECT 1 AS ok`. If it fails, record the error and stop; ask the user to check their Supabase session.
- **Direct Postgres:** run `bash scripts/run-query.sh --connection <n> --sql "SELECT 1 AS ok"`. If it fails, record the error and stop; suggest the user re-run `setup-postgres.sh` or verify the role has USAGE on `pg_catalog`.

Store `execution_mode` and the relevant identifier (`project_ref` OR `connection_name`) for every subsequent phase.

---

### Phase 2: Schema Discovery & Selection

**Objective:** Enumerate real schemas and confirm which ones to audit. Same workflow for both modes — only the execution mechanism differs.

1. Run the schema-enumeration query:
   ```sql
   SELECT nspname AS schema_name
   FROM pg_namespace
   WHERE nspname NOT IN (
     'pg_catalog','information_schema','pg_toast',
     'auth','storage','realtime','vault','extensions',
     'graphql','graphql_public','net','pgsodium','pgsodium_masks',
     'supabase_functions','supabase_migrations',
     '_analytics','_realtime','cron','pgtle','tiger','tiger_data','topology'
   )
   AND nspname NOT LIKE 'pg_temp_%'
   AND nspname NOT LIKE 'pg_toast_temp_%'
   ORDER BY nspname;
   ```
   - In `supabase-mcp` mode: via `mcp__*Supabase__execute_sql`.
   - In `direct-postgres` mode: via `bash scripts/run-query.sh --connection <n>` with the query on stdin.

2. For each returned schema, run a fast footprint query: count of tables, views, functions, triggers, and enums. This helps the user decide which schemas deserve auditing.
3. Use `ask_user_input_v0` with `multi_select` to let the user pick schemas. Pre-check any schema names that appeared in `$ARGUMENTS`. If `$ARGUMENTS` named all schemas explicitly and they all exist, skip the prompt and confirm the list inline.
4. If the user selects more than 10 schemas, warn about the sub-agent budget and offer to continue or narrow.
5. Load `.db-design-ignore` (if present) and record the entries for Phase 6. Surface any pattern that doesn't match the selected schemas as a "stale ignore" warning at the end of the run.

---

### Phase 3: Per-Schema Inventory (preparatory SELECTs)

**Objective:** Produce a compact structural snapshot per schema that each sub-agent starts from. Running these queries once centrally avoids N duplicate queries.

For every selected schema, run the queries from `reference.md` §2 (mirrored in `scripts/audit-queries.sql`) that produce the schema snapshot:

- **Tables + columns** (`information_schema.columns` + `pg_catalog.pg_attribute` for array flags)
- **Primary keys and unique constraints** (`pg_constraint` where `contype IN ('p','u')`)
- **Foreign keys** (`pg_constraint` where `contype = 'f'` with `confkey`, `conkey`, `confrelid`, delete/update actions)
- **Check constraints** (`pg_constraint` where `contype = 'c'`)
- **Indexes** (`pg_indexes` + `pg_index` joined for partiality, uniqueness, predicate)
- **Triggers** (`pg_trigger` where `NOT tgisinternal` + function references)
- **Functions / RPCs** (`pg_proc` + `pg_language` + volatility + security label + `prosrc`)
- **RLS state and policies** (`pg_class.relrowsecurity` + `pg_policies`)
- **Enums and custom types** (`pg_type` + `pg_enum`)
- **Views and materialized views** (`pg_views`, `pg_matviews`)
- **Approximate row counts and sizes** (`pg_stat_user_tables` + `pg_total_relation_size`)
- **Index usage** (`pg_stat_user_indexes`) — only if available (requires elevated role on some managed DBs)

**Execution routing:** every query in this phase goes through the chosen `execution_mode`. Never mix modes mid-audit.

**Advisors are Supabase-only.** In `supabase-mcp` mode, call `mcp__*Supabase__get_advisors` with `type='security'` and `type='performance'` and include the results in every sub-agent's starting context. In `direct-postgres` mode, there is no advisor equivalent — set `advisors_json: null` in the sub-agent prompt and note the absence in the report header.

Store each schema's snapshot as a JSON object in memory keyed by schema name. These are inputs to the sub-agents in Phase 4.

---

### Phase 4: Parallel Sub-Agent Audit (one per schema)

**Objective:** Walk every selected schema through the ten audit categories, in parallel.

For each selected schema, spawn one `Agent(subagent_type=Explore)` using the prompt template at `${CLAUDE_PLUGIN_ROOT}/skills/postgres-schema-audit/templates/subagent-prompt-template.md`. Issue all sub-agent tool calls **in a single assistant message** so they run in parallel.

Each sub-agent receives:

- The schema name
- The pre-fetched snapshot JSON from Phase 3
- The audit category list from `reference.md` §3
- The severity rubric from `reference.md` §5
- The `get_advisors` output (security + performance) — OR `null` if direct-postgres
- The `execution_mode` — so it knows whether to call `mcp__*Supabase__execute_sql` or `bash scripts/run-query.sh`
- The `connection_name` (direct-postgres mode only)
- Permission to execute follow-up SELECT-only queries via the chosen mechanism

Each sub-agent returns a structured JSON matching `templates/findings-schema.json` §finding shape — one object per finding, with category, subtype, target (schema.table.column or schema.function or schema.trigger), evidence SQL, severity, and a suggested remediation snippet.

Sub-agents MUST NOT:
- Run mutating SQL (no INSERT/UPDATE/DELETE/ALTER/CREATE/DROP)
- Call other sub-agents (no recursion)
- Fabricate findings without evidence from `pg_catalog` or `information_schema`
- Return findings for schemas other than their assigned one
- Switch execution modes

If a sub-agent returns malformed JSON, record the failure as a Phase 4 limitation and continue with the other agents' output.

---

### Phase 5: Cross-Schema Analysis

**Objective:** Detect issues that span schema boundaries — relationships that cross schemas, enum duplication, and shared-table opportunities.

1. **Cross-schema foreign keys.** Extract every FK where `pg_namespace(conrelid).nspname != pg_namespace(confrelid).nspname`. Document these as dependencies and flag any that go in an unexpected direction (e.g., a lower-tier schema referencing a higher-tier one).
2. **Duplicate enum definitions.** If two schemas define enums with substantially overlapping labels, flag for consolidation into a shared schema.
3. **Shared lookup opportunities.** If two or more schemas have tables with the same name and similar structure (e.g., `public.status`, `operations.status`), flag as consolidation candidates.
4. **Cross-schema trigger references.** Triggers that fire functions in a different schema are surfaced — they're legitimate but worth noting for dependency graphs.

All cross-schema findings go into a single `cross_schema` block in the merged JSON, not into individual schema findings.

---

### Phase 6: Merge & Risk Register

**Objective:** Consolidate sub-agent output into one coherent report.

1. Collect every sub-agent's JSON output and the cross-schema block from Phase 5.
2. Deduplicate any finding that appears in multiple places (rare but possible for cross-schema FK issues).
3. Apply severity adjustments per `reference.md` §5:
   - Findings on empty tables (zero rows, no recent writes) downgrade one tier.
   - Findings on tables flagged by `get_advisors` with `level='ERROR'` keep their severity — these were independently verified by Supabase. (Skipped in direct-postgres mode.)
   - Findings explicitly matched by `.db-design-ignore` are suppressed and surfaced in the "Suppressed" appendix.
4. Assign stable IDs: `DB-001`, `DB-002`, ... in severity-then-category order (CRITICAL first, then HIGH, then MEDIUM, then INFO).
5. Build the Risk Register: one row per finding with severity, category, target, evidence, and remediation.

---

### Phase 7: Migration Suggestion Drafting

**Objective:** Produce draft SQL for every remediable finding, with strong guardrails.

For every finding whose severity is CRITICAL, HIGH, or MEDIUM, emit a SQL block into `migrations-suggested.sql` with:

```sql
-- =============================================================================
-- DB-NNN — <severity> — <category>.<subtype>
-- Target: <schema.object>
-- Evidence: <one-line summary>
-- MANUAL REVIEW REQUIRED — DO NOT APPLY BLINDLY
-- =============================================================================
-- Suggested change:
<ALTER / CREATE / etc statement>
-- Rollback:
<reverse statement or comment if irreversible>
```

**Rules:**

- **Never emit `DROP TABLE` or `DROP COLUMN`** directly. Data-loss operations are commented out with a leading `-- DANGER:` and an expanded safety checklist.
- **Never emit `DROP POLICY`** without a replacement immediately below it.
- **Every `CREATE INDEX`** uses `CONCURRENTLY` with a named index to avoid locks.
- **Every FK addition** uses `NOT VALID` + `VALIDATE CONSTRAINT` in two steps, with a comment explaining why.
- **Every RLS policy creation** includes both `USING` and `WITH CHECK` clauses where applicable.
- **Every data-type change** uses `USING <expr>::<new_type>` with a note that this may require a table rewrite.

If the finding is INFO-only or FLAG-ONLY, do not emit SQL — reference the finding by ID and direct the reader to the markdown report.

---

### Phase 8: Reporting

**Objective:** Render the final three artifacts.

1. **Main markdown report** (`database-design-audit.md`) using `templates/output-template.md`. Required sections: header table (includes `execution_mode` and either `project_ref` or `connection_name + host + db + user`), executive summary, per-schema findings, cross-schema analysis, risk register, ER diagram (Mermaid `erDiagram`), risk heatmap (Mermaid `pie`), action batches, suppressed appendix.
2. **JSON sidecar** (`database-design-audit.json`) following `templates/findings-schema.json`. All findings with full evidence.
3. **Draft migrations** (`migrations-suggested.sql`) grouped by severity and schema.

Write every file with the `Write` tool. If a file already exists, ask the user before overwriting.

Emit a completeness summary at the end of the chat response with the final tier, per-phase scores, and any gaps the user should rerun with narrower scope.

---

## Completeness Summary

| Phase | Focus | Weight |
|---|---|---|
| Phase 1 — Connection | Mode confirmed, smoke-test passed, project/connection locked in | Gate (0 or full) |
| Phase 2 — Schema selection | Real schemas listed, user confirmation captured | Gate |
| Phase 3 — Inventory | Full snapshot per schema | Coverage |
| Phase 4 — Sub-agent audit | All ten categories walked per schema | Coverage + depth |
| Phase 5 — Cross-schema | Cross-schema relationships enumerated | Depth |
| Phase 6 — Merge & register | Every finding has ID, severity, evidence | Depth |
| Phase 7 — Migration drafts | SQL emitted for CRITICAL/HIGH/MEDIUM | Depth |
| Phase 8 — Reporting | All required report sections rendered | Depth |

**Tiers:**

- **95–100** — FULLY AUDITED
- **80–94** — MOSTLY AUDITED (gaps listed)
- **60–79** — PARTIALLY AUDITED
- **<60** — INSUFFICIENT — rerun with narrower scope or resolve connection/schema access first

---

## Important Principles

- **The audit is evidence-backed or it doesn't exist.** Every finding carries the SQL query that produced it and the rows returned. "Some missing FKs" is not a finding; "`operations.tasks.workspace_id` is `text` not `uuid` and has no FK to `operations.workspaces.id`" is.
- **The skill never writes to the database.** Both execution modes run SELECTs only. In direct-postgres mode, `run-query.sh` lints the query and wraps it in `BEGIN TRANSACTION READ ONLY; ... ROLLBACK;` as a belt-and-braces guarantee. Remediation is emitted as commented SQL the user applies themselves.
- **Credentials never appear in chat.** For direct-postgres mode, the setup wizard reads passwords with silent input and writes them to a mode-0600 file outside the project root. The skill only references connection names — never the contents of the env file.
- **Column drops and table drops are FLAG-ONLY.** These operations destroy data. They are flagged with `MANUAL REVIEW REQUIRED — DO NOT AUTO-DELETE` and never appear as runnable SQL in `migrations-suggested.sql`.
- **Every mutation suggestion uses safe patterns.** FK additions are `NOT VALID` + `VALIDATE`. Index creations are `CONCURRENTLY`. Type changes include `USING` clauses and rewrite warnings.
- **Supabase advisors are first-class evidence when available.** In supabase-mcp mode, `get_advisors` output is merged into audit findings with `evidence_source: "supabase-advisor"`. In direct-postgres mode, this evidence layer is absent — the report header notes that, and findings rely solely on catalog inspection.
- **Completeness is not quality.** A schema can score 100% completeness and still have CRITICAL design issues. These are independent axes.
- **Parallel sub-agents, one per schema.** Schemas are independent audit units. Running them in parallel is the only way to finish large multi-schema projects in reasonable time.
- **Respect `.db-design-ignore`.** Treat entries as load-bearing and surface stale patterns as warnings.
- **Australian English, DD/MM/YYYY dates, markdown-first outputs.**

---

## Edge Cases

1. **Neither mode configured (`mode: none`).** Offer both paths. Do NOT try to audit from static migration files — that's what the `dead-code-audit` and `write-path-mapping` skills are for.
2. **Multiple Supabase projects accessible.** Always ask the user to pick. Never silently default.
3. **Multiple direct-postgres profiles configured but no active one.** Always ask. Never silently default to alphabetical-first.
4. **User runs `setup-postgres.sh` then returns.** Re-run `check-connection.sh` — do not assume the mode has changed without verifying.
5. **`psql` not installed on user's machine (direct-postgres mode).** `setup-postgres.sh` fails early with platform-specific install hints. If somehow reached via a pre-existing profile, `run-query.sh` reports the error cleanly.
6. **Role lacks access to a schema.** Record the schema as "inaccessible — role permissions" in the report. Do not fail the audit; continue with the accessible schemas. In direct-postgres mode this is common when the audit uses a dedicated read-only role — the user may need to `GRANT USAGE ON SCHEMA <n> TO audit_reader`.
7. **Schema is empty (zero tables).** Emit a "zero tables in `<schema>`" note and skip the sub-agent. This is valid.
8. **Table is empty (zero rows).** Sub-agents downgrade all findings on empty tables by one severity tier.
9. **Massive schema (>100 tables).** Spawn a single sub-agent but chunk the category sweep into 3–4 passes to avoid token-budget exhaustion. Report the chunking strategy in the audit header.
10. **Query tool returns an error.** Record the error verbatim, continue with whichever queries succeeded, and surface the failure in the report. Never silently retry with a different query.
11. **Cross-schema FKs across audited and non-audited schemas.** Only include them in the cross-schema analysis if both schemas were selected for audit.
12. **Schema names with mixed case or special characters.** Use `pg_namespace.nspname` exactly — no lowercasing, no trimming. Quote identifiers in emitted SQL.
13. **Tool failure mid-audit.** If a query fails partway through, record the failure, continue with remaining queries, and mark the affected category as "partial". Never abort the whole audit on a single query failure.
14. **User's own security model differs from defaults.** Don't assume tenancy columns are named `workspace_id` — inspect the FK graph and RLS policies to infer the tenancy convention in use before flagging `cross-tenant-leak` candidates.
15. **Direct-postgres mode, user on a non-Supabase platform.** Skip all RLS-enabled-but-no-policies findings if no RLS is in use anywhere in the selected schemas (likely a non-Supabase deployment). RLS is a Postgres feature but outside Supabase it's rarely a default expectation.
