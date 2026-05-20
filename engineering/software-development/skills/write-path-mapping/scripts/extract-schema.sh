#!/usr/bin/env bash
# extract-schema.sh — Collect DB schema definitions from a project.
# Usage: bash scripts/extract-schema.sh <project-root>
# Output: JSON when jq is available, plain text otherwise. Always exits 0.
#
# Uses a single bulk grep per pattern so it scales to large migration corpora.

set -euo pipefail

PROJECT_ROOT="${1:-.}"

if [ ! -d "$PROJECT_ROOT" ]; then
  echo "ERROR: target is not a directory: $PROJECT_ROOT" >&2
  exit 1
fi

cd "$PROJECT_ROOT"

# --- Choose search roots --------------------------------------------------------------
ROOTS=()
for dir in supabase/migrations migrations db/migrate database/migrations alembic/versions sql schemas schema; do
  [ -d "$dir" ] && ROOTS+=("$dir")
done
# Specific single-file schemas
for f in prisma/schema.prisma src/db/schema.ts src/schema.ts db/schema.ts src/lib/db/schema.ts db/schema.rb knexfile.ts knexfile.js; do
  [ -f "$f" ] && ROOTS+=("$f")
done
if [ ${#ROOTS[@]} -eq 0 ]; then
  ROOTS=(".")
fi

run_search() {
  local pattern="$1"
  shift
  local glob="${1:-*.sql}"
  if command -v rg >/dev/null 2>&1; then
    rg --no-heading --line-number --color never -i \
       --glob "$glob" \
       --glob '!node_modules/**' --glob '!.git/**' --glob '!dist/**' \
       --glob '!build/**' --glob '!.next/**' --glob '!.turbo/**' \
       -e "$pattern" "${ROOTS[@]}" 2>/dev/null || true
  else
    grep -rniE --include="$glob" \
      --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=dist \
      --exclude-dir=build --exclude-dir=.next --exclude-dir=.turbo \
      -e "$pattern" "${ROOTS[@]}" 2>/dev/null || true
  fi
}

# --- Extract SQL tables ---------------------------------------------------------------
SQL_TABLES=$(run_search '^[[:space:]]*create[[:space:]]+(unlogged[[:space:]]+)?table' '*.sql' | \
  sed -E 's/^[^:]+:[^:]+:[[:space:]]*create[[:space:]]+(unlogged[[:space:]]+)?table[[:space:]]+(if[[:space:]]+not[[:space:]]+exists[[:space:]]+)?([a-zA-Z_.][a-zA-Z0-9_."]*).*/\3/i' | \
  tr -d '"' | sort -u)

# --- Extract Prisma models ------------------------------------------------------------
PRISMA_MODELS=""
if [ -f "prisma/schema.prisma" ]; then
  PRISMA_MODELS=$(grep -E '^model[[:space:]]+' prisma/schema.prisma 2>/dev/null | \
    sed -E 's/^model[[:space:]]+([A-Za-z0-9_]+).*/\1/' | sort -u)
fi

# --- Extract ActiveRecord tables -----------------------------------------------------
RAILS_TABLES=""
if [ -f "db/schema.rb" ]; then
  RAILS_TABLES=$(grep -E '^[[:space:]]*create_table' db/schema.rb 2>/dev/null | \
    sed -E 's/.*create_table[[:space:]]+"([^"]+)".*/\1/' | sort -u)
fi

# --- Merge and count ------------------------------------------------------------------
ALL_TABLES=$(printf '%s\n%s\n%s\n' "$SQL_TABLES" "$PRISMA_MODELS" "$RAILS_TABLES" | grep -v '^$' | sort -u)
TABLE_COUNT=$(echo "$ALL_TABLES" | grep -c . 2>/dev/null || echo 0)

# Count schema files actually searched
FILE_COUNT=0
for r in "${ROOTS[@]}"; do
  if [ -d "$r" ]; then
    FILE_COUNT=$(( FILE_COUNT + $(find "$r" -type f \( -name '*.sql' -o -name '*.prisma' -o -name 'schema.rb' \) 2>/dev/null | wc -l) ))
  elif [ -f "$r" ]; then
    FILE_COUNT=$(( FILE_COUNT + 1 ))
  fi
done

if command -v jq >/dev/null 2>&1; then
  jq -n \
    --argjson file_count "$FILE_COUNT" \
    --argjson table_count "$TABLE_COUNT" \
    --arg tables_csv "$(echo "$ALL_TABLES" | tr '\n' ',' | sed 's/,$//')" \
    --arg roots_csv "$(printf '%s,' "${ROOTS[@]}" | sed 's/,$//')" \
    '{
      schema_file_count: $file_count,
      table_count: $table_count,
      tables: ($tables_csv | split(",") | map(select(length > 0))),
      search_roots: ($roots_csv | split(","))
    }'
else
  echo "=== Schema Summary ==="
  echo "Search roots:    ${ROOTS[*]}"
  echo "Schema files:    $FILE_COUNT"
  echo "Tables found:    $TABLE_COUNT"
  echo ""
  if [ "$TABLE_COUNT" -gt 0 ]; then
    echo "Tables (first 100):"
    echo "$ALL_TABLES" | head -100 | sed 's/^/  - /'
  fi
fi

exit 0
