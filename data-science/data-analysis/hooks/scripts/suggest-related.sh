#!/usr/bin/env bash
# Anthril — Data Analysis Plugin: Suggest Related Skills

# Try to detect which skill was used from the transcript
TRANSCRIPT="${CLAUDE_TRANSCRIPT:-}"
DETECTED_SKILL=""

for skill in anomaly-detection-rule-builder cohort-analysis-builder data-dictionary-generator data-pipeline-architecture dataset-profiling-quality-audit; do
  if echo "$TRANSCRIPT" | grep -qi "$skill" 2>/dev/null; then
    DETECTED_SKILL="$skill"
    break
  fi
done

# Define relationships
case "$DETECTED_SKILL" in
  anomaly-detection-rule-builder)
    RELATED="cohort-analysis-builder, data-pipeline-architecture"
    ;;
  cohort-analysis-builder)
    RELATED="anomaly-detection-rule-builder, dataset-profiling-quality-audit"
    ;;
  data-dictionary-generator)
    RELATED="dataset-profiling-quality-audit, data-pipeline-architecture"
    ;;
  data-pipeline-architecture)
    RELATED="data-dictionary-generator, anomaly-detection-rule-builder"
    ;;
  dataset-profiling-quality-audit)
    RELATED="data-dictionary-generator, cohort-analysis-builder"
    ;;
  *)
    exit 0
    ;;
esac

if [ -n "$RELATED" ]; then
  MESSAGE="Related Data Analysis skills you might find useful: ${RELATED}"
  echo "{\"systemMessage\": \"${MESSAGE}\"}"
fi
