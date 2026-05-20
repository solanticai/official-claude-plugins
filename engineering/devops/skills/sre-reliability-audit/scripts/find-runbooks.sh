#!/usr/bin/env bash
# Anthril — SRE Reliability: Runbook Finder
# Prints one line per detected runbook with a freshness hint.

set -euo pipefail

# Runbook directories
find . -maxdepth 5 -type d \( -iname "runbook*" -o -iname "runbooks" \) 2>/dev/null | head -10 | while read -r d; do
  echo "runbook-dir:$d"
done

find . -maxdepth 5 -type d -path "*docs/runbooks*" 2>/dev/null | head -5 | while read -r d; do
  echo "runbook-dir:$d"
done

# Individual runbook files
find . -maxdepth 5 -type f -iname "RUNBOOK*.md" 2>/dev/null | head -20 | while read -r f; do
  # Freshness: last-modified epoch vs 90 days ago
  if [ -f "$f" ]; then
    age_days=$(( ( $(date +%s) - $(stat -c %Y "$f" 2>/dev/null || stat -f %m "$f" 2>/dev/null || echo 0) ) / 86400 ))
    echo "runbook:$f:age_days=$age_days"
  fi
done

# Runbooks inside a runbook directory
for dir in $(find . -maxdepth 5 -type d \( -iname "runbook*" -o -iname "runbooks" -o -path "*docs/runbooks*" \) 2>/dev/null | head -20); do
  find "$dir" -maxdepth 3 -type f \( -name "*.md" -o -name "*.mdx" \) 2>/dev/null | while read -r f; do
    age_days=$(( ( $(date +%s) - $(stat -c %Y "$f" 2>/dev/null || stat -f %m "$f" 2>/dev/null || echo 0) ) / 86400 ))
    echo "runbook:$f:age_days=$age_days"
  done
done

exit 0
