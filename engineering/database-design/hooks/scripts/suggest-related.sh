#!/usr/bin/env bash
set -e
TRANSCRIPT="${CLAUDE_TRANSCRIPT:-}"
[ -z "$TRANSCRIPT" ] || [ ! -f "$TRANSCRIPT" ] && exit 0

DETECTED=""
for skill in business-data-model-designer postgres-schema-audit erd-generator rls-policy-designer migration-plan-builder index-strategy-planner supabase-schema-bootstrap; do
  if tail -200 "$TRANSCRIPT" 2>/dev/null | grep -q "database-design:$skill"; then
    DETECTED="$skill"
  fi
done
[ -z "$DETECTED" ] && exit 0

case "$DETECTED" in
  business-data-model-designer) NEXT='Related skills: /database-design:rls-policy-designer + /database-design:erd-generator to round out the design.' ;;
  postgres-schema-audit) NEXT='Related skills: /database-design:index-strategy-planner if performance findings; /database-design:migration-plan-builder if change needed.' ;;
  erd-generator) NEXT='Related skill: /database-design:business-data-model-designer if you need full SQL + RLS, not just diagrams.' ;;
  rls-policy-designer) NEXT='Related skill: /database-design:postgres-schema-audit to verify policies compose with existing schema constraints.' ;;
  migration-plan-builder) NEXT='Related skill: /database-design:postgres-schema-audit to baseline before the migration; /database-design:index-strategy-planner if indexes are part of the migration.' ;;
  index-strategy-planner) NEXT='Related skill: /database-design:postgres-schema-audit for full performance review; /database-design:migration-plan-builder if changes touch heavily-trafficked tables.' ;;
  supabase-schema-bootstrap) NEXT='Related skills: /database-design:rls-policy-designer + /database-design:erd-generator to formalise the bootstrap.' ;;
esac

echo "{\"systemMessage\":\"$NEXT\"}"
exit 0
