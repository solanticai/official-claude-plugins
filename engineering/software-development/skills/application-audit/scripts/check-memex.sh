#!/usr/bin/env bash
# check-memex.sh — Detect whether the project has access to a memex wiki and how.
# Usage: bash scripts/check-memex.sh <project-root>
# Output: a single line `MEMEX_MODE=plugin|wiki|none` plus diagnostic lines.
# Exit 0 always.

set -euo pipefail

PROJECT_ROOT="${1:-.}"

if [ ! -d "$PROJECT_ROOT" ]; then
  echo "MEMEX_MODE=none"
  echo "Reason: target dir not found"
  exit 0
fi

cd "$PROJECT_ROOT" || exit 0

# 1) Is the claude-memex plugin available? We can't introspect Claude's plugin
#    state from a shell script, so we proxy via two signals:
#    - the project has a `memex.config.json` file (per the plugin's convention)
#    - the project has a `CLAUDE.md` referencing claude-memex / memex plugin
PLUGIN_HINT="false"
if [ -f "memex.config.json" ]; then
  PLUGIN_HINT="true"
fi

if [ -f "CLAUDE.md" ] && grep -qi "claude-memex\|memex plugin" CLAUDE.md 2>/dev/null; then
  PLUGIN_HINT="true"
fi

# 2) Is there a usable wiki on disk?
WIKI_HINT="false"
WIKI_INDEX=""
if [ -d ".memex" ]; then
  if [ -f ".memex/index.md" ]; then
    WIKI_HINT="true"
    WIKI_INDEX=".memex/index.md"
  elif [ -f ".memex/README.md" ]; then
    WIKI_HINT="true"
    WIKI_INDEX=".memex/README.md"
  fi
fi

# 3) Decide the mode. Plugin trumps wiki because the plugin's skill (memex:doc-query)
#    is more capable than reading raw markdown.
MODE="none"
if [ "$PLUGIN_HINT" = "true" ]; then
  MODE="plugin"
elif [ "$WIKI_HINT" = "true" ]; then
  MODE="wiki"
fi

echo "MEMEX_MODE=$MODE"
echo "Plugin hint: $PLUGIN_HINT"
echo "Wiki hint:   $WIKI_HINT"
[ -n "$WIKI_INDEX" ] && echo "Wiki index:  $WIKI_INDEX"

exit 0
