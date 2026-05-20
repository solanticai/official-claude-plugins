#!/usr/bin/env bash
# Anthril — Resource Manager Plugin: orphan MCP killer (Stop hook).
# Delegates to the cross-platform Python implementation.
PY=$(command -v python || command -v python3 || true)
if [ -z "$PY" ]; then
  # Python unavailable: exit 0 so the hook never blocks the turn.
  exit 0
fi
exec "$PY" "${CLAUDE_PLUGIN_ROOT}/hooks/scripts/kill-orphan-mcp.py" "$@"
