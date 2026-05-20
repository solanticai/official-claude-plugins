#!/usr/bin/env bash
# detect-stack.sh — Detect Next.js / React / TypeScript-strict / Supabase / Tailwind versions
# and stack drift relative to the canonical preset (Next 15 + React 19 + TS strict + Supabase + Tailwind).
#
# Usage: bash scripts/detect-stack.sh <project-root>
# Output: short text block to stdout. Exit 0 always (skill decides what to do with the result).

set -euo pipefail

PROJECT_ROOT="${1:-.}"

if [ ! -d "$PROJECT_ROOT" ]; then
  echo "ERROR: target is not a directory: $PROJECT_ROOT" >&2
  exit 0
fi

cd "$PROJECT_ROOT" || exit 0

# Pick the package.json that actually declares Next/React. In a monorepo invoked at
# the root, the root package.json is just the workspace manifest and won't have
# them — we have to walk apps/*, packages/*, etc.
PKG_JSON=""
MONOREPO=""

# Detect monorepo signals at root first.
if [ -f "pnpm-workspace.yaml" ]; then
  MONOREPO="pnpm"
elif [ -f "turbo.json" ]; then
  MONOREPO="turbo"
elif [ -f "nx.json" ]; then
  MONOREPO="nx"
elif [ -f "lerna.json" ]; then
  MONOREPO="lerna"
fi

# Helper: does this package.json declare next?
declares_next() {
  local f="$1"
  [ -f "$f" ] || return 1
  python3 - "$f" 2>/dev/null <<'PY'
import json, sys
try:
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        pkg = json.load(f)
except Exception:
    sys.exit(1)
for s in ("dependencies", "devDependencies"):
    if (pkg.get(s) or {}).get("next"):
        sys.exit(0)
sys.exit(1)
PY
}

# Try root first.
if [ -f "package.json" ] && declares_next "package.json"; then
  PKG_JSON="package.json"
fi

# If root didn't declare Next, walk common monorepo subdirectories.
if [ -z "$PKG_JSON" ]; then
  for candidate in apps/*/package.json packages/*/package.json services/*/package.json; do
    [ -f "$candidate" ] || continue
    if declares_next "$candidate"; then
      PKG_JSON="$candidate"
      break
    fi
  done
fi

# Fallback: pick root package.json even without Next, so we still report something.
if [ -z "$PKG_JSON" ] && [ -f "package.json" ]; then
  PKG_JSON="package.json"
fi

if [ -z "$PKG_JSON" ]; then
  echo "Stack:        no package.json detected — abort"
  echo "Drift:        n/a"
  exit 0
fi

# --- Helpers ---
# Extract a top-level dep version. Args: <dep-name> <package.json>. Echoes "" if absent.
get_dep_version() {
  local dep="$1"
  local pkg="$2"
  # Try dependencies, devDependencies, peerDependencies (in that order).
  python3 - "$dep" "$pkg" <<'PY' 2>/dev/null || echo ""
import json, sys
dep, path = sys.argv[1], sys.argv[2]
try:
    with open(path, 'r', encoding='utf-8') as f:
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

# Strip caret/tilde/range to first numeric. Returns "" when input is empty.
clean_version() {
  local raw="$1"
  [ -z "$raw" ] && return 0
  # Strip leading non-numeric (^, ~, >=, etc.) then take just the first version
  # token. If awk would produce "." (because numeric is empty), return empty.
  local cleaned
  cleaned=$(echo "$raw" | sed -E 's/^[^0-9]*//' | awk -F'[.-]' '{print $1"."$2"."$3}' | sed 's/\.\.$//;s/\.$//')
  case "$cleaned" in
    "."|""|"..") cleaned="";;
  esac
  printf '%s' "$cleaned"
}

# Major version helper.
major() {
  [ -z "$1" ] && return 0
  echo "$1" | awk -F'.' '{print $1}'
}

NEXT_RAW=$(get_dep_version "next" "$PKG_JSON")
REACT_RAW=$(get_dep_version "react" "$PKG_JSON")
TS_RAW=$(get_dep_version "typescript" "$PKG_JSON")
SUPABASE_JS_RAW=$(get_dep_version "@supabase/supabase-js" "$PKG_JSON")
SUPABASE_SSR_RAW=$(get_dep_version "@supabase/ssr" "$PKG_JSON")
SUPABASE_HELPERS_RAW=$(get_dep_version "@supabase/auth-helpers-nextjs" "$PKG_JSON")
TAILWIND_RAW=$(get_dep_version "tailwindcss" "$PKG_JSON")

NEXT_V=$(clean_version "$NEXT_RAW")
REACT_V=$(clean_version "$REACT_RAW")
TS_V=$(clean_version "$TS_RAW")
SUPABASE_JS_V=$(clean_version "$SUPABASE_JS_RAW")
SUPABASE_SSR_V=$(clean_version "$SUPABASE_SSR_RAW")
SUPABASE_HELPERS_V=$(clean_version "$SUPABASE_HELPERS_RAW")
TAILWIND_V=$(clean_version "$TAILWIND_RAW")

# --- TypeScript strict detection ---
# Read tsconfig.json from the same directory as the chosen package.json. In a
# monorepo, the root tsconfig is often an empty workspace shim; the real one
# lives next to apps/<app>/package.json.
PKG_DIR=$(dirname "$PKG_JSON")
TSCONFIG_PATH="$PKG_DIR/tsconfig.json"

TS_STRICT="unknown"
if [ -f "$TSCONFIG_PATH" ]; then
  TS_STRICT=$(python3 - "$TSCONFIG_PATH" <<'PY' 2>/dev/null
import json, sys, os, re

def load(path):
    if not os.path.exists(path):
        return None
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    text = re.sub(r'(?m)^\s*//.*$', '', text)
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
    text = re.sub(r',(\s*[}\]])', r'\1', text)
    try:
        return json.loads(text)
    except Exception:
        return None

def resolve(path, depth=0):
    if depth > 4 or path is None:
        return {}
    cfg = load(path) or {}
    base = {}
    extends_field = cfg.get("extends")
    if extends_field:
        if isinstance(extends_field, str):
            extends_list = [extends_field]
        else:
            extends_list = list(extends_field)
        here = os.path.dirname(path)
        for e in extends_list:
            ep = e
            if not os.path.isabs(ep):
                ep = os.path.normpath(os.path.join(here, ep))
            if not ep.endswith(".json"):
                ep = ep + ".json"
            base = {**base, **resolve(ep, depth + 1)}
    co = cfg.get("compilerOptions") or {}
    return {**base, **co}

start = sys.argv[1] if len(sys.argv) > 1 else "tsconfig.json"
opts = resolve(start)
strict = opts.get("strict")
if strict is True:
    print("yes")
elif strict is False:
    print("no")
else:
    print("partial" if any(k in opts for k in ("strictNullChecks", "noImplicitAny")) else "no")
PY
)
fi

# --- Build output ---
NEXT_MAJ=$(major "$NEXT_V")
REACT_MAJ=$(major "$REACT_V")
TAILWIND_MAJ=$(major "$TAILWIND_V")

# Drift assessment
DRIFT=()
[ -n "$NEXT_V" ] && [ "$NEXT_MAJ" != "15" ] && DRIFT+=("next ${NEXT_V} (canonical: 15.x)")
[ -z "$NEXT_V" ] && DRIFT+=("next not detected")
[ -n "$REACT_V" ] && [ "$REACT_MAJ" != "19" ] && DRIFT+=("react ${REACT_V} (canonical: 19.x)")
[ -z "$REACT_V" ] && DRIFT+=("react not detected")
[ "$TS_STRICT" != "yes" ] && DRIFT+=("typescript strict=${TS_STRICT}")
[ -z "$SUPABASE_JS_V" ] && [ -z "$SUPABASE_SSR_V" ] && DRIFT+=("supabase not detected")
[ -n "$SUPABASE_HELPERS_V" ] && DRIFT+=("@supabase/auth-helpers-nextjs (legacy; use @supabase/ssr)")
[ -z "$TAILWIND_V" ] && DRIFT+=("tailwindcss not detected")

PERMISSIVE="false"
[ ${#DRIFT[@]} -gt 0 ] && PERMISSIVE="true"

echo "Stack source:  $PKG_JSON${MONOREPO:+ (monorepo: $MONOREPO)}"
echo "Next.js:       ${NEXT_V:-not detected}"
echo "React:         ${REACT_V:-not detected}"
echo "TypeScript:    ${TS_V:-not detected} (strict: $TS_STRICT)"
echo "Supabase JS:   ${SUPABASE_JS_V:-not detected}"
echo "Supabase SSR:  ${SUPABASE_SSR_V:-not detected}"
[ -n "$SUPABASE_HELPERS_V" ] && echo "Supabase helpers (legacy): $SUPABASE_HELPERS_V"
echo "Tailwind:      ${TAILWIND_V:-not detected}"
echo "Permissive:    $PERMISSIVE"
if [ ${#DRIFT[@]} -gt 0 ]; then
  echo "Drift:"
  for d in "${DRIFT[@]}"; do
    echo "  - $d"
  done
else
  echo "Drift:         none (matches canonical preset)"
fi

exit 0
