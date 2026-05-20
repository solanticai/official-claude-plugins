#!/usr/bin/env bash
# check-profile-freshness.sh — Decide whether .anthril/preset-profile.md is current
# vs the actual package.json + tsconfig + tailwind.config + supabase imports.
#
# Usage: bash scripts/check-profile-freshness.sh <project-root>
# Output:
#   stdout: short reason text
#   exit 0  — profile is current (or no profile exists; caller decides)
#   exit 10 — profile is stale; caller should re-dispatch profile-builder in --update mode
#   exit 1  — error (e.g. target missing)
#
# We don't try to be exhaustive — the profile-builder agent does the deep audit.
# This script just answers: "is the recorded next/react/typescript/supabase/tailwind
# version still consistent with package.json?"

set -euo pipefail

PROJECT_ROOT="${1:-.}"

if [ ! -d "$PROJECT_ROOT" ]; then
  echo "ERROR: target is not a directory" >&2
  exit 1
fi

cd "$PROJECT_ROOT"

PROFILE=".anthril/preset-profile.md"

if [ ! -f "$PROFILE" ]; then
  echo "Profile absent — caller must create."
  exit 0
fi

if [ ! -f "package.json" ]; then
  echo "package.json absent — cannot compare. Profile assumed current."
  exit 0
fi

# Helper: pull a value off a "key:" line in the profile (very forgiving).
read_profile_field() {
  local label="$1"
  grep -E "^\s*[-*|]?\s*\*\*$label:?\*\*" "$PROFILE" 2>/dev/null \
    | head -1 \
    | sed -E 's/.*\*\*[^*]+\*\*[^|]*[|:][^a-zA-Z0-9.@\/^~-]*([^|]*).*/\1/' \
    | sed -E 's/^\s+//;s/\s+$//'
}

# Try a few naming conventions used in the template.
PROFILE_NEXT=$(grep -iE "next.*\*\*[^*]+\*\*" "$PROFILE" | head -1 || true)
PROFILE_REACT=$(grep -iE "react.*\*\*[^*]+\*\*" "$PROFILE" | head -1 || true)

# Simplest reliable approach: pull the actual current versions from package.json
# and look for them in the profile. If the profile mentions the current version
# string, we treat it as current. Otherwise stale.
get_dep_version() {
  python3 - "$1" <<'PY' 2>/dev/null || echo ""
import json, sys
dep = sys.argv[1]
try:
    with open("package.json", 'r', encoding='utf-8') as f:
        pkg = json.load(f)
except Exception:
    print(""); sys.exit(0)
for section in ("dependencies", "devDependencies", "peerDependencies"):
    v = (pkg.get(section) or {}).get(dep)
    if v:
        print(v); sys.exit(0)
print("")
PY
}

# Helper: is this current pkg version visible in the profile?
profile_mentions() {
  local version_string="$1"
  [ -z "$version_string" ] && return 0  # nothing to compare → not stale on this dep
  # strip caret/tilde and reduce to MAJOR.MINOR
  local clean
  clean=$(echo "$version_string" | sed -E 's/^[^0-9]*//' | awk -F'.' '{print $1"."$2}')
  grep -q "$clean" "$PROFILE"
}

CURRENT_NEXT=$(get_dep_version "next")
CURRENT_REACT=$(get_dep_version "react")
CURRENT_TS=$(get_dep_version "typescript")
CURRENT_SUPABASE=$(get_dep_version "@supabase/supabase-js")
CURRENT_SSR=$(get_dep_version "@supabase/ssr")
CURRENT_TAILWIND=$(get_dep_version "tailwindcss")

STALE_REASONS=()

profile_mentions "$CURRENT_NEXT"      || STALE_REASONS+=("next ${CURRENT_NEXT} not mentioned in profile")
profile_mentions "$CURRENT_REACT"     || STALE_REASONS+=("react ${CURRENT_REACT} not mentioned in profile")
profile_mentions "$CURRENT_TS"        || STALE_REASONS+=("typescript ${CURRENT_TS} not mentioned in profile")
profile_mentions "$CURRENT_SUPABASE"  || STALE_REASONS+=("@supabase/supabase-js ${CURRENT_SUPABASE} not mentioned in profile")
profile_mentions "$CURRENT_SSR"       || STALE_REASONS+=("@supabase/ssr ${CURRENT_SSR} not mentioned in profile")
profile_mentions "$CURRENT_TAILWIND"  || STALE_REASONS+=("tailwindcss ${CURRENT_TAILWIND} not mentioned in profile")

# Compare timestamps: if package.json or tsconfig is newer than the profile, mark stale.
if [ -n "$(command -v stat)" ]; then
  PROFILE_MTIME=$(stat -c '%Y' "$PROFILE" 2>/dev/null || stat -f '%m' "$PROFILE" 2>/dev/null || echo "0")
  PKG_MTIME=$(stat -c '%Y' "package.json" 2>/dev/null || stat -f '%m' "package.json" 2>/dev/null || echo "0")
  if [ -n "$PROFILE_MTIME" ] && [ -n "$PKG_MTIME" ] && [ "$PKG_MTIME" -gt "$PROFILE_MTIME" ]; then
    STALE_REASONS+=("package.json modified after profile")
  fi
fi

if [ ${#STALE_REASONS[@]} -eq 0 ]; then
  echo "Profile is current."
  exit 0
fi

echo "Profile is stale:"
for r in "${STALE_REASONS[@]}"; do
  echo "  - $r"
done
exit 10
