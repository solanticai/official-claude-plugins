#!/usr/bin/env bash
# list-pending-agents.sh — List which auditors have not yet produced a report
# for the given audit ID. Used by /audit-proceed to figure out who to re-dispatch
# (or by Phase 5 to confirm coverage before validation).
#
# Usage: bash scripts/list-pending-agents.sh <project-root> <audit-id>
# Output: JSON to stdout:
#   { "audit_id": "...", "expected": [...], "found": [...], "missing": [...] }
# Exit 0 always.

set -euo pipefail

PROJECT_ROOT="${1:-.}"
AUDIT_ID="${2:-}"

if [ ! -d "$PROJECT_ROOT" ] || [ -z "$AUDIT_ID" ]; then
  echo '{"audit_id":null,"expected":[],"found":[],"missing":[],"error":"missing args"}' >&2
  exit 0
fi

REPORTS_DIR="$PROJECT_ROOT/.anthril/audits/$AUDIT_ID/agent-reports"

EXPECTED=(
  "frontend-auditor"
  "backend-auditor"
  "bug-finder"
  "cross-cutting-security-auditor"
  "client-connection-auditor"
  "server-client-auditor"
  "postgres-auditor"
  "leak-detection-auditor"
  "connection-limit-auditor"
)

python3 - "$REPORTS_DIR" "$AUDIT_ID" "${EXPECTED[@]}" <<'PY'
import json, os, sys
reports_dir = sys.argv[1]
audit_id = sys.argv[2]
expected = sys.argv[3:]

found = []
missing = []
for name in expected:
    path = os.path.join(reports_dir, f"{name}.md")
    if os.path.isfile(path) and os.path.getsize(path) > 0:
        found.append(name)
    else:
        missing.append(name)

json.dump({
    "audit_id": audit_id,
    "expected": expected,
    "found": found,
    "missing": missing,
}, sys.stdout, ensure_ascii=False, indent=2)
sys.stdout.write("\n")
PY

exit 0
