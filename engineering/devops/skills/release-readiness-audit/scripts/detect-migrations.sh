#!/usr/bin/env bash
# Anthril — Release Readiness: Migration Detector
# Lists migrations added/modified in the diff and flags potentially destructive DDL.
# Usage: bash detect-migrations.sh [--base main]

set -euo pipefail
BASE="main"
while [ $# -gt 0 ]; do
  case "$1" in
    --base) BASE="$2"; shift 2 ;;
    *) shift ;;
  esac
done

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "error: not a git repository" >&2
  exit 1
fi

echo "=== MIGRATION FILES IN DIFF ==="
git diff --name-only "$BASE"...HEAD 2>/dev/null \
  | grep -iE "(migration|migrate|alembic|db/migrate|prisma/migrations|supabase/migrations|sql/)" \
  | head -50

echo ""
echo "=== NEW MIGRATION CONTENTS ==="
git diff --name-only --diff-filter=A "$BASE"...HEAD 2>/dev/null \
  | grep -iE "(migration|migrate)/.*\\.(sql|py|rb|js|ts)$" \
  | head -30 \
  | while read -r f; do
    echo "--- $f ---"
    head -40 "$f" 2>/dev/null
    echo ""
  done

echo ""
echo "=== DESTRUCTIVE DDL PATTERNS ==="
git diff "$BASE"...HEAD 2>/dev/null \
  | grep -inE "^\\+.*(DROP TABLE|DROP COLUMN|ALTER COLUMN|RENAME COLUMN|RENAME TABLE|TRUNCATE |ADD COLUMN .* NOT NULL|DROP CONSTRAINT|DROP INDEX)" \
  | head -40

echo ""
echo "=== NON-CONCURRENT INDEX CREATION ==="
git diff "$BASE"...HEAD 2>/dev/null \
  | grep -inE "^\\+.*CREATE INDEX" \
  | grep -vE "CONCURRENTLY" \
  | head -20

echo ""
echo "=== BACKFILL HINTS (UPDATE statements in migrations) ==="
git diff "$BASE"...HEAD 2>/dev/null \
  | grep -inE "^\\+.*UPDATE .+ SET " \
  | head -20
