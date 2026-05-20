#!/usr/bin/env bash
# Anthril — Business Economics Plugin: Suggest Related Skills

TRANSCRIPT="${CLAUDE_TRANSCRIPT:-}"
DETECTED_SKILL=""

for skill in unit-economics-calculator market-sizing-tam-estimator; do
  if echo "$TRANSCRIPT" | grep -qi "$skill" 2>/dev/null; then
    DETECTED_SKILL="$skill"
    break
  fi
done

case "$DETECTED_SKILL" in
  unit-economics-calculator)
    RELATED="market-sizing-tam-estimator"
    ;;
  market-sizing-tam-estimator)
    RELATED="unit-economics-calculator"
    ;;
  *)
    exit 0
    ;;
esac

if [ -n "$RELATED" ]; then
  MESSAGE="Related Business Economics skills you might find useful: ${RELATED}"
  echo "{\"systemMessage\": \"${MESSAGE}\"}"
fi
