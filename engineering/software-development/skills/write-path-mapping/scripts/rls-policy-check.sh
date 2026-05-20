#!/usr/bin/env bash
# rls-policy-check.sh — For Supabase/Postgres projects, map tables to their RLS policies.
# Usage: bash scripts/rls-policy-check.sh <project-root>
# Output: Plain-text listing of tables and their policies (or "NONE"). Always exits 0.
#
# Static-only: reads migration SQL files. For live state use live-db-probe.sh.
# Uses bulk grep passes (not per-file loops) for scalability.

set -euo pipefail

PROJECT_ROOT="${1:-.}"

if [ ! -d "$PROJECT_ROOT" ]; then
  echo "ERROR: target is not a directory: $PROJECT_ROOT" >&2
  exit 1
fi

cd "$PROJECT_ROOT"

# --- Choose search roots --------------------------------------------------------------
ROOTS=()
for dir in supabase/migrations migrations db/migrations; do
  [ -d "$dir" ] && ROOTS+=("$dir")
done

if [ ${#ROOTS[@]} -eq 0 ]; then
  echo "=== RLS Policy Check ==="
  echo "No Supabase/Postgres migration directories found."
  exit 0
fi

run_search() {
  local pattern="$1"
  if command -v rg >/dev/null 2>&1; then
    rg --no-heading --no-filename --color never -i \
       --glob '*.sql' \
       --glob '!node_modules/**' --glob '!.git/**' \
       -e "$pattern" "${ROOTS[@]}" 2>/dev/null || true
  else
    grep -rhiE --include='*.sql' \
      --exclude-dir=node_modules --exclude-dir=.git \
      -e "$pattern" "${ROOTS[@]}" 2>/dev/null || true
  fi
}

# --- Extract tables, policies, and RLS-enabled tables ---------------------------------
TABLES=$(run_search '^[[:space:]]*create[[:space:]]+(unlogged[[:space:]]+)?table[[:space:]]+' | \
  sed -E 's/^[[:space:]]*create[[:space:]]+(unlogged[[:space:]]+)?table[[:space:]]+(if[[:space:]]+not[[:space:]]+exists[[:space:]]+)?([a-zA-Z_.][a-zA-Z0-9_."]*).*/\3/i' | \
  tr -d '"' | sort -u)

POLICY_LINES=$(run_search 'create[[:space:]]+policy')

RLS_ENABLED=$(run_search 'alter[[:space:]]+table[[:space:]]+[a-zA-Z_."]+[[:space:]]+enable[[:space:]]+row[[:space:]]+level' | \
  sed -E 's/.*alter[[:space:]]+table[[:space:]]+([a-zA-Z_.][a-zA-Z0-9_."]*).*/\1/i' | \
  tr -d '"' | sort -u)

# Parse policies: try to extract (table_name, policy_name) from each line
POLICIES_TABLES=""
if [ -n "$POLICY_LINES" ]; then
  POLICIES_TABLES=$(echo "$POLICY_LINES" | \
    sed -nE 's/.*create[[:space:]]+policy[[:space:]]+"?([^"[:space:]]+)"?.*on[[:space:]]+([a-zA-Z_.][a-zA-Z0-9_."]*).*/\2\t\1/Ip' | \
    tr -d '"')
fi

echo "=== RLS Policy Check ==="
echo ""

# Tables with RLS enabled
echo "--- Tables with ENABLE ROW LEVEL SECURITY ---"
if [ -n "$RLS_ENABLED" ]; then
  echo "$RLS_ENABLED" | sed 's/^/  /'
else
  echo "  (none found)"
fi
echo ""

# Tables with policies
echo "--- Table -> Policies ---"
if [ -n "$POLICIES_TABLES" ]; then
  echo "$POLICIES_TABLES" | awk -F'\t' '{tables[$1] = tables[$1] ", " $2} END {for (t in tables) print "  " t " : " substr(tables[t], 3)}' | sort
else
  echo "  (none found)"
fi
echo ""

# Tables WITHOUT policies
echo "--- Tables WITHOUT any policy (CANDIDATES for missing-rls risk) ---"
UNPOLICED=0
POLICIES_ONLY_TABLES=""
if [ -n "$POLICIES_TABLES" ]; then
  POLICIES_ONLY_TABLES=$(echo "$POLICIES_TABLES" | awk -F'\t' '{print $1}' | sort -u)
fi
if [ -n "$TABLES" ]; then
  while IFS= read -r tbl; do
    [ -z "$tbl" ] && continue
    case "$tbl" in
      _prisma*|_supabase*|schema_migrations|ar_internal*) continue ;;
    esac
    if [ -n "$POLICIES_ONLY_TABLES" ]; then
      if ! echo "$POLICIES_ONLY_TABLES" | grep -qxF "$tbl"; then
        echo "  $tbl"
        UNPOLICED=$((UNPOLICED + 1))
      fi
    else
      echo "  $tbl"
      UNPOLICED=$((UNPOLICED + 1))
    fi
  done <<<"$TABLES"
fi
[ "$UNPOLICED" -eq 0 ] && echo "  (all tables have at least one policy)"
echo ""

# --- Summary --------------------------------------------------------------------------
TABLE_COUNT=$(echo "$TABLES" | grep -c . 2>/dev/null || echo 0)
POLICY_COUNT=$(echo "$POLICY_LINES" | grep -c . 2>/dev/null || echo 0)
RLS_COUNT=$(echo "$RLS_ENABLED" | grep -c . 2>/dev/null || echo 0)

echo "=== Summary ==="
echo "  Search roots:            ${ROOTS[*]}"
echo "  Tables discovered:       $TABLE_COUNT"
echo "  Policies discovered:     $POLICY_COUNT"
echo "  RLS-enabled tables:      $RLS_COUNT"
echo "  Unpoliced tables:        $UNPOLICED"

exit 0
