#!/usr/bin/env bash
# check-prerequisites.sh — List which CLI tools and read-only environment bits the audit can use.
# Usage: bash scripts/check-prerequisites.sh <project-root>
# Output: short text block to stdout. Exit 0 always.

set -euo pipefail

PROJECT_ROOT="${1:-.}"

if [ ! -d "$PROJECT_ROOT" ]; then
  echo "ERROR: target is not a directory: $PROJECT_ROOT" >&2
  exit 0
fi

cd "$PROJECT_ROOT" || exit 0

check_cmd() {
  local cmd="$1"
  if command -v "$cmd" >/dev/null 2>&1; then
    local v
    v=$("$cmd" --version 2>/dev/null | head -1 || echo "version unknown")
    echo "  ✓ $cmd — $v"
  else
    echo "  ✗ $cmd — not found"
  fi
}

echo "Tools:"
check_cmd node
check_cmd python3
check_cmd jq
check_cmd rg
check_cmd gh
check_cmd git
check_cmd npx

echo ""
echo "Project signals:"
[ -f "package.json" ] && echo "  ✓ package.json" || echo "  ✗ package.json (skill targets JS/TS apps)"
[ -d "supabase" ] && echo "  ✓ supabase/ directory" || echo "  - supabase/ directory (not present)"
[ -d ".git" ] && echo "  ✓ .git" || echo "  - .git (not a git repo)"
[ -d ".anthril" ] && echo "  ✓ .anthril/ exists" || echo "  - .anthril/ will be created on first run"
[ -f ".anthril/preset-profile.md" ] && echo "  ✓ .anthril/preset-profile.md (will be checked for freshness)" || echo "  - .anthril/preset-profile.md (will be created on first run)"

echo ""
echo "MCPs (auditors discover connected MCPs at runtime via the Agent tool — this script just hints what they should look for):"
echo "  ? Supabase MCP — postgres-auditor, security-auditor, backend-auditor, connection-limit-auditor"
echo "  ? Vercel MCP — frontend-auditor, server-client-auditor, bug-finder"
echo "  ? Sentry MCP — bug-finder, leak-detection-auditor"
echo "  ? GitHub MCP — security-auditor, leak-detection-auditor, backend-auditor"
echo "  ? Figma MCP — frontend-auditor"

exit 0
