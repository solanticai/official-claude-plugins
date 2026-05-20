#!/usr/bin/env bash
# list-system-schemas.sh — Print the Postgres + Supabase system schemas to exclude.
# Usage: bash scripts/list-system-schemas.sh [--format json|text]
# Output: One schema per line (text mode, default) OR a JSON array.
#         Always exits 0.
#
# The skill excludes these schemas from:
#   - the schema-selection prompt in Phase 2
#   - the inventory SELECTs in Phase 3
#   - any parallel sub-agent dispatch in Phase 4
#
# Rationale: these schemas are owned by Postgres or by Supabase extensions.
# Anything we'd report on them would be (a) noise the user cannot action and
# (b) at risk of breaking the platform if "fixed". They are flag-only at most;
# in practice we just skip them.

set -euo pipefail

FORMAT="text"
if [ "${1:-}" = "--format" ] && [ -n "${2:-}" ]; then
  FORMAT="$2"
fi

# --- Postgres core ------------------------------------------------------------
# Owned by the database itself; always present.
PG_CORE=(
  pg_catalog
  information_schema
  pg_toast
)

# --- Supabase managed schemas ------------------------------------------------
# These are created by the Supabase platform and/or its default extensions.
# Users rarely own them and modifying them is strongly discouraged.
SUPABASE_MANAGED=(
  auth                 # Supabase Auth (GoTrue)
  storage              # Supabase Storage
  realtime             # Supabase Realtime
  vault                # Supabase Vault (encrypted secrets)
  extensions           # default extension namespace
  graphql              # pg_graphql internals
  graphql_public       # pg_graphql public entrypoint
  net                  # pg_net (HTTP from Postgres)
  pgsodium             # pgsodium crypto extension
  pgsodium_masks       # pgsodium mask views
  supabase_functions   # Supabase Edge Function metadata
  supabase_migrations  # Supabase migration tracking
  _analytics           # Supabase analytics (Logflare)
  _realtime            # Supabase realtime internal
  cron                 # pg_cron schedules (included — rarely user-owned)
  pgtle                # pg_tle trusted language extension
  tiger                # PostGIS tiger_geocoder (if PostGIS installed)
  tiger_data           # PostGIS tiger data
  topology             # PostGIS topology
)

ALL=("${PG_CORE[@]}" "${SUPABASE_MANAGED[@]}")

case "$FORMAT" in
  json)
    # Compact JSON array, no dependency on jq
    printf '['
    first=1
    for s in "${ALL[@]}"; do
      if [ "$first" -eq 1 ]; then
        first=0
      else
        printf ','
      fi
      printf '"%s"' "$s"
    done
    printf ']\n'
    ;;
  text|*)
    for s in "${ALL[@]}"; do
      echo "$s"
    done
    ;;
esac

exit 0
