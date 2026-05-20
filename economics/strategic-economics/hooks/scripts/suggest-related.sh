#!/usr/bin/env bash
set -e
TRANSCRIPT="${CLAUDE_TRANSCRIPT:-}"
[ -z "$TRANSCRIPT" ] || [ ! -f "$TRANSCRIPT" ] && exit 0

DETECTED=""
for skill in competitive-dynamics-analyser elasticity-estimator moat-strength-audit; do
  if tail -200 "$TRANSCRIPT" 2>/dev/null | grep -q "strategic-economics:$skill"; then
    DETECTED="$skill"
  fi
done
[ -z "$DETECTED" ] && exit 0

case "$DETECTED" in
  competitive-dynamics-analyser) NEXT='Related skill: /strategic-economics:moat-strength-audit to score whether your position is defensible against the dynamics you mapped.' ;;
  elasticity-estimator) NEXT='Related skill: /business-economics:pricing-architecture-designer to apply elasticity findings to pricing.' ;;
  moat-strength-audit) NEXT='Related skill: /strategic-economics:competitive-dynamics-analyser to map the forces threatening the weakest moat.' ;;
esac

echo "{\"systemMessage\":\"$NEXT\"}"
exit 0
