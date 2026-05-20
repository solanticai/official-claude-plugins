#!/usr/bin/env bash
# Anthril — SRE Reliability: Postmortem Finder
# Lists postmortem files with age and a rough template-compliance hint.

set -euo pipefail

# Postmortem directories
for dir in $(find . -maxdepth 5 -type d \( -iname "postmortem*" -o -iname "incidents" -o -iname "incident-reports" \) 2>/dev/null); do
  echo "pm-dir:$dir"
done

# Individual postmortem files
find . -maxdepth 6 -type f \( -iname "postmortem*.md" -o -iname "incident-*.md" -o -path "*postmortems/*.md" -o -path "*incidents/*.md" \) 2>/dev/null | head -40 | while read -r f; do
  if [ -f "$f" ]; then
    age_days=$(( ( $(date +%s) - $(stat -c %Y "$f" 2>/dev/null || stat -f %m "$f" 2>/dev/null || echo 0) ) / 86400 ))
    # Rough template compliance: look for key sections
    has_impact=$(grep -qE "^##?\\s*Impact" "$f" 2>/dev/null && echo y || echo n)
    has_timeline=$(grep -qE "^##?\\s*Timeline" "$f" 2>/dev/null && echo y || echo n)
    has_action_items=$(grep -qE "^##?\\s*Action items" "$f" 2>/dev/null && echo y || echo n)
    has_blameless_marker=$(grep -qiE "(blameless|no blame)" "$f" 2>/dev/null && echo y || echo n)
    echo "postmortem:$f:age_days=$age_days:impact=$has_impact:timeline=$has_timeline:actions=$has_action_items:blameless=$has_blameless_marker"
  fi
done

exit 0
