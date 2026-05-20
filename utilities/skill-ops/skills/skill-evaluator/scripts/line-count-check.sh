#!/usr/bin/env bash
# Report line count for a file along with a pass/warn/fail status against the
# 500-line SKILL.md soft cap.
#
# Usage: line-count-check.sh <path>
# Emits: JSON { "path": ..., "lines": N, "status": "pass|warn|fail" }

set -euo pipefail

FILE="${1:-}"
[ -z "$FILE" ] && { echo '{"error":"no-file"}'; exit 1; }
[ ! -f "$FILE" ] && { echo '{"error":"not-found"}'; exit 1; }

LINES=$(wc -l < "$FILE" | tr -d '[:space:]')

STATUS="pass"
if [ "$LINES" -gt 500 ]; then
  STATUS="fail"
elif [ "$LINES" -gt 450 ]; then
  STATUS="warn"
fi

printf '{"path":"%s","lines":%s,"status":"%s"}\n' "$FILE" "$LINES" "$STATUS"
