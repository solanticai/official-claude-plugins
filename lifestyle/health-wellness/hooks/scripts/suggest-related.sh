#!/usr/bin/env bash
# health-wellness Stop hook — suggests related skills. Non-blocking.

set -e

TRANSCRIPT="${CLAUDE_TRANSCRIPT:-}"
if [ -z "$TRANSCRIPT" ] || [ ! -f "$TRANSCRIPT" ]; then
  exit 0
fi

DETECTED=""
for skill in \
  week-of-meals \
  move-more-plan \
  sleep-tune-up \
  smart-supplement-stack \
  daily-wellness-stack
do
  if tail -200 "$TRANSCRIPT" 2>/dev/null | grep -q "health-wellness:$skill"; then
    DETECTED="$skill"
  fi
done

if [ -z "$DETECTED" ]; then
  exit 0
fi

case "$DETECTED" in
  week-of-meals)
    NEXT='Related skills: /health-wellness:smart-supplement-stack to round out micronutrients, and /health-wellness:move-more-plan to align meals to training days.' ;;
  move-more-plan)
    NEXT='Related skills: /health-wellness:week-of-meals to fuel the program, and /health-wellness:sleep-tune-up to support recovery.' ;;
  sleep-tune-up)
    NEXT='Related skills: /health-wellness:daily-wellness-stack to anchor sleep-supportive habits, and /personal-productivity:energy-detective to validate the gains.' ;;
  smart-supplement-stack)
    NEXT='Related skill: /health-wellness:week-of-meals — food first, supplements fill gaps.' ;;
  daily-wellness-stack)
    NEXT='Related skill: /personal-productivity:habit-stacker to anchor this stack to your existing routines.' ;;
  *)
    exit 0 ;;
esac

echo "{\"systemMessage\":\"$NEXT\"}"
exit 0
