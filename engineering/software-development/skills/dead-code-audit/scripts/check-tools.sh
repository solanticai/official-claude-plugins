#!/usr/bin/env bash
# check-tools.sh — Check which dead-code detection tools are installed for the detected stack.
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
  local lang="$1" tool="$2" probe="$3" install="$4"
  if eval "$probe" >/dev/null 2>&1; then
    echo "  [OK]      $lang :: $tool"
    OK=$((OK + 1))
  else
    echo "  [MISSING] $lang :: $tool   -- install: $install"
    MISSING=$((MISSING + 1))
  fi
}

echo "=== Tool Availability ==="
echo ""

# JS / TS
if [ -f "package.json" ]; then
  check "JS/TS" "knip" "command -v knip || npx --no-install knip --version" \
        "npm install -D knip"
  check "JS/TS" "depcheck (fallback)" "command -v depcheck || npx --no-install depcheck --version" \
        "npm install -D depcheck"
fi

# Python
if [ -f "pyproject.toml" ] || [ -f "setup.py" ] || ls requirements*.txt >/dev/null 2>&1; then
  check "Python" "vulture" "command -v vulture" \
        "pip install vulture"
  check "Python" "ruff" "command -v ruff" \
        "pip install ruff"
fi

# Go
if [ -f "go.mod" ]; then
  check "Go" "deadcode" "command -v deadcode" \
        "go install golang.org/x/tools/cmd/deadcode@latest"
  check "Go" "staticcheck" "command -v staticcheck" \
        "go install honnef.co/go/tools/cmd/staticcheck@latest"
fi

# Rust
if [ -f "Cargo.toml" ]; then
  check "Rust" "cargo-machete" "command -v cargo-machete" \
        "cargo install cargo-machete"
  check "Rust" "cargo-udeps (optional)" "command -v cargo-udeps" \
        "cargo install cargo-udeps --locked  (requires nightly)"
fi

# Java / Kotlin
if [ -f "pom.xml" ] || [ -f "build.gradle" ] || [ -f "build.gradle.kts" ]; then
  check "Java" "qodana CLI" "command -v qodana" \
        "https://www.jetbrains.com/help/qodana/install-qodana.html"
fi

# PHP
if [ -f "composer.json" ]; then
  check "PHP" "phpstan" "command -v phpstan || [ -f vendor/bin/phpstan ]" \
        "composer require --dev phpstan/phpstan"
  check "PHP" "shipmonk/dead-code-detector" "[ -d vendor/shipmonk/dead-code-detector ]" \
        "composer require --dev shipmonk/dead-code-detector"
fi

# Ruby
if [ -f "Gemfile" ]; then
  check "Ruby" "debride" "command -v debride" \
        "gem install debride"
  check "Ruby" "rubocop" "command -v rubocop" \
        "gem install rubocop"
fi

# C#
if ls *.csproj *.sln >/dev/null 2>&1; then
  check "C#" "dotnet (built-in analyzers)" "command -v dotnet" \
        "https://dotnet.microsoft.com/download"
fi

# Universal helpers
echo ""
echo "=== Universal Helpers ==="
check "shared" "git (for blame and history)" "command -v git" "https://git-scm.com/downloads"
check "shared" "jq (for JSON parsing)" "command -v jq" "https://stedolan.github.io/jq/download/"

echo ""
echo "=== Summary ==="
echo "  Available: $OK"
echo "  Missing:   $MISSING"
echo ""
if [ "$MISSING" -gt 0 ]; then
  echo "Note: missing tools will cause their phases to be skipped."
  echo "      The audit will continue with whichever tools are available."
fi

exit 0
