#!/usr/bin/env bash
# Anthril — Business Economics Plugin: Suggest Related Skills

TRANSCRIPT="${CLAUDE_TRANSCRIPT:-}"
DETECTED_SKILL=""

for skill in unit-economics-calculator market-sizing-tam-estimator pricing-architecture-designer cost-structure-builder break-even-scenario-modeller; do
  if echo "$TRANSCRIPT" | grep -qi "$skill" 2>/dev/null; then
    DETECTED_SKILL="$skill"
    break
  fi
done

case "$DETECTED_SKILL" in
  unit-economics-calculator)
    RELATED="cost-structure-builder, break-even-scenario-modeller" ;;
  market-sizing-tam-estimator)
    RELATED="pricing-architecture-designer, unit-economics-calculator" ;;
  pricing-architecture-designer)
    RELATED="unit-economics-calculator, cost-structure-builder" ;;
  cost-structure-builder)
    RELATED="break-even-scenario-modeller, unit-economics-calculator" ;;
  break-even-scenario-modeller)
    RELATED="cost-structure-builder, pricing-architecture-designer" ;;
  *)
    exit 0 ;;
esac

if [ -n "$RELATED" ]; then
  MESSAGE="Related Business Economics skills: ${RELATED}"
  echo "{\"systemMessage\": \"${MESSAGE}\"}"
fi
