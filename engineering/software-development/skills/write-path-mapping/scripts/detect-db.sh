#!/usr/bin/env bash
# detect-db.sh — Detect persistence layers and database tooling in a target directory.
# Usage: bash scripts/detect-db.sh <project-root>
# Output: JSON when jq is available, plain text otherwise. Always exits 0.
#
# Identifies: Supabase, raw Postgres, Prisma, Drizzle, TypeORM, Sequelize, Kysely,
# Mongoose, Django ORM, SQLAlchemy, ActiveRecord, Eloquent, Doctrine, Knex, gorm, sqlx,
# Redis, and live DB availability (DATABASE_URL, Supabase MCP).

set -euo pipefail

PROJECT_ROOT="${1:-.}"

if [ ! -d "$PROJECT_ROOT" ]; then
  echo "ERROR: target is not a directory: $PROJECT_ROOT" >&2
  exit 1
fi

cd "$PROJECT_ROOT"

DBS=()
SCHEMA_LOCATIONS=()
LIVE_AVAILABLE="none"

has_pkg() {
  # Match a dependency name in package.json (runtime or dev)
  [ -f package.json ] && grep -q "\"$1\"" package.json 2>/dev/null
}

has_py_pkg() {
  grep -q "$1" pyproject.toml requirements*.txt 2>/dev/null || false
}

# --- Supabase -------------------------------------------------------------------------
if [ -d "supabase" ]; then
  DBS+=("supabase")
  [ -d "supabase/migrations" ] && SCHEMA_LOCATIONS+=("supabase/migrations")
  [ -d "supabase/functions" ] && SCHEMA_LOCATIONS+=("supabase/functions")
  [ -f "supabase/config.toml" ] && SCHEMA_LOCATIONS+=("supabase/config.toml")
fi
if has_pkg "@supabase/supabase-js" || has_pkg "@supabase/ssr"; then
  [[ ! " ${DBS[*]:-} " =~ " supabase " ]] && DBS+=("supabase")
fi

# --- Prisma ---------------------------------------------------------------------------
if [ -f "prisma/schema.prisma" ] || find . -maxdepth 3 -name "schema.prisma" -print -quit 2>/dev/null | grep -q .; then
  DBS+=("prisma")
  SCHEMA_LOCATIONS+=("prisma/schema.prisma")
fi

# --- Drizzle --------------------------------------------------------------------------
if [ -f "drizzle.config.ts" ] || [ -f "drizzle.config.js" ] || [ -f "drizzle.config.json" ]; then
  DBS+=("drizzle")
  # Drizzle schema files are usually pointed to by the config; add common locations
  for candidate in src/db/schema.ts src/schema.ts db/schema.ts src/lib/db/schema.ts; do
    [ -f "$candidate" ] && SCHEMA_LOCATIONS+=("$candidate")
  done
fi

# --- Kysely ---------------------------------------------------------------------------
has_pkg "kysely" && DBS+=("kysely")

# --- TypeORM / Sequelize / Mongoose / Knex --------------------------------------------
has_pkg "typeorm" && DBS+=("typeorm")
has_pkg "sequelize" && DBS+=("sequelize")
has_pkg "mongoose" && { DBS+=("mongoose"); DBS+=("mongodb"); }
has_pkg "mikro-orm" && DBS+=("mikro-orm")
if has_pkg "knex"; then
  DBS+=("knex")
  [ -f "knexfile.ts" ] && SCHEMA_LOCATIONS+=("knexfile.ts")
  [ -f "knexfile.js" ] && SCHEMA_LOCATIONS+=("knexfile.js")
fi

# --- Raw node-postgres / postgres-js --------------------------------------------------
has_pkg '"pg":' && DBS+=("node-postgres")
has_pkg '"postgres":' && DBS+=("postgres-js")

# --- Redis ----------------------------------------------------------------------------
if has_pkg "ioredis" || has_pkg "\"redis\":" || has_pkg "@upstash/redis"; then
  DBS+=("redis")
fi

# --- Python ORMs ----------------------------------------------------------------------
if has_py_pkg "django"; then
  DBS+=("django-orm")
  [ -d "*/migrations" ] 2>/dev/null && SCHEMA_LOCATIONS+=("*/migrations")
fi
if has_py_pkg "sqlalchemy"; then
  DBS+=("sqlalchemy")
fi
if [ -f "alembic.ini" ] || [ -d "alembic" ]; then
  DBS+=("alembic")
  [ -d "alembic/versions" ] && SCHEMA_LOCATIONS+=("alembic/versions")
fi
if has_py_pkg "peewee"; then DBS+=("peewee"); fi
if has_py_pkg "tortoise-orm"; then DBS+=("tortoise-orm"); fi

# --- Ruby / Rails ---------------------------------------------------------------------
if [ -f "config/database.yml" ] || [ -f "db/schema.rb" ]; then
  DBS+=("active-record")
  [ -f "db/schema.rb" ] && SCHEMA_LOCATIONS+=("db/schema.rb")
  [ -d "db/migrate" ] && SCHEMA_LOCATIONS+=("db/migrate")
fi

# --- PHP ------------------------------------------------------------------------------
if [ -f "composer.json" ]; then
  if grep -q 'laravel/framework' composer.json 2>/dev/null; then
    DBS+=("eloquent")
    [ -d "database/migrations" ] && SCHEMA_LOCATIONS+=("database/migrations")
  fi
  if grep -q 'doctrine/orm' composer.json 2>/dev/null; then
    DBS+=("doctrine")
  fi
fi

# --- Go -------------------------------------------------------------------------------
if [ -f "go.mod" ]; then
  if grep -q "gorm.io/gorm" go.mod 2>/dev/null; then DBS+=("gorm"); fi
  if grep -q "sqlx" go.mod 2>/dev/null; then DBS+=("sqlx-go"); fi
  if grep -q "sqlc" go.mod 2>/dev/null; then DBS+=("sqlc"); fi
  if grep -q "uptrace/bun" go.mod 2>/dev/null; then DBS+=("bun"); fi
  if grep -q "ent." go.mod 2>/dev/null; then DBS+=("ent"); fi
fi

# --- Rust -----------------------------------------------------------------------------
if [ -f "Cargo.toml" ]; then
  if grep -q '^sqlx' Cargo.toml 2>/dev/null || grep -q 'sqlx = ' Cargo.toml 2>/dev/null; then DBS+=("sqlx-rust"); fi
  if grep -q 'diesel = ' Cargo.toml 2>/dev/null; then DBS+=("diesel"); fi
  if grep -q 'sea-orm = ' Cargo.toml 2>/dev/null; then DBS+=("sea-orm"); fi
fi

# --- Raw SQL schema directories -------------------------------------------------------
for dir in migrations db/migrations sql schemas schema; do
  [ -d "$dir" ] && SCHEMA_LOCATIONS+=("$dir")
done

# --- Live DB availability -------------------------------------------------------------
# Skill callers may optionally enrich with a live probe if credentials are present.
if [ -n "${DATABASE_URL:-}" ]; then
  LIVE_AVAILABLE="database-url"
fi
# Supabase MCP presence is inferred from mcp config files at user level — skill can check
if [ -f ".mcp.json" ] && grep -q "supabase" .mcp.json 2>/dev/null; then
  LIVE_AVAILABLE="supabase-mcp"
fi
# .env.local with DATABASE_URL (do not print the value)
if [ -f ".env.local" ] && grep -q "DATABASE_URL=" .env.local 2>/dev/null; then
  [ "$LIVE_AVAILABLE" = "none" ] && LIVE_AVAILABLE="env-file"
fi
if [ -f ".env" ] && grep -q "DATABASE_URL=" .env 2>/dev/null; then
  [ "$LIVE_AVAILABLE" = "none" ] && LIVE_AVAILABLE="env-file"
fi

# --- Deduplicate arrays ---------------------------------------------------------------
dedupe() {
  local -a input=("$@")
  local -A seen=()
  local -a output=()
  local item
  for item in "${input[@]:-}"; do
    [ -z "$item" ] && continue
    if [ -z "${seen[$item]:-}" ]; then
      seen[$item]=1
      output+=("$item")
    fi
  done
  printf '%s\n' "${output[@]:-}"
}

DBS_UNIQ=$(dedupe "${DBS[@]:-}" | tr '\n' ',' | sed 's/,$//')
SCHEMAS_UNIQ=$(dedupe "${SCHEMA_LOCATIONS[@]:-}" | tr '\n' ',' | sed 's/,$//')

# --- Output ---------------------------------------------------------------------------
if command -v jq >/dev/null 2>&1; then
  jq -n \
    --arg dbs "$DBS_UNIQ" \
    --arg schemas "$SCHEMAS_UNIQ" \
    --arg live "$LIVE_AVAILABLE" \
    '{
      persistence: ($dbs | split(",") | map(select(length > 0))),
      schema_locations: ($schemas | split(",") | map(select(length > 0))),
      live_db_available: $live
    }'
else
  echo "=== Persistence Layer ==="
  echo "Databases/ORMs:    ${DBS_UNIQ:-none}"
  echo "Schema locations:  ${SCHEMAS_UNIQ:-none}"
  echo "Live DB available: $LIVE_AVAILABLE"
fi

exit 0
