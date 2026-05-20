#!/usr/bin/env bash
# Anthril — CI/CD Pipeline Audit: Workflow Parser
# Prints a structural summary of a workflow file for sub-agent ingestion.
# Usage: bash parse-workflow.sh <workflow-path>

set -euo pipefail

FILE="${1:-}"
if [ -z "$FILE" ] || [ ! -f "$FILE" ]; then
  echo "error: file not found" >&2
  exit 1
fi

echo "=== FILE: $FILE ==="
echo "=== SIZE: $(wc -l < "$FILE") lines ==="
echo ""
echo "=== TRIGGERS ==="
grep -nE "^on:|^  (push|pull_request|workflow_dispatch|schedule|release|workflow_run):" "$FILE" 2>/dev/null | head -30

echo ""
echo "=== PERMISSIONS ==="
grep -nE "^permissions:|^  permissions:" "$FILE" 2>/dev/null | head -20

echo ""
echo "=== JOBS ==="
grep -nE "^  [a-zA-Z_-]+:$" "$FILE" 2>/dev/null | head -30

echo ""
echo "=== RUNNERS ==="
grep -nE "runs-on:" "$FILE" 2>/dev/null

echo ""
echo "=== TIMEOUTS ==="
grep -nE "timeout-minutes:" "$FILE" 2>/dev/null

echo ""
echo "=== CONCURRENCY ==="
grep -nE "concurrency:" "$FILE" 2>/dev/null

echo ""
echo "=== ACTION REFERENCES ==="
grep -nE "uses:" "$FILE" 2>/dev/null

echo ""
echo "=== SECRET REFERENCES ==="
grep -nE "secrets\\." "$FILE" 2>/dev/null | head -40

echo ""
echo "=== ENVIRONMENT BLOCKS ==="
grep -nE "^\\s+environment:" "$FILE" 2>/dev/null

echo ""
echo "=== CACHE USAGE ==="
grep -nE "actions/cache@|cache:" "$FILE" 2>/dev/null
