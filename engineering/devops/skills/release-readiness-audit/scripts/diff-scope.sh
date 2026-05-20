#!/usr/bin/env bash
# Anthril — Release Readiness: Diff Scope
# Usage: bash diff-scope.sh [--base main]

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

echo "=== BASE: $BASE ==="
echo "=== HEAD: $(git rev-parse --short HEAD 2>/dev/null) ==="
echo ""

echo "=== CHANGED FILES ==="
git diff --name-status "$BASE"...HEAD 2>/dev/null | head -200

echo ""
echo "=== MIGRATION FILES ==="
git diff --name-only "$BASE"...HEAD 2>/dev/null \
  | grep -iE "(migration|migrate)/" \
  | head -50

echo ""
echo "=== NEW ENV VARS (diff of .env.example) ==="
git diff "$BASE"...HEAD -- .env.example 2>/dev/null | grep -E "^\\+[A-Z_]+=" | head -30

echo ""
echo "=== DEPENDENCY CHANGES (package.json) ==="
git diff "$BASE"...HEAD -- "package.json" 2>/dev/null | grep -E "^[+-].+[\"]" | grep -v "^[+-]--" | head -40

echo ""
echo "=== DEPENDENCY CHANGES (requirements.txt / go.mod) ==="
git diff "$BASE"...HEAD -- requirements.txt go.mod 2>/dev/null | head -40

echo ""
echo "=== POTENTIAL DESTRUCTIVE DDL ==="
git diff "$BASE"...HEAD 2>/dev/null \
  | grep -iE "^\\+.*(DROP TABLE|DROP COLUMN|ALTER COLUMN|RENAME COLUMN|TRUNCATE |ADD COLUMN .* NOT NULL)" \
  | head -30

echo ""
echo "=== NEW EXTERNAL API CALL SITES (rough) ==="
git diff "$BASE"...HEAD 2>/dev/null \
  | grep -E "^\\+.*(fetch\\(|axios\\.|requests\\.get|http\\.Get)" \
  | head -20

echo ""
echo "=== COMMITS ==="
git log --oneline "$BASE"...HEAD 2>/dev/null | head -30
