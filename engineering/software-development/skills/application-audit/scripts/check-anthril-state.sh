#!/usr/bin/env bash
# check-anthril-state.sh — Report the current .anthril/ state so the SKILL.md User Context block can summarise it.
# Usage: bash scripts/check-anthril-state.sh <project-root>
# Output: short text block to stdout. Exit 0 always.

set -euo pipefail

PROJECT_ROOT="${1:-.}"

if [ ! -d "$PROJECT_ROOT" ]; then
  echo "ERROR: target is not a directory: $PROJECT_ROOT" >&2
  exit 0
fi

cd "$PROJECT_ROOT" || exit 0

if [ ! -d ".anthril" ]; then
  echo "Status:           first run (.anthril/ does not exist)"
  echo "Profile:          will be created"
  echo "Audits:           none"
  echo "Open questions:   none"
  exit 0
fi

PROFILE_STATUS="absent"
PROFILE_AGE=""
if [ -f ".anthril/preset-profile.md" ]; then
  PROFILE_STATUS="present"
  if [ -n "$(command -v stat)" ]; then
    # GNU stat / BSD stat differ; try GNU first.
    PROFILE_AGE=$(stat -c '%y' ".anthril/preset-profile.md" 2>/dev/null || stat -f '%Sm' ".anthril/preset-profile.md" 2>/dev/null || echo "")
  fi
fi

AUDIT_COUNT=0
LATEST_AUDIT=""
if [ -d ".anthril/audits" ]; then
  AUDIT_COUNT=$(find ".anthril/audits" -mindepth 1 -maxdepth 1 -type d ! -name "latest" 2>/dev/null | wc -l | tr -d ' ')
  LATEST_AUDIT=$(find ".anthril/audits" -mindepth 1 -maxdepth 1 -type d ! -name "latest" 2>/dev/null | sort -r | head -1 | xargs -I {} basename {} 2>/dev/null || echo "")
fi

OPEN_Q_COUNT=0
if [ -d ".anthril/questions" ]; then
  OPEN_Q_COUNT=$(find ".anthril/questions" -maxdepth 1 -type f -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
fi

echo "Status:           subsequent run"
echo "Profile:          $PROFILE_STATUS${PROFILE_AGE:+ (modified $PROFILE_AGE)}"
echo "Audits to date:   $AUDIT_COUNT${LATEST_AUDIT:+ (latest: $LATEST_AUDIT)}"
echo "Open questions:   $OPEN_Q_COUNT"

if [ "$OPEN_Q_COUNT" -gt 0 ]; then
  echo ""
  echo "  ⚠ Open questions exist from a previous run. Review .anthril/questions/ before re-running,"
  echo "    or run /audit-proceed all to resume the prior audit."
fi

exit 0
