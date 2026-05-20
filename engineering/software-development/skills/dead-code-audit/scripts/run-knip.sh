#!/usr/bin/env bash
# run-knip.sh — Wrapper for knip with sensible defaults for the dead-code-audit skill.
# Usage: bash scripts/run-knip.sh <project-root>
# Output: Knip JSON to stdout. Exits 0 even on findings (knip exits non-zero by default).

set -euo pipefail

PROJECT_ROOT="${1:-.}"

if [ ! -d "$PROJECT_ROOT" ]; then
  echo "ERROR: target is not a directory: $PROJECT_ROOT" >&2
  exit 1
fi

cd "$PROJECT_ROOT"

if [ ! -f "package.json" ]; then
  echo '{"error": "no package.json found", "files": [], "exports": [], "dependencies": [], "devDependencies": []}'
  exit 0
fi

# Try knip on PATH first, then npx, then bail gracefully.
if command -v knip >/dev/null 2>&1; then
  KNIP_CMD="knip"
elif command -v npx >/dev/null 2>&1; then
  KNIP_CMD="npx --no-install knip"
else
  echo '{"error": "knip not installed", "install": "npm install -D knip", "files": [], "exports": [], "dependencies": [], "devDependencies": []}'
  exit 0
fi

# Knip exits 1 when findings exist — that's the success path for an audit tool.
# Capture output and exit 0 unless the tool itself crashed.
OUTPUT=$($KNIP_CMD --reporter json 2>&1) || KNIP_EXIT=$?
KNIP_EXIT=${KNIP_EXIT:-0}

# Exit codes: 0 = no findings, 1 = findings (normal), 2+ = real error
if [ "$KNIP_EXIT" -ge 2 ]; then
  echo "{\"error\": \"knip crashed\", \"exit_code\": $KNIP_EXIT, \"output\": $(printf '%s' "$OUTPUT" | head -20 | sed 's/"/\\"/g' | awk '{printf "%s\\n",$0}' | sed 's/^/"/;s/$/"/') }"
  exit 0
fi

echo "$OUTPUT"
exit 0
