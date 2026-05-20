# Database Design — Anthril Plugin

A deep-audit skill for Postgres schemas. Works with **Supabase** (via MCP) and with **any other Postgres 13+ database** (AWS RDS, Google Cloud SQL, Neon, Railway, self-hosted, local) via a securely-stored read-only connection profile. Runs in `ultrathink` mode with parallel per-schema sub-agents and produces evidence-backed, severity-scored reports with draft migration SQL.

---

## Skills

| # | Skill | Purpose |
|---|---|---|
| 1 | `postgres-schema-audit` | Audits Postgres schemas for structural and relational design quality. One sub-agent per schema runs in parallel, each examining tables, columns, relationships, constraints, triggers, RPC functions, indexes, RLS policies, and array/JSONB design. Produces a markdown report, an ER diagram, a JSON sidecar, and a draft `migrations-suggested.sql` file. |

The skill is interview-driven (Phase 1 detects which connection mode is available, then asks which project/connection and which schemas to audit) and fail-loud when no connection is configured — it never fabricates findings.

---

## Installation

### Local development

```bash
claude --plugin-dir ./database-design
```

After Claude Code starts, run `/reload-plugins` to discover the skill.

### Marketplace install

```bash
/plugin install database-design@anthril-claude-plugins
```

---

## Connection modes

The plugin supports two ways of reaching your database. Either is fine on its own; configure both if you want to switch between them.

### Mode A — Supabase MCP (fastest setup for Supabase users)

If you have the Supabase MCP connector enabled in Claude Code, the skill detects it automatically and uses it for every query. Supabase's `get_advisors` endpoint becomes an additional evidence stream on top of the catalog inspection.

Nothing to install — just make sure the Supabase connector is enabled.

### Mode B — Direct Postgres (works with any Postgres 13+)

For RDS, Cloud SQL, Neon, Railway, self-hosted, local, or any other Postgres where the Supabase MCP isn't applicable, run the setup wizard from your terminal (not from chat):

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/postgres-schema-audit/scripts/setup-postgres.sh"
```

The wizard will:

1. Prompt for a connection name, host, port, database, username, password, and SSL mode.
2. Read the password with silent input (never echoed, never in shell history).
3. Test the connection with `SELECT 1`.
4. Write the profile to `~/.config/database-design/connections/<name>.env` at mode `0600`.
5. Print a SQL snippet for creating a dedicated read-only role (strongly recommended).

You can also pass a DATABASE_URL directly:

```bash
bash scripts/setup-postgres.sh --name prod --url "postgres://user:pass@host:5432/db?sslmode=require"
```

Once configured, re-run the skill — it'll detect the new profile.

### Mode detection

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/postgres-schema-audit/scripts/check-connection.sh"
```

Reports one of: `supabase-mcp`, `direct-postgres`, `both`, or `none`.

### Listing configured profiles (direct-postgres mode)

```bash
bash scripts/list-connections.sh              # text
bash scripts/list-connections.sh --format json # JSON
```

Passwords are never printed — only name, host, port, database, user, sslmode.

---

## Invocation

```
/database-design:postgres-schema-audit
/database-design:postgres-schema-audit public,operations
/database-design:postgres-schema-audit --project my-supabase-project
```

If no arguments are provided, the skill asks for the project/connection and schema list interactively.

---

## Prerequisites

### Required (pick one)

- **Either** a Supabase MCP connector enabled in Claude Code
- **Or** a direct-postgres connection profile configured via `setup-postgres.sh` (requires the `psql` client on your PATH)

### Optional

- **`supabase` CLI** on PATH for local project introspection
- **Dedicated read-only role** — highly recommended for direct-postgres mode; the setup wizard emits the SQL to create one

---

## Security posture

This plugin handles database credentials. The design decisions, spelled out:

- **Passwords are never typed into chat.** `setup-postgres.sh` is a terminal-interactive script using `read -s`. Claude never sees the password because it never reads the env file.
- **Credentials live outside the project.** Connection profiles are stored at `~/.config/database-design/connections/<name>.env` with mode `0600`. They are never written into the project directory where they could accidentally be committed.
- **Every query is read-only at two layers.**
  1. `run-query.sh` lints the query text and refuses anything that doesn't start with `SELECT`, `WITH`, `EXPLAIN`, `SHOW`, `TABLE`, or `VALUES`.
  2. The query is wrapped in `BEGIN TRANSACTION READ ONLY; ... ROLLBACK;` — Postgres itself refuses any write even if the lint were bypassed.
- **The skill never reads the env file.** Claude only calls `check-connection.sh` (which reports mode + profile names) and `list-connections.sh` (which reports non-secret metadata). The password stays on disk.
- **Recommended role model.** The setup wizard prints a ready-to-apply SQL snippet for creating an `audit_reader` role with the minimum grants needed. Using a dedicated read-only role is the strongest safety guarantee.

---

## Output artifacts

Every audit emits three files into the current working directory. Existing files are never overwritten without confirmation.

| File | Contents |
|---|---|
| `database-design-audit.md` | Main markdown report. Header includes execution mode and either the Supabase project ref or the connection name + host + db + user. Executive summary, per-schema findings, cross-schema relationships, risk register, ER diagram, prioritised action batches. |
| `database-design-audit.json` | Machine-readable findings following `templates/findings-schema.json`. |
| `migrations-suggested.sql` | Draft `ALTER TABLE`, `CREATE INDEX`, `CREATE POLICY`, `CREATE TRIGGER` statements. Every block is commented `-- MANUAL REVIEW REQUIRED — DO NOT APPLY BLINDLY` and grouped by severity. |

---

## What this skill audits

For every selected schema, the sub-agent walks these 10 categories:

| # | Category | Representative checks |
|---|---|---|
| A | Keys & Relationships | Missing PKs, FK-shaped columns with no constraint, TEXT columns holding UUIDs, missing junction tables, wrong FK actions |
| B | Data Types | TEXT storing timestamps/UUIDs, `timestamp` vs `timestamptz`, JSON vs JSONB, VARCHAR(n) arbitrary caps, NUMERIC without precision for money |
| C | Constraints & Defaults | Missing NOT NULL, missing natural-key uniqueness, missing CHECK constraints, candidates for domain types and generated columns |
| D | Arrays & JSONB | Repeating group columns → array, scalar delimited lists → array, JSONB with consistent shape → normalise, missing GIN indexes |
| E | Indexes | Unsupported FKs, duplicates, unused, missing partial indexes for soft-delete, missing composite indexes |
| F | Triggers & RPC Functions | Missing `updated_at` trigger, unlocked `search_path` in SECURITY DEFINER functions, dead triggers, cascade chains, volatility labels |
| G | RLS | Tables without RLS, RLS enabled with no policies, permissive `USING (true)`, SELECT without INSERT/UPDATE/DELETE equivalents. (Skipped in direct-postgres mode if no schema uses RLS.) |
| H | Naming & Conventions | Casing consistency, reserved words, singular/plural mixing, missing comments |
| I | Timestamps & Soft Delete | Missing `created_at`/`updated_at`, `timestamp` without tz, soft-delete without partial index |
| J | Orphans & Dead Weight | Tables never referenced, always-null columns, single-distinct-value columns, empty tables with recent writes gap |

The full check taxonomy, severity rules, and SQL snippets are in `skills/postgres-schema-audit/reference.md`.

---

## What this skill will NOT do

- **Run migrations.** The skill is read-only. It emits `migrations-suggested.sql` with every statement commented. Humans apply changes.
- **Drop data.** No `DROP`, no `DELETE`, no destructive suggestion is ever auto-applied. Column drops and table drops are flagged `MANUAL REVIEW REQUIRED`.
- **Accept credentials in chat.** If no connection is configured, the skill tells you to run `setup-postgres.sh` in your terminal — it will not take your password through the conversation.
- **Read the env file.** The skill never opens `~/.config/database-design/connections/*.env`. Queries go through `run-query.sh` which sources the env itself and isolates the credentials.
- **Fabricate findings.** Every finding includes the SQL query that produced it and the row count / evidence returned. If the evidence is ambiguous, the finding is marked `NEEDS HUMAN REVIEW` rather than promoted to CRITICAL.

---

## Skill structure

```
skills/postgres-schema-audit/
├── SKILL.md                          # Interview-driven main workflow (< 500 lines)
├── reference.md                      # Full check taxonomy, SQL library, scoring rules
├── LICENSE.txt                       # Apache 2.0
├── templates/
│   ├── output-template.md            # Main report skeleton
│   ├── findings-schema.json          # JSON sidecar schema
│   ├── subagent-prompt-template.md   # Per-schema sub-agent prompt (dual-mode)
│   └── db-design-ignore.example      # Suppression file example
├── examples/
│   └── example-output.md             # Fully realised example audit
└── scripts/
    ├── check-connection.sh           # Detects Supabase MCP and/or direct-postgres
    ├── setup-postgres.sh             # Interactive wizard for a new direct-postgres profile
    ├── list-connections.sh           # Lists configured profiles (no secrets printed)
    ├── run-query.sh                  # Read-only psql wrapper (for direct-postgres mode)
    ├── list-system-schemas.sh        # Prints system schemas to exclude
    └── audit-queries.sql             # Canonical SQL query library
```

---

## Troubleshooting

### `check-connection.sh` reports `mode: none` but I have a `.mcp.json`

The script searches for the literal string `supabase` (case-insensitive) inside the config. If your MCP server is named something else, either rename it or use direct-postgres mode via `setup-postgres.sh`.

### `setup-postgres.sh` fails with "psql: command not found"

Install the Postgres client. The setup script prints platform-specific instructions:
- macOS: `brew install libpq && brew link --force libpq`
- Ubuntu/Debian: `sudo apt install postgresql-client`
- Fedora/RHEL: `sudo dnf install postgresql`

### `run-query.sh` exits with code 4 — "query does not start with a read-only keyword"

The linter refused your query. This is a safety feature. Make sure the query starts with SELECT / WITH / EXPLAIN / SHOW / TABLE / VALUES (after comments are stripped). If you believe it's a false positive, file an issue — don't try to work around the check.

### The audit role can't see my tables

In direct-postgres mode with a dedicated read-only role, you need:

```sql
GRANT USAGE ON SCHEMA <schema_name> TO audit_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA <schema_name> TO audit_reader;
ALTER DEFAULT PRIVILEGES IN SCHEMA <schema_name>
  GRANT SELECT ON TABLES TO audit_reader;
```

Repeat for each schema you want audited. The setup wizard's final output includes a fuller template.

---

## Conventions

- **Australian English** in narrative
- **DD/MM/YYYY** date format
- **Markdown-first** outputs
- **Evidence-backed findings** — every finding carries the SQL that produced it and, where relevant, the `pg_catalog` row count

---

## License

MIT for the plugin wrapper — see `.claude-plugin/plugin.json`. Per-skill `LICENSE.txt` is Apache 2.0 boilerplate.

---

## Author

[Anthril](https://github.com/anthril) — `john@anthril.com`
