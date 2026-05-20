#!/usr/bin/env bash
# check-tools.sh — Check which write-path-mapping tools are installed.
# Usage: bash scripts/check-tools.sh <project-root>
# Output: Plain-text checklist with install commands for missing tools. Always exits 0.

set -euo pipefail

PROJECT_ROOT="${1:-.}"

if [ ! -d "$PROJECT_ROOT" ]; then
  echo "ERROR: target is not a directory: $PROJECT_ROOT" >&2
  exit 1
fi

cd "$PROJECT_ROOT"

OK=0
MISSING=0

check() {
  local group="$1" tool="$2" probe="$3" install="$4"
  if eval "$probe" >/dev/null 2>&1; then
    echo "  [OK]      $group :: $tool"
    OK=$((OK + 1))
  else
    echo "  [MISSING] $group :: $tool   -- install: $install"
    MISSING=$((MISSING + 1))
  fi
}

echo "=== Tool Availability ==="
echo ""

# --- Core scanning helpers (bash-only mode still works without these) -----------------
check "core"    "ripgrep (rg)"       "command -v rg"       "https://github.com/BurntSushi/ripgrep#installation"
check "core"    "git"                "command -v git"      "https://git-scm.com/downloads"
check "core"    "jq (optional)"      "command -v jq"       "https://stedolan.github.io/jq/download/"
check "core"    "python3"            "command -v python3 || command -v python" "https://www.python.org/downloads/"

# --- Node / JS tooling ----------------------------------------------------------------
if [ -f "package.json" ]; then
  check "js/ts" "node"               "command -v node"     "https://nodejs.org/"
  check "js/ts" "npx"                "command -v npx"      "bundled with Node.js"
  check "js/ts" "ast-grep (sg)"      "command -v sg || command -v ast-grep" \
        "npm i -g @ast-grep/cli  or  cargo install ast-grep"
fi

# --- Python tooling -------------------------------------------------------------------
if [ -f "pyproject.toml" ] || [ -f "setup.py" ] || ls requirements*.txt >/dev/null 2>&1; then
  check "python" "ruff (optional)"   "command -v ruff"     "pip install ruff"
fi

# --- Supabase tooling -----------------------------------------------------------------
if [ -d "supabase" ] || grep -q '"@supabase/' package.json 2>/dev/null; then
  check "supabase" "supabase CLI (optional)" "command -v supabase" \
        "https://supabase.com/docs/guides/cli"
fi

# --- Live DB probe helpers (optional) -------------------------------------------------
check "live-db" "psql (optional)"    "command -v psql"     "https://www.postgresql.org/download/"

# --- Diagram rendering (optional for local preview) -----------------------------------
check "render"  "mmdc (mermaid-cli, optional)" "command -v mmdc" \
      "npm i -g @mermaid-js/mermaid-cli"

echo ""
echo "=== Summary ==="
echo "  Available: $OK"
echo "  Missing:   $MISSING"
echo ""
if [ "$MISSING" -gt 0 ]; then
  echo "Note: missing tools degrade but never abort the mapping."
  echo "      ripgrep is the only strongly recommended tool — everything else is optional."
fi

exit 0
