#!/usr/bin/env bash
# stop-hook.sh — Advisory hook that runs when the assistant stops.
#
# Detects orphaned orchestrator state (a marker file written when the skill
# starts but never cleaned up). If any orphan is found, prints a warning to
# stderr so the user knows their last orchestrator run did not finalise. The
# hook never blocks the conversation — it always exits 0.
#
# Marker convention used by SKILL.md:
#   /tmp/plan-orchestrator-<session>.json         — written on Phase 1 entry
#   /tmp/plan-orchestrator-<session>.complete     — written on Phase 5 success
#
# A marker without a matching .complete is treated as orphaned and surfaced.
# Markers older than 6 hours are auto-pruned.

set -euo pipefail

MARKERS_GLOB="/tmp/plan-orchestrator-*.json"
PRUNE_HOURS=6
NOW_EPOCH=$(date +%s)

# If no markers, nothing to do.
shopt -s nullglob
markers=( $MARKERS_GLOB )
shopt -u nullglob

if [ ${#markers[@]} -eq 0 ]; then
  exit 0
fi

ORPHANED=()
for marker in "${markers[@]}"; do
  # Auto-prune anything older than PRUNE_HOURS.
  if [ -f "$marker" ]; then
    mtime=$(stat -c %Y "$marker" 2>/dev/null || stat -f %m "$marker" 2>/dev/null || echo "$NOW_EPOCH")
    age_hours=$(( (NOW_EPOCH - mtime) / 3600 ))
    if [ "$age_hours" -ge "$PRUNE_HOURS" ]; then
      rm -f "$marker" "${marker%.json}.complete" 2>/dev/null
      continue
    fi
  fi

  # Anything still here is recent. Treat as orphan if .complete is missing.
  if [ ! -f "${marker%.json}.complete" ]; then
    ORPHANED+=("$marker")
  fi
done

if [ ${#ORPHANED[@]} -gt 0 ]; then
  {
    echo "[plan-orchestrator] Detected ${#ORPHANED[@]} orphaned run(s):"
    for m in "${ORPHANED[@]}"; do
      echo "  - $m"
    done
    echo "[plan-orchestrator] These runs started but never wrote a .complete flag."
    echo "[plan-orchestrator] If you cancelled a previous orchestration, this is expected."
    echo "[plan-orchestrator] Markers auto-prune after ${PRUNE_HOURS}h."
  } >&2
fi

exit 0
