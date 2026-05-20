#!/usr/bin/env bash
# Anthril — Knowledge Engineering Plugin: Suggest Related Skills

TRANSCRIPT="${CLAUDE_TRANSCRIPT:-}"
DETECTED_SKILL=""

for skill in entity-disambiguation entity-relationship-mapper knowledge-graph-builder business-data-model-designer; do
  if echo "$TRANSCRIPT" | grep -qi "$skill" 2>/dev/null; then
    DETECTED_SKILL="$skill"
    break
  fi
done

case "$DETECTED_SKILL" in
  entity-disambiguation)
    RELATED="entity-relationship-mapper, knowledge-graph-builder"
    ;;
  entity-relationship-mapper)
    RELATED="entity-disambiguation, business-data-model-designer"
    ;;
  knowledge-graph-builder)
    RELATED="entity-relationship-mapper, business-data-model-designer"
    ;;
  business-data-model-designer)
    RELATED="knowledge-graph-builder, entity-relationship-mapper"
    ;;
  *)
    exit 0
    ;;
esac

if [ -n "$RELATED" ]; then
  MESSAGE="Related Knowledge Engineering skills you might find useful: ${RELATED}"
  echo "{\"systemMessage\": \"${MESSAGE}\"}"
fi
