#!/usr/bin/env bash
# home-life-logistics Stop hook — suggests related skills. Non-blocking.

set -e

TRANSCRIPT="${CLAUDE_TRANSCRIPT:-}"
if [ -z "$TRANSCRIPT" ] || [ ! -f "$TRANSCRIPT" ]; then
  exit 0
fi

DETECTED=""
for skill in \
  trip-day-by-day \
  home-tlc-calendar \
  adulting-checklist \
  thoughtful-gifts-plan
do
  if tail -200 "$TRANSCRIPT" 2>/dev/null | grep -q "home-life-logistics:$skill"; then
    DETECTED="$skill"
  fi
done

[ -z "$DETECTED" ] && exit 0

case "$DETECTED" in
  trip-day-by-day)
    NEXT='Related skill: /home-life-logistics:adulting-checklist to clear pre-travel life-admin (passports, insurance, mail hold).' ;;
  home-tlc-calendar)
    NEXT='Related skill: /home-life-logistics:adulting-checklist to fold maintenance into your quarterly sweep.' ;;
  adulting-checklist)
    NEXT='Related skill: /personal-finance:rainy-day-plan to fold insurance + buffer checks into the same quarterly cadence.' ;;
  thoughtful-gifts-plan)
    NEXT='Related skill: /personal-finance:money-map — make sure your gift envelope is in a sinking fund.' ;;
  *)
    exit 0 ;;
esac

echo "{\"systemMessage\":\"$NEXT\"}"
exit 0
