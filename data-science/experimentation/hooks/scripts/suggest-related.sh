#!/usr/bin/env bash
set -e
TRANSCRIPT="${CLAUDE_TRANSCRIPT:-}"
[ -z "$TRANSCRIPT" ] || [ ! -f "$TRANSCRIPT" ] && exit 0

DETECTED=""
for skill in ab-test-designer experiment-readout-builder forecasting-model-spec causal-impact-analyser; do
  if tail -200 "$TRANSCRIPT" 2>/dev/null | grep -q "experimentation:$skill"; then
    DETECTED="$skill"
  fi
done
[ -z "$DETECTED" ] && exit 0

case "$DETECTED" in
  ab-test-designer)
    NEXT='Related skill: /experimentation:experiment-readout-builder once your results are in.' ;;
  experiment-readout-builder)
    NEXT='Related skill: /experimentation:ab-test-designer for follow-up experiments suggested by the readout.' ;;
  forecasting-model-spec)
    NEXT='Related skill: /experimentation:causal-impact-analyser if you need to measure the effect of an intervention on the forecast baseline.' ;;
  causal-impact-analyser)
    NEXT='Related skill: /experimentation:experiment-readout-builder if you can convert to a randomised test; quasi-experiments are a fallback.' ;;
esac

echo "{\"systemMessage\":\"$NEXT\"}"
exit 0
