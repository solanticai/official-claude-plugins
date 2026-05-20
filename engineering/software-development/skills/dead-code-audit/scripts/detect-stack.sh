#!/usr/bin/env bash
# detect-stack.sh — Detect languages, frameworks, and monorepo layout in a target directory.
# Usage: bash scripts/detect-stack.sh <project-root>
# Output: JSON when `jq` is available, plain text otherwise. Exits 0 even on partial detection.

set -euo pipefail

PROJECT_ROOT="${1:-.}"

if [ ! -d "$PROJECT_ROOT" ]; then
  echo "ERROR: target is not a directory: $PROJECT_ROOT" >&2
  exit 1
fi

cd "$PROJECT_ROOT"

# --- Language detection ---------------------------------------------------------------

LANGS=()
FRAMEWORKS=()
MONOREPO=""

# JavaScript / TypeScript
if [ -f "package.json" ]; then
  LANGS+=("javascript")
  if [ -f "tsconfig.json" ] || ls **/tsconfig.json >/dev/null 2>&1; then
    LANGS+=("typescript")
  fi
  # Framework hints from package.json
  if grep -q '"next"' package.json 2>/dev/null; then FRAMEWORKS+=("nextjs"); fi
  if grep -q '"nuxt"' package.json 2>/dev/null; then FRAMEWORKS+=("nuxt"); fi
  if grep -q '"@nestjs/' package.json 2>/dev/null; then FRAMEWORKS+=("nestjs"); fi
  if grep -q '"@remix-run/' package.json 2>/dev/null; then FRAMEWORKS+=("remix"); fi
  if grep -q '"astro"' package.json 2>/dev/null; then FRAMEWORKS+=("astro"); fi
  if grep -q '"vite"' package.json 2>/dev/null; then FRAMEWORKS+=("vite"); fi
  if grep -q '"react"' package.json 2>/dev/null; then FRAMEWORKS+=("react"); fi
  if grep -q '"vue"' package.json 2>/dev/null; then FRAMEWORKS+=("vue"); fi
  if grep -q '"svelte"' package.json 2>/dev/null; then FRAMEWORKS+=("svelte"); fi
fi

# Python
if [ -f "pyproject.toml" ] || [ -f "setup.py" ] || ls requirements*.txt >/dev/null 2>&1; then
  LANGS+=("python")
  if grep -q "django" pyproject.toml requirements*.txt 2>/dev/null; then FRAMEWORKS+=("django"); fi
  if grep -q "flask" pyproject.toml requirements*.txt 2>/dev/null; then FRAMEWORKS+=("flask"); fi
  if grep -q "fastapi" pyproject.toml requirements*.txt 2>/dev/null; then FRAMEWORKS+=("fastapi"); fi
fi

# Go
if [ -f "go.mod" ]; then
  LANGS+=("go")
  if [ -f "go.work" ]; then MONOREPO="go-workspace"; fi
fi

# Rust
if [ -f "Cargo.toml" ]; then
  LANGS+=("rust")
  if grep -q '\[workspace\]' Cargo.toml 2>/dev/null; then MONOREPO="cargo-workspace"; fi
fi

# Java / Kotlin
if [ -f "pom.xml" ]; then
  LANGS+=("java")
  FRAMEWORKS+=("maven")
  if grep -q "spring" pom.xml 2>/dev/null; then FRAMEWORKS+=("spring"); fi
fi
if [ -f "build.gradle" ] || [ -f "build.gradle.kts" ] || [ -f "settings.gradle" ] || [ -f "settings.gradle.kts" ]; then
  if [[ ! " ${LANGS[*]:-} " =~ " java " ]]; then
    LANGS+=("java")
  fi
  FRAMEWORKS+=("gradle")
  if find . -maxdepth 3 -name "*.kt" -print -quit 2>/dev/null | grep -q .; then
    LANGS+=("kotlin")
  fi
fi

# PHP
if [ -f "composer.json" ]; then
  LANGS+=("php")
  if grep -q "symfony" composer.json 2>/dev/null; then FRAMEWORKS+=("symfony"); fi
  if grep -q "laravel" composer.json 2>/dev/null; then FRAMEWORKS+=("laravel"); fi
fi

# Ruby
if [ -f "Gemfile" ]; then
  LANGS+=("ruby")
  if grep -q "rails" Gemfile 2>/dev/null; then FRAMEWORKS+=("rails"); fi
fi

# C# / .NET
if ls *.csproj *.sln >/dev/null 2>&1 || find . -maxdepth 3 -name "*.csproj" -print -quit 2>/dev/null | grep -q .; then
  LANGS+=("csharp")
fi

# --- Monorepo detection ---------------------------------------------------------------

if [ -z "$MONOREPO" ]; then
  if [ -f "pnpm-workspace.yaml" ]; then MONOREPO="pnpm-workspace"
  elif [ -f "lerna.json" ]; then MONOREPO="lerna"
  elif [ -f "nx.json" ]; then MONOREPO="nx"
  elif [ -f "turbo.json" ]; then MONOREPO="turborepo"
  elif [ -f "rush.json" ]; then MONOREPO="rush"
  elif [ -f "package.json" ] && grep -q '"workspaces"' package.json 2>/dev/null; then
    MONOREPO="npm-workspaces"
  fi
fi

# --- File counts by extension --------------------------------------------------------

count_files() {
  local pattern="$1"
  find . -type f \
    -not -path "*/node_modules/*" \
    -not -path "*/.venv/*" \
    -not -path "*/venv/*" \
    -not -path "*/target/*" \
    -not -path "*/dist/*" \
    -not -path "*/build/*" \
    -not -path "*/.next/*" \
    -not -path "*/coverage/*" \
    -not -path "*/.git/*" \
    -name "$pattern" 2>/dev/null | wc -l | tr -d ' '
}

TS_COUNT=$(count_files "*.ts")
TSX_COUNT=$(count_files "*.tsx")
JS_COUNT=$(count_files "*.js")
JSX_COUNT=$(count_files "*.jsx")
PY_COUNT=$(count_files "*.py")
GO_COUNT=$(count_files "*.go")
RS_COUNT=$(count_files "*.rs")
JAVA_COUNT=$(count_files "*.java")
KT_COUNT=$(count_files "*.kt")
PHP_COUNT=$(count_files "*.php")
RB_COUNT=$(count_files "*.rb")
CS_COUNT=$(count_files "*.cs")

# --- Output ---------------------------------------------------------------------------

# Join arrays helper
join_arr() {
  local IFS=","
  echo "${*:-}"
}

LANGS_STR=$(join_arr "${LANGS[@]:-}")
FRAMEWORKS_STR=$(join_arr "${FRAMEWORKS[@]:-}")

if command -v jq >/dev/null 2>&1; then
  jq -n \
    --arg root "$PROJECT_ROOT" \
    --arg langs "$LANGS_STR" \
    --arg frameworks "$FRAMEWORKS_STR" \
    --arg monorepo "${MONOREPO:-none}" \
    --argjson ts "$TS_COUNT" \
    --argjson tsx "$TSX_COUNT" \
    --argjson js "$JS_COUNT" \
    --argjson jsx "$JSX_COUNT" \
    --argjson py "$PY_COUNT" \
    --argjson go "$GO_COUNT" \
    --argjson rs "$RS_COUNT" \
    --argjson java "$JAVA_COUNT" \
    --argjson kt "$KT_COUNT" \
    --argjson php "$PHP_COUNT" \
    --argjson rb "$RB_COUNT" \
    --argjson cs "$CS_COUNT" \
    '{
      root: $root,
      languages: ($langs | split(",") | map(select(length > 0))),
      frameworks: ($frameworks | split(",") | map(select(length > 0))),
      monorepo: $monorepo,
      file_counts: {
        ts: $ts, tsx: $tsx, js: $js, jsx: $jsx,
        py: $py, go: $go, rs: $rs,
        java: $java, kt: $kt,
        php: $php, rb: $rb, cs: $cs
      }
    }'
else
  echo "=== Detected Stack ==="
  echo "Root:       $PROJECT_ROOT"
  echo "Languages:  ${LANGS_STR:-none}"
  echo "Frameworks: ${FRAMEWORKS_STR:-none}"
  echo "Monorepo:   ${MONOREPO:-none}"
  echo ""
  echo "=== File Counts ==="
  echo "  TypeScript:  $TS_COUNT (.ts) + $TSX_COUNT (.tsx)"
  echo "  JavaScript:  $JS_COUNT (.js) + $JSX_COUNT (.jsx)"
  echo "  Python:      $PY_COUNT"
  echo "  Go:          $GO_COUNT"
  echo "  Rust:        $RS_COUNT"
  echo "  Java:        $JAVA_COUNT"
  echo "  Kotlin:      $KT_COUNT"
  echo "  PHP:         $PHP_COUNT"
  echo "  Ruby:        $RB_COUNT"
  echo "  C#:          $CS_COUNT"
fi

exit 0
