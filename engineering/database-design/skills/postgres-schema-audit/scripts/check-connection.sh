#!/usr/bin/env bash
# check-connection.sh — Detect which database connection modes are available.
# Usage: bash scripts/check-connection.sh [project-root]
# Output: Plain-text report with a machine-parseable `mode:` line. Always exits 0
#         so the skill can proceed with whatever is available.
#
# Modes:
#   supabase-mcp    — Supabase MCP connector is configured. Use MCP tools.
#   direct-postgres — One or more psql-connection profiles exist. Use run-query.sh.
#   both            — Both available. Skill should ask the user to pick.
#   none            — Neither available. Skill should prompt setup.
#
# Supabase MCP detection order (first match wins):
#   1. Project-local .mcp.json
#   2. Project-local .claude/.mcp.json
#   3. User-level ~/.claude/.mcp.json
#   4. User-level ~/.config/claude/.mcp.json
#
# Direct-postgres detection:
#   Scans $XDG_CONFIG_HOME/database-design/connections/*.env
#   (falls back to ~/.config/database-design/connections/*.env)

set -euo pipefail

PROJECT_ROOT="${1:-.}"
if [ ! -d "$PROJECT_ROOT" ]; then
  echo "ERROR: target is not a directory: $PROJECT_ROOT" >&2
  exit 1
fi
cd "$PROJECT_ROOT"

# -----------------------------------------------------------------------------
# Supabase MCP probe
# -----------------------------------------------------------------------------
MCP_FOUND_PATHS=()
MCP_MODE="none"

MCP_CANDIDATES=(
  ".mcp.json"
  ".claude/.mcp.json"
  "$HOME/.claude/.mcp.json"
  "$HOME/.config/claude/.mcp.json"
)

for cfg in "${MCP_CANDIDATES[@]}"; do
  if [ -f "$cfg" ] && grep -qi "supabase" "$cfg" 2>/dev/null; then
    MCP_FOUND_PATHS+=("$cfg")
    MCP_MODE="supabase-mcp"
  fi
done

# -----------------------------------------------------------------------------
# Direct-postgres probe
# -----------------------------------------------------------------------------
CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}"
CONN_DIR="$CONFIG_HOME/database-design/connections"
ACTIVE_FILE="$CONFIG_HOME/database-design/active-connection"

DIRECT_PROFILES=()
DIRECT_MODE="none"
ACTIVE_CONN=""

if [ -d "$CONN_DIR" ]; then
  # shellcheck disable=SC2012
  while IFS= read -r f; do
    [ -f "$f" ] || continue
    name=$(basename "$f" .env)
    DIRECT_PROFILES+=("$name")
    DIRECT_MODE="direct-postgres"
  done < <(ls -1 "$CONN_DIR"/*.env 2>/dev/null || true)
fi

# Project-local active-connection pointer takes precedence over global
if [ -f ".database-design/active-connection" ]; then
  ACTIVE_CONN=$(head -n1 ".database-design/active-connection" | tr -d '[:space:]')
elif [ -f "$ACTIVE_FILE" ]; then
  ACTIVE_CONN=$(head -n1 "$ACTIVE_FILE" | tr -d '[:space:]')
fi

# -----------------------------------------------------------------------------
# Resolve overall mode
# -----------------------------------------------------------------------------
if [ "$MCP_MODE" = "supabase-mcp" ] && [ "$DIRECT_MODE" = "direct-postgres" ]; then
  OVERALL="both"
elif [ "$MCP_MODE" = "supabase-mcp" ]; then
  OVERALL="supabase-mcp"
elif [ "$DIRECT_MODE" = "direct-postgres" ]; then
  OVERALL="direct-postgres"
else
  OVERALL="none"
fi

# -----------------------------------------------------------------------------
# Report
# -----------------------------------------------------------------------------
echo "=== Database Connection Check ==="
echo "mode: $OVERALL"
echo ""

echo "--- Supabase MCP ---"
if [ "$MCP_MODE" = "supabase-mcp" ]; then
  echo "status: configured"
  echo "found_configs:"
  for p in "${MCP_FOUND_PATHS[@]}"; do
    echo "  - $p"
  done
else
  echo "status: not_configured"
  echo "searched:"
  for cfg in "${MCP_CANDIDATES[@]}"; do
    echo "  - $cfg"
  done
fi
echo ""

echo "--- Direct Postgres ---"
if [ "$DIRECT_MODE" = "direct-postgres" ]; then
  echo "status: configured"
  echo "connections_dir: $CONN_DIR"
  echo "profiles:"
  for p in "${DIRECT_PROFILES[@]}"; do
    if [ "$p" = "$ACTIVE_CONN" ]; then
      echo "  - $p  (active)"
    else
      echo "  - $p"
    fi
  done
  if [ -z "$ACTIVE_CONN" ]; then
    echo "active: (none set — skill will ask user to pick)"
  else
    echo "active: $ACTIVE_CONN"
  fi
else
  echo "status: not_configured"
  echo "expected_dir: $CONN_DIR"
fi
echo ""

# -----------------------------------------------------------------------------
# Actionable hints for the skill
# -----------------------------------------------------------------------------
echo "--- Next steps ---"
case "$OVERALL" in
  none)
    echo "Neither connection mode is configured. The skill should offer two options:"
    echo "  1. Enable the Supabase MCP connector (if the user uses Supabase)"
    echo "  2. Run: bash \"\${CLAUDE_PLUGIN_ROOT}/skills/postgres-schema-audit/scripts/setup-postgres.sh\""
    echo "     (for any other Postgres — RDS, Neon, Railway, self-hosted, local)"
    ;;
  supabase-mcp)
    echo "Supabase MCP is available. The skill will use:"
    echo "  - mcp__*Supabase__list_projects       (pick the project)"
    echo "  - mcp__*Supabase__list_tables         (seed schema inventory)"
    echo "  - mcp__*Supabase__execute_sql         (read-only SELECTs)"
    echo "  - mcp__*Supabase__get_advisors        (security/performance hints)"
    ;;
  direct-postgres)
    echo "Direct Postgres connection is available. The skill will use:"
    echo "  - bash scripts/run-query.sh           (read-only SELECTs via psql)"
    echo "  - Active profile: ${ACTIVE_CONN:-<unset — will prompt>}"
    echo "Note: get_advisors is Supabase-only. In direct mode the skill skips that step."
    ;;
  both)
    echo "Both connection modes are available. The skill should ask the user which to use."
    echo "Supabase MCP unlocks get_advisors; direct-postgres works with any Postgres role."
    ;;
esac

exit 0
