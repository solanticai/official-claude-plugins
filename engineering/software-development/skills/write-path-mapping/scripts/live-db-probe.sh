#!/usr/bin/env bash
# live-db-probe.sh — Opportunistically query the live database for schema, triggers, and policies.
# Usage: bash scripts/live-db-probe.sh <project-root>
# Output: Plain text describing which probe path was used. Always exits 0.
#
# Behaviour:
#   1. If Supabase MCP is configured, emit guidance so the skill can use MCP tool calls instead.
#   2. If DATABASE_URL is set and psql is available, run read-only metadata queries.
#   3. Otherwise, exit gracefully with a "no live DB" notice.
#
# This script is non-interactive and NEVER prints credentials or writes to the DB.

set -euo pipefail

PROJECT_ROOT="${1:-.}"

if [ ! -d "$PROJECT_ROOT" ]; then
  echo "ERROR: target is not a directory: $PROJECT_ROOT" >&2
  exit 1
fi

cd "$PROJECT_ROOT"

echo "=== Live DB Probe ==="

# --- Check for Supabase MCP configuration ---------------------------------------------
MCP_CONFIGS=(".mcp.json" ".claude/.mcp.json" "$HOME/.claude/.mcp.json")
for cfg in "${MCP_CONFIGS[@]}"; do
  if [ -f "$cfg" ] && grep -q -i "supabase" "$cfg" 2>/dev/null; then
    echo "mode: supabase-mcp"
    echo "note: Supabase MCP is configured in $cfg."
    echo "      The skill should use the mcp__*__Supabase__* tool calls for"
    echo "      list_tables, execute_sql (SELECT only), get_advisors, list_migrations"
    echo "      instead of calling this script's psql path."
    echo "recommended_queries:"
    echo "  - select * from pg_policies where schemaname not in ('pg_catalog','information_schema');"
    echo "  - select tgname, tgrelid::regclass, tgfoid::regproc from pg_trigger where not tgisinternal;"
    echo "  - select table_schema, table_name from information_schema.tables where table_schema not in ('pg_catalog','information_schema');"
    exit 0
  fi
done

# --- Load DATABASE_URL from env or dotenv files --------------------------------------
DB_URL="${DATABASE_URL:-}"
if [ -z "$DB_URL" ]; then
  for env_file in .env.local .env.development .env; do
    if [ -f "$env_file" ]; then
      # Extract without echoing the value
      if grep -q '^DATABASE_URL=' "$env_file" 2>/dev/null; then
        # shellcheck disable=SC1090
        set -a
        . "$env_file" 2>/dev/null || true
        set +a
        DB_URL="${DATABASE_URL:-}"
        break
      fi
    fi
  done
fi

if [ -z "$DB_URL" ]; then
  echo "mode: none"
  echo "note: No DATABASE_URL found in environment or .env files, and no Supabase MCP configured."
  echo "      Skill will fall back to static schema analysis only."
  exit 0
fi

if ! command -v psql >/dev/null 2>&1; then
  echo "mode: none"
  echo "note: DATABASE_URL is set but psql is not installed. Skipping live probe."
  exit 0
fi

echo "mode: psql"
echo "note: Running read-only metadata queries against \$DATABASE_URL (not printed)."
echo ""

# Run queries with very short timeouts and only SELECT against metadata catalogs.
# Exit cleanly on any failure — never let a DB error crash the skill.

PSQL_OPTS=(--no-psqlrc --pset=footer=off --tuples-only --no-align
           --set=AUTOCOMMIT=off --set=ON_ERROR_STOP=off
           --command="SET statement_timeout = '3s';")

run_query() {
  local label="$1" query="$2"
  echo "--- $label ---"
  if ! psql "$DB_URL" "${PSQL_OPTS[@]}" --command="$query" 2>/dev/null; then
    echo "(query failed or returned no rows)"
  fi
  echo ""
}

run_query "User tables" \
  "select table_schema || '.' || table_name from information_schema.tables
   where table_schema not in ('pg_catalog','information_schema','pg_toast')
   order by 1 limit 500;"

run_query "RLS policies" \
  "select schemaname || '.' || tablename || ' :: ' || policyname || ' (' || cmd || ')'
   from pg_policies
   where schemaname not in ('pg_catalog','information_schema')
   order by schemaname, tablename, policyname limit 500;"

run_query "Tables with RLS enabled but no policies" \
  "select n.nspname || '.' || c.relname
   from pg_class c join pg_namespace n on n.oid = c.relnamespace
   where c.relrowsecurity = true
     and n.nspname not in ('pg_catalog','information_schema','pg_toast')
     and not exists (
       select 1 from pg_policies p
       where p.schemaname = n.nspname and p.tablename = c.relname
     )
   order by 1 limit 200;"

run_query "Triggers" \
  "select n.nspname || '.' || c.relname || ' :: ' || t.tgname || ' -> ' || p.proname
   from pg_trigger t
   join pg_class c on c.oid = t.tgrelid
   join pg_namespace n on n.oid = c.relnamespace
   join pg_proc p on p.oid = t.tgfoid
   where not t.tgisinternal
     and n.nspname not in ('pg_catalog','information_schema')
   order by 1 limit 500;"

run_query "pg_cron schedules (if installed)" \
  "select jobid, schedule, jobname, command
   from cron.job
   order by jobid limit 200;"

echo "=== Live probe complete ==="
exit 0
