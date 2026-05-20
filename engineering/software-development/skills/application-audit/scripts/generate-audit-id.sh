#!/usr/bin/env bash
# generate-audit-id.sh — Emit a unique audit ID in YYYYMMDD-HHMM format.
# Collisions are resolved by appending -1, -2, ...
#
# Usage: bash scripts/generate-audit-id.sh <project-root>
# Output: the audit ID, single line, no trailing newline.
# Exit 0 always (or 1 if the project root is bad).

set -euo pipefail

PROJECT_ROOT="${1:-.}"

if [ ! -d "$PROJECT_ROOT" ]; then
  echo "ERROR: target is not a directory: $PROJECT_ROOT" >&2
  exit 1
fi

cd "$PROJECT_ROOT" || exit 1

BASE_ID=$(date '+%Y%m%d-%H%M')
ID="$BASE_ID"
SUFFIX=1

while [ -d ".anthril/audits/$ID" ]; do
  ID="${BASE_ID}-${SUFFIX}"
  SUFFIX=$((SUFFIX + 1))
done

printf '%s' "$ID"
exit 0
