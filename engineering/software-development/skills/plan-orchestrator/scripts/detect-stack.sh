#!/usr/bin/env bash
# detect-stack.sh — Identify language, framework, and persistence layer.
# Usage: bash scripts/detect-stack.sh <project-root>
# Output: A short text block; exit 0 always.
#
# This is intentionally less exhaustive than dead-code-audit's detect-stack.sh
# because the orchestrator only needs hints to seed the sub-agent prompts —
# the agents themselves do the deep introspection.

set -euo pipefail

PROJECT_ROOT="${1:-.}"

if [ ! -d "$PROJECT_ROOT" ]; then
  echo "ERROR: target is not a directory: $PROJECT_ROOT" >&2
  exit 0
fi

cd "$PROJECT_ROOT"

LANGS=()
FRAMEWORKS=()
PERSISTENCE=()
INFRA=()

# --- Languages ---
[ -f "package.json" ] && LANGS+=("JS/TS")
[ -f "pyproject.toml" ] || [ -f "setup.py" ] || ls requirements*.txt >/dev/null 2>&1 && LANGS+=("Python")
[ -f "go.mod" ] && LANGS+=("Go")
[ -f "Cargo.toml" ] && LANGS+=("Rust")
[ -f "pom.xml" ] || [ -f "build.gradle" ] || [ -f "build.gradle.kts" ] && LANGS+=("Java/Kotlin")
[ -f "composer.json" ] && LANGS+=("PHP")
[ -f "Gemfile" ] && LANGS+=("Ruby")
ls *.csproj *.sln >/dev/null 2>&1 && LANGS+=("C#")

# --- Frameworks (best-effort) ---
if [ -f "package.json" ]; then
  PKG=$(cat package.json 2>/dev/null || echo "{}")
  echo "$PKG" | grep -q '"next"' && FRAMEWORKS+=("Next.js")
  echo "$PKG" | grep -q '"react"' && FRAMEWORKS+=("React")
  echo "$PKG" | grep -q '"vue"' && FRAMEWORKS+=("Vue")
  echo "$PKG" | grep -q '"svelte"' && FRAMEWORKS+=("Svelte")
  echo "$PKG" | grep -q '"express"' && FRAMEWORKS+=("Express")
  echo "$PKG" | grep -q '"fastify"' && FRAMEWORKS+=("Fastify")
  echo "$PKG" | grep -q '"hono"' && FRAMEWORKS+=("Hono")
  echo "$PKG" | grep -q '"@nestjs/' && FRAMEWORKS+=("NestJS")
  echo "$PKG" | grep -q '"tailwindcss"' && FRAMEWORKS+=("TailwindCSS")
fi

if [ -f "pyproject.toml" ] || ls requirements*.txt >/dev/null 2>&1; then
  grep -lE '(^|[^a-z])(django|fastapi|flask)' pyproject.toml requirements*.txt 2>/dev/null | head -1 | while read f; do
    grep -qE '(^|[^a-z])django' "$f" 2>/dev/null && echo "Django"
    grep -qE '(^|[^a-z])fastapi' "$f" 2>/dev/null && echo "FastAPI"
    grep -qE '(^|[^a-z])flask' "$f" 2>/dev/null && echo "Flask"
  done | sort -u | while read fw; do FRAMEWORKS+=("$fw"); done || true
fi

# --- Persistence layer ---
[ -d "supabase" ] && PERSISTENCE+=("Supabase")
[ -f "prisma/schema.prisma" ] && PERSISTENCE+=("Prisma")
grep -rqs "drizzle-orm" --include="package.json" . 2>/dev/null && PERSISTENCE+=("Drizzle")
grep -rqs "typeorm" --include="package.json" . 2>/dev/null && PERSISTENCE+=("TypeORM")
[ -d "db/migrate" ] && PERSISTENCE+=("Rails ActiveRecord")

# --- Infra ---
[ -f "Dockerfile" ] && INFRA+=("Docker")
[ -d ".github/workflows" ] && INFRA+=("GitHub Actions")
[ -f "vercel.json" ] && INFRA+=("Vercel")
[ -f "wrangler.toml" ] || [ -f "wrangler.jsonc" ] && INFRA+=("Cloudflare Workers")
[ -f "fly.toml" ] && INFRA+=("Fly.io")
[ -f ".gitlab-ci.yml" ] && INFRA+=("GitLab CI")

# --- Monorepo signals ---
MONOREPO=""
[ -f "pnpm-workspace.yaml" ] && MONOREPO="pnpm"
[ -f "turbo.json" ] && MONOREPO="turbo"
[ -f "nx.json" ] && MONOREPO="nx"
[ -f "lerna.json" ] && MONOREPO="lerna"

echo "Languages:    ${LANGS[*]:-none detected}"
echo "Frameworks:   ${FRAMEWORKS[*]:-none detected}"
echo "Persistence:  ${PERSISTENCE[*]:-none detected}"
echo "Infra:        ${INFRA[*]:-none detected}"
[ -n "$MONOREPO" ] && echo "Monorepo:     $MONOREPO"

exit 0
