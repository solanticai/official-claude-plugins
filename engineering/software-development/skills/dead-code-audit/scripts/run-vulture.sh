#!/usr/bin/env bash
# run-vulture.sh — Wrapper for vulture with sensible defaults for the dead-code-audit skill.
# Usage: bash scripts/run-vulture.sh <project-root> [min-confidence]
# Output: Vulture text findings to stdout. Always exits 0.

set -euo pipefail

PROJECT_ROOT="${1:-.}"
MIN_CONF="${2:-60}"

if [ ! -d "$PROJECT_ROOT" ]; then
  echo "ERROR: target is not a directory: $PROJECT_ROOT" >&2
  exit 1
fi

cd "$PROJECT_ROOT"

# Check this looks like a Python project
if [ ! -f "pyproject.toml" ] && [ ! -f "setup.py" ] && ! ls requirements*.txt >/dev/null 2>&1; then
  echo "# no python project detected (no pyproject.toml, setup.py, or requirements*.txt)"
  exit 0
fi

if ! command -v vulture >/dev/null 2>&1; then
  echo "# vulture not installed -- install: pip install vulture"
  exit 0
fi

# Build exclude list
EXCLUDE_PATHS=".venv,venv,node_modules,build,dist,.git,__pycache__,migrations,*.egg-info"

# Vulture exits non-zero when findings exist; treat that as a normal scan result.
OUTPUT=$(vulture . \
  --min-confidence "$MIN_CONF" \
  --exclude "$EXCLUDE_PATHS" \
  2>&1) || true

if [ -z "$OUTPUT" ]; then
  echo "# no findings at confidence >= ${MIN_CONF}%"
else
  echo "$OUTPUT"
fi

exit 0
