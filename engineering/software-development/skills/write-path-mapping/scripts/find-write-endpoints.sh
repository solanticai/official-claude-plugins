#!/usr/bin/env bash
# find-write-endpoints.sh — Fast ripgrep-based seed list of candidate write entry points.
# Usage: bash scripts/find-write-endpoints.sh <project-root>
# Output: Newline-delimited `file:line:verb:label` records. Always exits 0.
#
# This is a SEED list — Phase 2 of the skill verifies and classifies each candidate.
# It favours recall over precision: false positives here are filtered later.

set -euo pipefail

PROJECT_ROOT="${1:-.}"

if [ ! -d "$PROJECT_ROOT" ]; then
  echo "ERROR: target is not a directory: $PROJECT_ROOT" >&2
  exit 1
fi

cd "$PROJECT_ROOT"

RG="rg"
if ! command -v rg >/dev/null 2>&1; then
  # Fall back to grep -rn; slower but works
  RG="grep -rn --include"
fi

EXCLUDES=(
  --glob '!node_modules/**'
  --glob '!.next/**'
  --glob '!dist/**'
  --glob '!build/**'
  --glob '!target/**'
  --glob '!.venv/**'
  --glob '!venv/**'
  --glob '!coverage/**'
  --glob '!.git/**'
  --glob '!.turbo/**'
  --glob '!*.min.js'
)

# Helper: emit a normalized line
emit() {
  local file="$1" line="$2" verb="$3" label="$4"
  printf '%s:%s:%s:%s\n' "$file" "$line" "$verb" "$label"
}

TMP="$(mktemp 2>/dev/null || echo "${TMPDIR:-/tmp}/wpm-endpoints.$$")"
: > "$TMP"

run_rg() {
  if command -v rg >/dev/null 2>&1; then
    rg --no-heading --line-number --color never "${EXCLUDES[@]}" "$@" 2>/dev/null || true
  else
    # Best-effort fallback for grep
    grep -rn --include="*.ts" --include="*.tsx" --include="*.js" --include="*.jsx" \
         --include="*.py" --include="*.go" --include="*.rb" --include="*.php" \
         --include="*.rs" --include="*.java" --include="*.kt" --include="*.cs" \
         --exclude-dir=node_modules --exclude-dir=.next --exclude-dir=dist \
         --exclude-dir=build --exclude-dir=target --exclude-dir=.venv \
         --exclude-dir=venv --exclude-dir=coverage --exclude-dir=.git \
         "$@" . 2>/dev/null || true
  fi
}

# --- Next.js App Router route handlers ------------------------------------------------
# app/**/route.ts exporting POST/PUT/PATCH/DELETE
if command -v rg >/dev/null 2>&1; then
  rg --no-heading --line-number --color never \
    -g 'app/**/route.{ts,tsx,js,jsx}' \
    -g '!node_modules/**' \
    -e 'export\s+(async\s+)?function\s+(POST|PUT|PATCH|DELETE)' 2>/dev/null | \
    while IFS=: read -r file line rest; do
      verb=$(echo "$rest" | grep -oE '(POST|PUT|PATCH|DELETE)' | head -1)
      emit "$file" "$line" "$verb" "next-app-route" >> "$TMP"
    done || true

  # Next.js Pages Router: pages/api/**
  rg --no-heading --line-number --color never \
    -g 'pages/api/**/*.{ts,tsx,js,jsx}' \
    -g '!node_modules/**' \
    -e 'req\.method\s*[!=]==\s*["'"'"']GET["'"'"']' 2>/dev/null | \
    while IFS=: read -r file line _rest; do
      emit "$file" "$line" "POST|PUT|PATCH|DELETE" "next-pages-api" >> "$TMP"
    done || true

  # Server Actions
  rg --no-heading --line-number --color never \
    -g '**/*.{ts,tsx,js,jsx}' \
    -g '!node_modules/**' \
    -e "['\"]use server['\"]" 2>/dev/null | \
    while IFS=: read -r file line _rest; do
      emit "$file" "$line" "ACTION" "next-server-action" >> "$TMP"
    done || true
fi

# --- Express / Fastify / Hono / Koa ---------------------------------------------------
run_rg -g '**/*.{ts,tsx,js,jsx}' \
  -e '\b(app|router|fastify)\.(post|put|patch|delete)\s*\(' | \
  while IFS=: read -r file line rest; do
    verb=$(echo "$rest" | grep -oE '\.(post|put|patch|delete)\b' | head -1 | tr -d '.' | tr '[:lower:]' '[:upper:]')
    emit "$file" "$line" "$verb" "express-like" >> "$TMP"
  done || true

# --- NestJS decorators ----------------------------------------------------------------
run_rg -g '**/*.{ts}' \
  -e '@(Post|Put|Patch|Delete|MessagePattern|EventPattern)\s*\(' | \
  while IFS=: read -r file line rest; do
    verb=$(echo "$rest" | grep -oE '@(Post|Put|Patch|Delete|MessagePattern|EventPattern)' | head -1 | tr -d '@')
    emit "$file" "$line" "$verb" "nestjs" >> "$TMP"
  done || true

# --- tRPC mutations -------------------------------------------------------------------
run_rg -g '**/*.{ts}' \
  -e '\.mutation\s*\(' | \
  while IFS=: read -r file line _rest; do
    emit "$file" "$line" "MUTATION" "trpc" >> "$TMP"
  done || true

# --- GraphQL mutations (resolver side) ------------------------------------------------
run_rg -g '**/*.{ts,js,graphql,gql}' \
  -e '^\s*Mutation\s*:\s*\{' | \
  while IFS=: read -r file line _rest; do
    emit "$file" "$line" "GQL_MUTATION" "graphql" >> "$TMP"
  done || true

# --- FastAPI / Flask / Django REST ----------------------------------------------------
run_rg -g '**/*.py' \
  -e '@(app|router)\.(post|put|patch|delete)\s*\(' | \
  while IFS=: read -r file line rest; do
    verb=$(echo "$rest" | grep -oE '\.(post|put|patch|delete)\b' | head -1 | tr -d '.' | tr '[:lower:]' '[:upper:]')
    emit "$file" "$line" "$verb" "fastapi-flask" >> "$TMP"
  done || true

run_rg -g '**/*.py' \
  -e '@action\(.*methods\s*=\s*\[.*(post|put|patch|delete)' | \
  while IFS=: read -r file line rest; do
    verb=$(echo "$rest" | grep -oiE '(post|put|patch|delete)' | head -1 | tr '[:lower:]' '[:upper:]')
    emit "$file" "$line" "$verb" "drf-action" >> "$TMP"
  done || true

# --- Django urls.py views -------------------------------------------------------------
run_rg -g '**/views.py' \
  -e '\bdef\s+(create|update|destroy|perform_create|perform_update|perform_destroy)\s*\(' | \
  while IFS=: read -r file line rest; do
    emit "$file" "$line" "WRITE" "django-view" >> "$TMP"
  done || true

# --- Rails routes and controllers -----------------------------------------------------
run_rg -g 'config/routes.rb' \
  -e '\b(post|put|patch|delete|resources)\b' | \
  while IFS=: read -r file line rest; do
    verb=$(echo "$rest" | grep -oiE '\b(post|put|patch|delete|resources)\b' | head -1 | tr '[:lower:]' '[:upper:]')
    emit "$file" "$line" "$verb" "rails-route" >> "$TMP"
  done || true

run_rg -g 'app/controllers/**/*.rb' \
  -e '\bdef\s+(create|update|destroy)\b' | \
  while IFS=: read -r file line rest; do
    verb=$(echo "$rest" | grep -oiE '\b(create|update|destroy)\b' | head -1 | tr '[:lower:]' '[:upper:]')
    emit "$file" "$line" "$verb" "rails-controller" >> "$TMP"
  done || true

# --- Laravel / Symfony ----------------------------------------------------------------
run_rg -g '**/routes/*.php' \
  -e 'Route::(post|put|patch|delete|resource)\s*\(' | \
  while IFS=: read -r file line rest; do
    verb=$(echo "$rest" | grep -oiE '\b(post|put|patch|delete|resource)\b' | head -1 | tr '[:lower:]' '[:upper:]')
    emit "$file" "$line" "$verb" "laravel-route" >> "$TMP"
  done || true

run_rg -g '**/*.php' \
  -e '#\[Route\(.*methods.*(POST|PUT|PATCH|DELETE)' | \
  while IFS=: read -r file line rest; do
    verb=$(echo "$rest" | grep -oE '(POST|PUT|PATCH|DELETE)' | head -1)
    emit "$file" "$line" "$verb" "symfony-route" >> "$TMP"
  done || true

# --- Go (gin/echo/fiber/chi/net-http) -------------------------------------------------
run_rg -g '**/*.go' \
  -e '\.(POST|PUT|PATCH|DELETE|Post|Put|Patch|Delete)\s*\(' | \
  while IFS=: read -r file line rest; do
    verb=$(echo "$rest" | grep -oE '(POST|PUT|PATCH|DELETE)' | head -1)
    emit "$file" "$line" "$verb" "go-router" >> "$TMP"
  done || true

run_rg -g '**/*.go' \
  -e '\bHandleFunc\s*\([^)]*,' | \
  while IFS=: read -r file line _rest; do
    emit "$file" "$line" "HANDLE" "go-net-http" >> "$TMP"
  done || true

# --- Rust (axum/actix/rocket) ---------------------------------------------------------
run_rg -g '**/*.rs' \
  -e '#\[(post|put|patch|delete)\s*\(' | \
  while IFS=: read -r file line rest; do
    verb=$(echo "$rest" | grep -oiE '\b(post|put|patch|delete)\b' | head -1 | tr '[:lower:]' '[:upper:]')
    emit "$file" "$line" "$verb" "rust-attr" >> "$TMP"
  done || true

run_rg -g '**/*.rs' \
  -e '\.route\([^)]*post\(|\.route\([^)]*put\(|\.route\([^)]*delete\(|\.route\([^)]*patch\(' | \
  while IFS=: read -r file line rest; do
    verb=$(echo "$rest" | grep -oiE '\b(post|put|patch|delete)\b' | head -1 | tr '[:lower:]' '[:upper:]')
    emit "$file" "$line" "$verb" "axum-route" >> "$TMP"
  done || true

# --- Supabase Edge Functions ----------------------------------------------------------
if [ -d "supabase/functions" ]; then
  find supabase/functions -name "index.ts" -type f 2>/dev/null | while read -r f; do
    emit "$f" "1" "FUNCTION" "supabase-edge" >> "$TMP"
  done
fi

# --- Cloudflare Workers ---------------------------------------------------------------
run_rg -g 'src/**/*.{ts,js}' \
  -e 'async\s+fetch\s*\(\s*request' | \
  while IFS=: read -r file line _rest; do
    emit "$file" "$line" "FETCH" "cf-worker" >> "$TMP"
  done || true

# --- Webhook handlers (heuristic: signature verify) -----------------------------------
run_rg -e 'stripe\.webhooks\.constructEvent|verifyStripeSignature|crypto\.verify.*webhook|Webhook::verify' | \
  while IFS=: read -r file line _rest; do
    emit "$file" "$line" "WEBHOOK" "webhook-receiver" >> "$TMP"
  done || true

# --- Queue consumers ------------------------------------------------------------------
run_rg -e '\bnew\s+Worker\s*\(|\.process\s*\(|@Processor\s*\(|subscribe\s*\([^)]*,\s*async' | \
  while IFS=: read -r file line _rest; do
    emit "$file" "$line" "CONSUME" "queue-consumer" >> "$TMP"
  done || true

# --- Cron jobs ------------------------------------------------------------------------
run_rg -e '@Cron\s*\(|schedule\.every\(|cron\.schedule\s*\(|supabase.*cron|pg_cron' | \
  while IFS=: read -r file line _rest; do
    emit "$file" "$line" "CRON" "scheduled-job" >> "$TMP"
  done || true

# Deduplicate (same file:line:verb)
if [ -s "$TMP" ]; then
  sort -u "$TMP"
fi
rm -f "$TMP" 2>/dev/null || true
exit 0
