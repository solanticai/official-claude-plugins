#!/usr/bin/env bash
# Anthril — SRE Reliability: SLO File Finder

set -euo pipefail

find . -maxdepth 5 -type f \( \
  -iname "slo*.yaml" \
  -o -iname "slo*.yml" \
  -o -iname "slis*.yaml" \
  -o -iname "slis*.yml" \
  -o -iname "error-budget*.md" \
  -o -name "*.slo.yaml" \
  -o -name "*.slo.yml" \
\) 2>/dev/null | head -30 | while read -r f; do
  # Try to detect OpenSLO-compatible files
  if grep -q "^kind:\\s*SLO" "$f" 2>/dev/null; then
    echo "openslo:$f"
  elif grep -qE "(objective|error_budget|burn_rate)" "$f" 2>/dev/null; then
    echo "slo-candidate:$f"
  else
    echo "slo-file:$f"
  fi
done

# SLO references in Markdown docs (for teams that document SLOs in prose)
grep -rlE "Service Level Objective|SLO\\s*:\\s*[0-9]+%?|error budget|burn rate" \
  --include="*.md" \
  --exclude-dir=node_modules --exclude-dir=.git \
  . 2>/dev/null | head -20 | while read -r f; do
    echo "slo-doc:$f"
  done

exit 0
