#!/usr/bin/env bash
# extract-triggers.sh — Collect CREATE TRIGGER / FUNCTION / POLICY statements.
# Usage: bash scripts/extract-triggers.sh <project-root>
# Output: Plain-text listing. Always exits 0.
#
# Uses a single bulk ripgrep/grep pass per pattern (not per-file) so it scales
# to projects with thousands of SQL files.

set -euo pipefail

PROJECT_ROOT="${1:-.}"

if [ ! -d "$PROJECT_ROOT" ]; then
  echo "ERROR: target is not a directory: $PROJECT_ROOT" >&2
  exit 1
fi

cd "$PROJECT_ROOT"

# Choose search roots — prefer known migration directories; fall back to .
ROOTS=()
for dir in supabase/migrations migrations db/migrate database/migrations alembic/versions sql schemas schema; do
  [ -d "$dir" ] && ROOTS+=("$dir")
done
if [ ${#ROOTS[@]} -eq 0 ]; then
  ROOTS=(".")
fi

# Build exclusion flags for node_modules etc.
run_search() {
  local pattern="$1"
  if command -v rg >/dev/null 2>&1; then
    rg --no-heading --line-number --color never -i \
       --glob '*.sql' \
       --glob '!node_modules/**' --glob '!.git/**' --glob '!dist/**' \
       --glob '!build/**' --glob '!.next/**' --glob '!.turbo/**' \
       -e "$pattern" "${ROOTS[@]}" 2>/dev/null || true
  else
    # grep fallback: use --include for file filter + --exclude-dir
    grep -rniE --include='*.sql' \
      --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=dist \
      --exclude-dir=build --exclude-dir=.next --exclude-dir=.turbo \
      -e "$pattern" "${ROOTS[@]}" 2>/dev/null || true
  fi
}

echo "=== DB Triggers ==="
TRIGGER_OUT=$(run_search '^[[:space:]]*create[[:space:]]+(or[[:space:]]+replace[[:space:]]+)?trigger')
if [ -n "$TRIGGER_OUT" ]; then
  echo "$TRIGGER_OUT" | sed 's/^/  /'
  TRIGGER_COUNT=$(echo "$TRIGGER_OUT" | grep -c .)
else
  echo "  (none)"
  TRIGGER_COUNT=0
fi

echo ""
echo "=== DB Functions ==="
FN_OUT=$(run_search '^[[:space:]]*create[[:space:]]+(or[[:space:]]+replace[[:space:]]+)?function')
if [ -n "$FN_OUT" ]; then
  echo "$FN_OUT" | sed 's/^/  /' | head -500
  FN_COUNT=$(echo "$FN_OUT" | grep -c .)
else
  echo "  (none)"
  FN_COUNT=0
fi

echo ""
echo "=== RLS Policies ==="
POL_OUT=$(run_search '^[[:space:]]*create[[:space:]]+policy')
if [ -n "$POL_OUT" ]; then
  echo "$POL_OUT" | sed 's/^/  /' | head -500
  POL_COUNT=$(echo "$POL_OUT" | grep -c .)
else
  echo "  (none)"
  POL_COUNT=0
fi

echo ""
echo "=== Summary ==="
echo "  Search roots:  ${ROOTS[*]}"
echo "  Triggers:      $TRIGGER_COUNT"
echo "  Functions:     $FN_COUNT"
echo "  Policies:      $POL_COUNT"

exit 0
