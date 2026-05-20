#!/usr/bin/env bash
# Anthril — DevOps Plugin: Suggest Related Skills

TRANSCRIPT="${CLAUDE_TRANSCRIPT:-}"
DETECTED_SKILL=""

for skill in devops-needs-assessment cicd-pipeline-audit iac-terraform-audit container-audit kubernetes-manifest-audit observability-audit release-readiness-audit devsecops-supply-chain-audit sre-reliability-audit; do
  if echo "$TRANSCRIPT" | grep -qi "$skill" 2>/dev/null; then
    DETECTED_SKILL="$skill"
    break
  fi
done

case "$DETECTED_SKILL" in
  devops-needs-assessment)
    RELATED="cicd-pipeline-audit, observability-audit"
    ;;
  cicd-pipeline-audit)
    RELATED="devsecops-supply-chain-audit, container-audit"
    ;;
  iac-terraform-audit)
    RELATED="container-audit, kubernetes-manifest-audit"
    ;;
  container-audit)
    RELATED="kubernetes-manifest-audit, devsecops-supply-chain-audit"
    ;;
  kubernetes-manifest-audit)
    RELATED="observability-audit, sre-reliability-audit"
    ;;
  observability-audit)
    RELATED="sre-reliability-audit, release-readiness-audit"
    ;;
  release-readiness-audit)
    RELATED="sre-reliability-audit, observability-audit"
    ;;
  devsecops-supply-chain-audit)
    RELATED="cicd-pipeline-audit, container-audit"
    ;;
  sre-reliability-audit)
    RELATED="observability-audit, release-readiness-audit"
    ;;
  *)
    exit 0
    ;;
esac

if [ -n "$RELATED" ]; then
  MESSAGE="Related DevOps skills you might find useful: ${RELATED}"
  echo "{\"systemMessage\": \"${MESSAGE}\"}"
fi
