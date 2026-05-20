#!/usr/bin/env bash
# run-query.sh — Execute a read-only SELECT against a configured Postgres
# connection and return results as JSON.
#
# Usage:
#   bash run-query.sh [--connection NAME] [--format json|tsv|raw]
#
# Query source (pick one):
#   - Stdin:  echo "SELECT 1" | bash run-query.sh
#   - File:   bash run-query.sh -f query.sql
#   - Inline: bash run-query.sh --sql "SELECT 1"
#
# Guarantees:
#   - Query is linted: must start with SELECT, WITH, EXPLAIN, SHOW, or TABLE
#     (after stripping comments and leading whitespace). Anything else is
#     rejected before psql is invoked.
#   - Query runs inside BEGIN TRANSACTION READ ONLY; ... ROLLBACK; which means
#     the Postgres server itself refuses any write even if the lint is bypassed.
#   - statement_timeout is set per-session to PG_STATEMENT_TIMEOUT_MS from
#     the connection profile (default 30000ms).
#
# Output:
#   - json (default): a JSON array of row objects. Empty result = [].
#   - tsv: tab-separated with header row.
#   - raw: psql's default aligned output.
#
# Exit codes:
#   0  success
#   2  bad arguments
#   3  no connection configured
#   4  query failed lint (not a SELECT)
#   5  psql failed

set -euo pipefail

CONN_NAME=""
QUERY_FILE=""
INLINE_SQL=""
FORMAT="json"

while [ $# -gt 0 ]; do
  case "$1" in
    --connection) CONN_NAME="$2"; shift 2 ;;
    -f|--file)    QUERY_FILE="$2"; shift 2 ;;
    --sql)        INLINE_SQL="$2"; shift 2 ;;
    --format)     FORMAT="$2"; shift 2 ;;
    -h|--help)    sed -n '2,32p' "$0"; exit 0 ;;
    *)            echo "Unknown arg: $1" >&2; exit 2 ;;
  esac
done

# ----------------------------------------------------------------------------
# Resolve active connection profile
# ----------------------------------------------------------------------------
CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}"
CONN_DIR="$CONFIG_HOME/database-design/connections"
ACTIVE_FILE="$CONFIG_HOME/database-design/active-connection"

if [ -z "$CONN_NAME" ]; then
  # Prefer project-local pointer over user-global
  if [ -f ".database-design/active-connection" ]; then
    CONN_NAME=$(head -n1 ".database-design/active-connection" | tr -d '[:space:]')
  elif [ -f "$ACTIVE_FILE" ]; then
    CONN_NAME=$(head -n1 "$ACTIVE_FILE" | tr -d '[:space:]')
  fi
fi

if [ -z "$CONN_NAME" ]; then
  echo "ERROR: no connection specified and no active connection set." >&2
  echo "Run: bash setup-postgres.sh  — or pass --connection NAME" >&2
  exit 3
fi

ENV_FILE="$CONN_DIR/${CONN_NAME}.env"
if [ ! -f "$ENV_FILE" ]; then
  echo "ERROR: connection profile not found: $ENV_FILE" >&2
  echo "Available profiles:" >&2
  ls -1 "$CONN_DIR"/*.env 2>/dev/null | sed 's|.*/||; s|\.env$||; s/^/  - /' >&2 || echo "  (none)" >&2
  exit 3
fi

# Source the profile (safe because we control the file format)
# shellcheck disable=SC1090
set -a
. "$ENV_FILE"
set +a

if ! command -v psql >/dev/null 2>&1; then
  echo "ERROR: psql is not installed." >&2
  exit 5
fi

# ----------------------------------------------------------------------------
# Gather the query
# ----------------------------------------------------------------------------
if [ -n "$QUERY_FILE" ] && [ -n "$INLINE_SQL" ]; then
  echo "ERROR: specify EITHER -f OR --sql, not both." >&2
  exit 2
fi

if [ -n "$QUERY_FILE" ]; then
  if [ ! -f "$QUERY_FILE" ]; then
    echo "ERROR: file not found: $QUERY_FILE" >&2
    exit 2
  fi
  QUERY=$(cat "$QUERY_FILE")
elif [ -n "$INLINE_SQL" ]; then
  QUERY="$INLINE_SQL"
else
  # Read from stdin
  QUERY=$(cat)
fi

if [ -z "${QUERY//[[:space:]]/}" ]; then
  echo "ERROR: empty query." >&2
  exit 2
fi

# ----------------------------------------------------------------------------
# Lint the query: read-only prefix check
# ----------------------------------------------------------------------------
# Strip:
#   - leading whitespace and newlines
#   - leading SQL line comments (-- ...)
#   - leading SQL block comments (/* ... */)
# Then check the first keyword.
normalise_query() {
  local q="$1"
  # Remove line comments and block comments
  q=$(printf '%s' "$q" | perl -0777 -pe 's{/\*.*?\*/}{}gs; s/--[^\n]*//g')
  # Trim leading whitespace
  q=$(printf '%s' "$q" | sed -E 's/^[[:space:]]+//')
  printf '%s' "$q"
}

NORMALISED=$(normalise_query "$QUERY")
FIRST_WORD=$(printf '%s' "$NORMALISED" | awk '{print toupper($1)}' | tr -d '[:space:]')

case "$FIRST_WORD" in
  SELECT|WITH|EXPLAIN|SHOW|TABLE|VALUES) ;;  # allowed
  *)
    echo "ERROR: query does not start with a read-only keyword." >&2
    echo "       Allowed: SELECT, WITH, EXPLAIN, SHOW, TABLE, VALUES" >&2
    echo "       Got:     $FIRST_WORD" >&2
    echo "       This wrapper refuses any query that could write to the database." >&2
    exit 4
    ;;
esac

# Additional defence: refuse queries containing obvious mutation keywords as
# whole words. This is belt-and-braces — the READ ONLY transaction below is
# the authoritative safety net.
FORBIDDEN_REGEX='\b(INSERT|UPDATE|DELETE|ALTER|CREATE|DROP|GRANT|REVOKE|TRUNCATE|VACUUM|REINDEX|CLUSTER|COMMENT[[:space:]]+ON|REFRESH[[:space:]]+MATERIALIZED|COPY[[:space:]]+[^(]|SECURITY[[:space:]]+LABEL|LOCK[[:space:]]+TABLE|DO[[:space:]])\b'
if printf '%s' "$NORMALISED" | grep -iqE "$FORBIDDEN_REGEX"; then
  # EXPLAIN may legitimately precede a SELECT that is all fine; we only blocked
  # actual DML keywords above, so this match means the user passed something
  # like "SELECT ...; DROP TABLE x" — refuse.
  echo "ERROR: query contains a mutation keyword outside a comment." >&2
  echo "       Refusing to execute." >&2
  exit 4
fi

# Strip a single trailing semicolon so we can wrap the query in a subselect.
QUERY_CLEAN=$(printf '%s' "$QUERY" | sed -E ':a;N;$!ba;s/[[:space:]]*;[[:space:]]*$//')

# ----------------------------------------------------------------------------
# Execute
# ----------------------------------------------------------------------------
STMT_TIMEOUT="${PG_STATEMENT_TIMEOUT_MS:-30000}"
APP_NAME="${PGAPPNAME:-database-design-audit}"

PSQL_OPTS=(
  -v ON_ERROR_STOP=1
  --no-psqlrc
  --set "AUTOCOMMIT=off"
)

case "$FORMAT" in
  json)
    # Wrap the user's SELECT in a json_agg and return a single JSON string.
    # Use psql's -At to get tuples-only, unaligned output (the one JSON string
    # comes back cleanly).
    #
    # Use $USER_QUERY$ dollar-quoted marker is NOT needed because we're not
    # literalising the query — we're pasting it directly into a SELECT FROM (...).
    # The query source is trusted (came from the skill or the user's own hand).
    OUT=$(psql "${PSQL_OPTS[@]}" -At <<SQL
SET application_name = '$APP_NAME';
SET statement_timeout = $STMT_TIMEOUT;
BEGIN TRANSACTION READ ONLY;
SELECT COALESCE(
  (SELECT json_agg(_row) FROM (
$QUERY_CLEAN
  ) _row),
  '[]'::json
)::text;
ROLLBACK;
SQL
)
    RC=$?
    if [ $RC -ne 0 ]; then
      echo "ERROR: psql exited with code $RC" >&2
      echo "$OUT" >&2
      exit 5
    fi
    printf '%s\n' "$OUT"
    ;;

  tsv)
    psql "${PSQL_OPTS[@]}" -A -F $'\t' <<SQL
SET application_name = '$APP_NAME';
SET statement_timeout = $STMT_TIMEOUT;
BEGIN TRANSACTION READ ONLY;
$QUERY_CLEAN;
ROLLBACK;
SQL
    ;;

  raw)
    psql "${PSQL_OPTS[@]}" <<SQL
SET application_name = '$APP_NAME';
SET statement_timeout = $STMT_TIMEOUT;
BEGIN TRANSACTION READ ONLY;
$QUERY_CLEAN;
ROLLBACK;
SQL
    ;;

  *)
    echo "ERROR: unknown format '$FORMAT'. Use json, tsv, or raw." >&2
    exit 2
    ;;
esac

exit 0
