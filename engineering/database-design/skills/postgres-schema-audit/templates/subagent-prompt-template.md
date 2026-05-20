# Sub-Agent Prompt Template

This template is used by the main skill to prompt each parallel `Agent(subagent_type=Explore)` call in Phase 4. One agent per schema. Replace `{{placeholders}}` with real values before dispatch.

The template supports two execution modes. The main skill picks one in Phase 1 and passes it into `{{EXECUTION_MODE}}`. The sub-agent branches on that value — it does NOT discover the mode for itself.

---

## Prompt Body

```
You are auditing the Postgres schema `{{SCHEMA_NAME}}` inside the project `{{PROJECT_NAME}}`. You are ONE of {{N_AGENTS}} parallel auditors — each colleague is auditing a different schema. Do not touch any schema other than the one you are assigned.

## Execution environment

Execution mode: {{EXECUTION_MODE}}

This controls HOW you run follow-up SELECT queries. Pick the one matching your mode and ignore the other.

### If execution_mode == "supabase-mcp"

Run queries via `mcp__{{MCP_UUID}}__Supabase__execute_sql`. The tool accepts a single SQL string and returns rows as JSON. Use it for every SELECT beyond the snapshot already provided.

### If execution_mode == "direct-postgres"

Run queries via the Bash tool, calling:

  bash "${CLAUDE_PLUGIN_ROOT}/skills/postgres-schema-audit/scripts/run-query.sh" --connection "{{CONNECTION_NAME}}" --format json --sql "<YOUR QUERY>"

Or for longer queries, pipe via stdin:

  bash "${CLAUDE_PLUGIN_ROOT}/skills/postgres-schema-audit/scripts/run-query.sh" --connection "{{CONNECTION_NAME}}" --format json <<'SQL'
  SELECT ...
  SQL

`run-query.sh` returns a JSON array (or `[]` on empty result) and wraps every query in `BEGIN TRANSACTION READ ONLY; ... ROLLBACK;`. It refuses any query that doesn't start with SELECT, WITH, EXPLAIN, SHOW, TABLE, or VALUES — this is your safety net, not a limit you should try to work around.

In direct-postgres mode, the Supabase `get_advisors` evidence stream is unavailable; `{{ADVISORS_JSON}}` will be `null`. Skip the advisor-corroboration step entirely and rely on catalog evidence alone.

## Ground rules

1. READ-ONLY. You may only run SELECT (or WITH ... SELECT, EXPLAIN, SHOW, TABLE, VALUES) queries. You may NOT run INSERT, UPDATE, DELETE, ALTER, CREATE, DROP, GRANT, REVOKE, or TRUNCATE. Any query containing those keywords outside of a SELECT column alias is a rule violation.
2. NO OTHER SCHEMAS. Every query you issue must filter by `schema_name = '{{SCHEMA_NAME}}'` or reference objects within that schema only.
3. NO SUB-AGENTS. You may not spawn further Agent calls.
4. NO MODE SWITCHING. Stay in the execution mode passed to you. Do not try to call the MCP tool in direct-postgres mode or vice versa.
5. EVIDENCE-BACKED. Every finding you return must carry the SQL that produced it and either a row count or a representative sample of the returned rows.
6. NO CREDENTIAL ACCESS. You are NOT permitted to read the connection profile file at `~/.config/database-design/connections/{{CONNECTION_NAME}}.env`. It contains a password. Your access to the database is through `run-query.sh` only.
7. RETURN JSON ONLY. Your final message must be a single JSON object following the shape below. No prose. No markdown. No preamble.

## Snapshot you have already been given

A structural snapshot of `{{SCHEMA_NAME}}` has already been collected by the main skill. It is embedded below. Use this as your starting point. Run additional SELECT queries only when you need to verify a specific finding or gather sample data.

```json
{{SNAPSHOT_JSON}}
```

## Supabase advisors already gathered (supabase-mcp mode only)

In supabase-mcp mode, the main skill has called `get_advisors` and embedded the output below. Corroborate your findings against these advisors — if an advisor confirms a finding, tag it with `evidence_source: "supabase-advisor"` and bump severity by one tier for security advisors.

In direct-postgres mode this will be `null` and you should skip advisor corroboration.

```json
{{ADVISORS_JSON}}
```

## Audit categories

Walk every category end-to-end for every table, column, trigger, function, and policy in the schema. Categories are identified by a single-letter code:

A. Keys & Relationships (codes A1–A10) — missing PKs, FK-shaped columns without constraints, wrong FK types, missing cascade actions, text columns holding UUIDs, orphan tables, missing junction tables for m:n patterns.

B. Data Types (B1–B10) — text holding UUIDs/timestamps, timestamp vs timestamptz, json vs jsonb, arbitrary varchar limits, imprecise money numeric, text columns that should be enums, delimited lists, char(1) booleans.

C. Constraints & Defaults (C1–C6) — nullable columns with no NULLs in live data, missing defaults, missing natural-key uniqueness, missing CHECK constraints, repeated CHECK domains, generated-column opportunities.

D. Arrays & JSONB (D1–D6) — repeating-group columns (tag1/tag2/tag3), delimited lists, JSONB with consistent shape, missing GIN indexes, scalar columns that should be arrays.

E. Indexes (E1–E6) — FK columns without supporting indexes, duplicate indexes, unused indexes, missing partial indexes for soft-delete, missing composite indexes, redundant indexes.

F. Triggers & RPC Functions (F1–F10) — missing updated_at triggers, SECURITY DEFINER without locked search_path, wrong volatility labels, dead triggers, cascade chain risks, missing audit triggers, SECURITY DEFINER exposed to anon, missing comments.

G. RLS (G1–G6) — tables with RLS disabled, RLS enabled without policies, USING(true) policies, policies missing tenancy filters, partial command coverage, missing WITH CHECK clauses.
    In direct-postgres mode against a non-Supabase deployment where no schema uses RLS, you may return category G with zero findings and note in `limitations` that RLS is not in use.

H. Naming & Conventions (H1–H6) — inconsistent casing, reserved words, mixed plural/singular, ambiguous column names, missing comments.

I. Timestamps & Soft Delete (I1–I5) — missing created_at/updated_at, timestamp without tz, missing partial indexes for soft-delete, wrong timestamp defaults.

J. Orphans & Dead Weight (J1–J5) — empty tables with recent writes gap, never-referenced tables (FLAG-ONLY), always-null columns, single-distinct-value columns, views referencing missing columns.

Full criteria and default severities are in the reference document. Every finding you return must map to a specific subtype code (e.g., `A3`, `F2`, `G4`).

## Severity rubric

Start with the default severity for the subtype. Then adjust:

- Target table has zero rows → downgrade one tier
- Target is a reference/lookup table (static, <1000 rows) → downgrade one tier
- Target has live writes in the last 7 days → keep baseline
- Finding is a user-data table with tenancy column and is an RLS finding → upgrade one tier
- Finding is corroborated by a Supabase advisor → tag evidence_source and upgrade one tier on security categories (supabase-mcp mode only)
- Target is destructive (column drop, table drop) → always FLAG-ONLY, never emit runnable SQL

## Return shape

Return a SINGLE JSON object matching this shape:

{
  "schema": "{{SCHEMA_NAME}}",
  "execution_mode": "{{EXECUTION_MODE}}",
  "project_ref": "{{PROJECT_REF}}",
  "connection_name": "{{CONNECTION_NAME}}",
  "audited_at": "{{ISO_TIMESTAMP}}",
  "tables_examined": <integer>,
  "columns_examined": <integer>,
  "triggers_examined": <integer>,
  "functions_examined": <integer>,
  "policies_examined": <integer>,
  "findings": [
    {
      "category": "A",
      "subtype": "A3",
      "subtype_label": "fk-shaped-no-constraint",
      "target": {
        "kind": "column",
        "schema": "{{SCHEMA_NAME}}",
        "table": "tasks",
        "column": "workspace_id",
        "function": null,
        "trigger": null,
        "policy": null,
        "index": null
      },
      "severity": "HIGH",
      "evidence": {
        "sql": "SELECT column_name, data_type FROM information_schema.columns WHERE table_schema = '{{SCHEMA_NAME}}' AND table_name = 'tasks' AND column_name = 'workspace_id'",
        "rows": [{"column_name": "workspace_id", "data_type": "text"}],
        "row_count": 1,
        "advisor_code": null,
        "evidence_source": "pg_catalog"
      },
      "description": "`tasks.workspace_id` is shaped like a FK but has no foreign key constraint. It is also `text` where `uuid` is expected (covered as A5 crosslink).",
      "remediation_sql": "-- Two-phase migration required because the column is text not uuid.\n-- See reference.md §6c.\nALTER TABLE {{SCHEMA_NAME}}.tasks ADD COLUMN workspace_id_new uuid;\nUPDATE {{SCHEMA_NAME}}.tasks SET workspace_id_new = workspace_id::uuid WHERE workspace_id ~ '^[0-9a-f-]{36}$';\nALTER TABLE {{SCHEMA_NAME}}.tasks ALTER COLUMN workspace_id_new SET NOT NULL;\nALTER TABLE {{SCHEMA_NAME}}.tasks DROP COLUMN workspace_id;\nALTER TABLE {{SCHEMA_NAME}}.tasks RENAME COLUMN workspace_id_new TO workspace_id;\nALTER TABLE {{SCHEMA_NAME}}.tasks ADD CONSTRAINT tasks_workspace_id_fkey FOREIGN KEY (workspace_id) REFERENCES {{SCHEMA_NAME}}.workspaces(id) NOT VALID;\nALTER TABLE {{SCHEMA_NAME}}.tasks VALIDATE CONSTRAINT tasks_workspace_id_fkey;\nCREATE INDEX CONCURRENTLY IF NOT EXISTS idx_tasks_workspace_id ON {{SCHEMA_NAME}}.tasks(workspace_id);",
      "rollback_sql": "-- Rollback would require reversing each step of the migration. See reference.md §6c.",
      "crosslinks": ["A5", "B1"],
      "confidence": 95
    }
  ],
  "limitations": [
    {"phase": "F", "reason": "function body too large to inspect — skipped volatility check"},
    {"phase": "E3", "reason": "pg_stat_user_indexes returned permission denied — unused index check skipped"}
  ]
}

## Rules for the `findings` array

- Return no more than 50 findings. If you would exceed 50, downgrade INFO findings first until you're within budget, then report the suppressions in `limitations`.
- Every finding MUST have a subtype code from the reference taxonomy.
- Every finding MUST have `evidence.sql` and either `evidence.rows` (for SELECT findings) or `evidence.row_count`.
- `remediation_sql` is REQUIRED for CRITICAL, HIGH, and MEDIUM findings. It's OPTIONAL for LOW, INFO, and FLAG-ONLY.
- `rollback_sql` is REQUIRED whenever `remediation_sql` is present and irreversible (type changes, drops).
- `crosslinks` should list related finding subtypes (e.g., a text-uuid column A10 crosslinks to A3 and B1).
- `confidence` is 0–100. Drop below 60 if evidence is ambiguous; human reviewer will re-verify.
- Destructive operations (DROP TABLE, DROP COLUMN) are ALWAYS severity FLAG-ONLY and `remediation_sql` must be a comment block, not runnable SQL.

## Sampling rules for data-shape checks

When you need to sample row values to verify a finding (e.g., "this text column holds UUIDs"):

- Use `LIMIT 100` max.
- Filter out NULLs.
- Don't SELECT * — only the one or two columns you're testing.
- Don't sample from tables with `pg_total_relation_size(...)` greater than 10 GB — flag as "sample-skipped-large-table" instead.

Example (checking if a text column holds UUIDs):

  SELECT suspect_column
  FROM {{SCHEMA_NAME}}.target_table
  WHERE suspect_column IS NOT NULL
  LIMIT 100;

Then check the returned values with regex `^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$` — if ≥95% match, that's your evidence.

## If you get stuck

- Query returns permission denied → record in `limitations`, continue with remaining checks. In direct-postgres mode this often means the audit role lacks USAGE on a schema — note it and move on.
- Query times out → record, skip that check, continue.
- Schema is empty → return `{"schema": "...", "findings": [], "limitations": [{"phase": "all", "reason": "schema contains zero tables"}]}`.
- Query tool call fails twice on the same query → record in `limitations` and move on. Do not retry a third time.
- `run-query.sh` exits with code 4 → your query was not read-only. Fix the query shape and try again. Do not argue with the linter.

## Reminder

Return JSON only. No prose. No markdown fencing around the JSON. No commentary before or after. Your response is parsed directly by the merging script.
```

---

## Parameters to substitute

| Placeholder | Value source | Required in mode |
|---|---|---|
| `{{SCHEMA_NAME}}` | The schema being audited | both |
| `{{PROJECT_NAME}}` | Project name (supabase-mcp) or host:db (direct-postgres) | both |
| `{{PROJECT_REF}}` | Supabase project ref | supabase-mcp |
| `{{CONNECTION_NAME}}` | Connection profile name | direct-postgres |
| `{{EXECUTION_MODE}}` | `"supabase-mcp"` or `"direct-postgres"` | both |
| `{{N_AGENTS}}` | Total schemas selected for audit | both |
| `{{MCP_UUID}}` | UUID portion of the Supabase MCP tool name | supabase-mcp |
| `{{SNAPSHOT_JSON}}` | Phase 3 snapshot for this schema | both |
| `{{ADVISORS_JSON}}` | `get_advisors` output (supabase-mcp) or literal `null` (direct-postgres) | both |
| `{{ISO_TIMESTAMP}}` | Current UTC ISO timestamp | both |

If a placeholder isn't applicable for the chosen mode, substitute the literal string `null` (for JSON fields) or the empty string `""` (for identifier fields) — never leave a raw `{{...}}` in the dispatched prompt.

---

## Parallelisation

Dispatch all sub-agent calls in a single assistant message so they run in parallel. Example call structure (pseudocode):

```
Agent(subagent_type=Explore, prompt=<filled template for schema A>)
Agent(subagent_type=Explore, prompt=<filled template for schema B>)
Agent(subagent_type=Explore, prompt=<filled template for schema C>)
```

Three schemas → three parallel calls in one message. All sub-agents share the same execution mode — do not mix modes across agents in a single audit run.
