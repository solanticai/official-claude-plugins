#!/usr/bin/env bash
# Anthril — Container Audit: Dockerfile Parser
# Prints structural extract for sub-agent ingestion.
# Usage: bash parse-dockerfile.sh <path>

set -euo pipefail
FILE="${1:-}"
[ -z "$FILE" ] || [ ! -f "$FILE" ] && { echo "error: file not found" >&2; exit 1; }

echo "=== FILE: $FILE ==="
echo "=== LINES: $(wc -l < "$FILE") ==="
echo ""

echo "=== FROM ==="
grep -nE "^FROM " "$FILE" 2>/dev/null

echo ""
echo "=== USER ==="
grep -nE "^USER " "$FILE" 2>/dev/null

echo ""
echo "=== ARG ==="
grep -nE "^ARG " "$FILE" 2>/dev/null

echo ""
echo "=== ENV ==="
grep -nE "^ENV " "$FILE" 2>/dev/null

echo ""
echo "=== COPY / ADD ==="
grep -nE "^(COPY|ADD) " "$FILE" 2>/dev/null

echo ""
echo "=== RUN ==="
grep -nE "^RUN " "$FILE" 2>/dev/null

echo ""
echo "=== HEALTHCHECK ==="
grep -nE "^HEALTHCHECK " "$FILE" 2>/dev/null

echo ""
echo "=== ENTRYPOINT / CMD ==="
grep -nE "^(ENTRYPOINT|CMD) " "$FILE" 2>/dev/null

echo ""
echo "=== EXPOSE ==="
grep -nE "^EXPOSE " "$FILE" 2>/dev/null

echo ""
echo "=== STOPSIGNAL ==="
grep -nE "^STOPSIGNAL " "$FILE" 2>/dev/null
