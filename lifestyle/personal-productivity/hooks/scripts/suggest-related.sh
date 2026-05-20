#!/usr/bin/env bash
# personal-productivity Stop hook — suggests related skills based on the most
# recent personal-productivity skill invoked in the current transcript. Non-blocking.

set -e

TRANSCRIPT="${CLAUDE_TRANSCRIPT:-}"
if [ -z "$TRANSCRIPT" ] || [ ! -f "$TRANSCRIPT" ]; then
  exit 0
fi

DETECTED=""
for skill in \
  habit-stacker \
  sunday-reset \
  deep-focus-day \
  energy-detective
do
  if tail -200 "$TRANSCRIPT" 2>/dev/null | grep -q "personal-productivity:$skill"; then
    DETECTED="$skill"
  fi
done

if [ -z "$DETECTED" ]; then
  exit 0
fi

case "$DETECTED" in
  habit-stacker)
    NEXT='Related skills: /personal-productivity:sunday-reset to build the weekly cadence that anchors your stack, and /personal-productivity:energy-detective to validate the time slots you picked.' ;;
  sunday-reset)
    NEXT='Related skill: /personal-productivity:deep-focus-day to translate your weekly priorities into protected blocks.' ;;
  deep-focus-day)
    NEXT='Related skills: /personal-productivity:energy-detective to confirm your peak hours, and /personal-productivity:habit-stacker to make the focus routine stick.' ;;
  energy-detective)
    NEXT='Related skill: /personal-productivity:deep-focus-day to schedule your high-energy windows for the work that matters most.' ;;
  *)
    exit 0 ;;
esac

echo "{\"systemMessage\":\"$NEXT\"}"
exit 0
