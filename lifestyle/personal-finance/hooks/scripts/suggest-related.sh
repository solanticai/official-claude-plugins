#!/usr/bin/env bash
# personal-finance Stop hook — suggests related skills. Non-blocking.

set -e

TRANSCRIPT="${CLAUDE_TRANSCRIPT:-}"
if [ -z "$TRANSCRIPT" ] || [ ! -f "$TRANSCRIPT" ]; then
  exit 0
fi

DETECTED=""
for skill in \
  money-map \
  debt-knockout-plan \
  savings-game-plan \
  future-me-projection \
  rainy-day-plan
do
  if tail -200 "$TRANSCRIPT" 2>/dev/null | grep -q "personal-finance:$skill"; then
    DETECTED="$skill"
  fi
done

if [ -z "$DETECTED" ]; then
  exit 0
fi

case "$DETECTED" in
  money-map)
    NEXT='Related skills: /personal-finance:savings-game-plan to give the surplus a destination, and /personal-finance:debt-knockout-plan if there are debts to handle.' ;;
  debt-knockout-plan)
    NEXT='Related skill: /personal-finance:money-map — the payoff is only as good as the budget that feeds it.' ;;
  savings-game-plan)
    NEXT='Related skills: /personal-finance:future-me-projection to model what the savings rate compounds to, and /personal-finance:rainy-day-plan to size the emergency buffer.' ;;
  future-me-projection)
    NEXT='Related skill: /personal-finance:savings-game-plan to tune contribution levers; consider a licensed adviser to validate assumptions.' ;;
  rainy-day-plan)
    NEXT='Related skill: /personal-finance:money-map — the buffer needs a home in the budget.' ;;
  *)
    exit 0 ;;
esac

echo "{\"systemMessage\":\"$NEXT\"}"
exit 0
