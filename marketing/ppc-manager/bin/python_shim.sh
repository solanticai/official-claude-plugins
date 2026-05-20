#!/usr/bin/env bash
# Resolve the Python interpreter written by ensure-venv.sh and exec it.
# Used by .mcp.json so MCP server entries don't need OS-specific paths.

DATA_DIR="${CLAUDE_PLUGIN_DATA:-$HOME/.claude/plugins/data/ppc-manager}"
PY_PATH_FILE="$DATA_DIR/python_path.txt"

if [ ! -f "$PY_PATH_FILE" ]; then
  echo "ppc-manager: python_path.txt not found; did ensure-venv run?" >&2
  exit 127
fi

PY=$(cat "$PY_PATH_FILE")
if [ ! -x "$PY" ] && [ ! -f "$PY" ]; then
  echo "ppc-manager: interpreter at $PY is missing" >&2
  exit 127
fi

exec "$PY" "$@"
