#!/usr/bin/env bash
# Anthril — IaC Terraform Audit: HCL Parser
# Prints a structural summary of one module directory for sub-agent ingestion.
# Uses hcl2json when available; falls back to grep-based extraction.
# Usage: bash parse-hcl.sh <module-dir>

set -euo pipefail
DIR="${1:-.}"
[ ! -d "$DIR" ] && { echo "error: directory not found: $DIR" >&2; exit 1; }

echo "=== MODULE: $DIR ==="
echo "=== FILES ==="
find "$DIR" -maxdepth 1 -type f \( -name "*.tf" -o -name "*.tf.json" \) 2>/dev/null | sort

echo ""
echo "=== REQUIRED_PROVIDERS / REQUIRED_VERSION ==="
grep -nE "(required_providers|required_version)" "$DIR"/*.tf 2>/dev/null

echo ""
echo "=== BACKEND BLOCK ==="
grep -nE "^\\s*backend\\s+\"" "$DIR"/*.tf 2>/dev/null

echo ""
echo "=== PROVIDER BLOCKS ==="
grep -nE "^provider\\s+\"" "$DIR"/*.tf 2>/dev/null

echo ""
echo "=== RESOURCES ==="
grep -nE "^resource\\s+\"" "$DIR"/*.tf 2>/dev/null

echo ""
echo "=== DATA SOURCES ==="
grep -nE "^data\\s+\"" "$DIR"/*.tf 2>/dev/null

echo ""
echo "=== VARIABLES ==="
grep -nE "^variable\\s+\"" "$DIR"/*.tf 2>/dev/null

echo ""
echo "=== OUTPUTS ==="
grep -nE "^output\\s+\"" "$DIR"/*.tf 2>/dev/null

echo ""
echo "=== MODULE CALLS ==="
grep -nE "^module\\s+\"" "$DIR"/*.tf 2>/dev/null

echo ""
echo "=== LIFECYCLE BLOCKS ==="
grep -nE "^\\s*lifecycle\\s*\\{" "$DIR"/*.tf 2>/dev/null

echo ""
echo "=== SENSITIVE MARKERS ==="
grep -nE "sensitive\\s*=\\s*true" "$DIR"/*.tf 2>/dev/null

echo ""
echo "=== VALIDATION BLOCKS ==="
grep -nE "^\\s*validation\\s*\\{" "$DIR"/*.tf 2>/dev/null

# hcl2json upgrade path — if available, emit richer JSON to stderr
if command -v hcl2json >/dev/null 2>&1; then
  echo "" >&2
  echo "=== hcl2json structured output ===" >&2
  for f in "$DIR"/*.tf; do
    [ -f "$f" ] && hcl2json "$f" 2>/dev/null >&2 && echo "---" >&2
  done
fi
