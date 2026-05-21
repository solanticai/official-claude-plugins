#!/usr/bin/env bash
# detect-stack.sh — Detect primary language, framework, runtime, and package manager
# Usage: detect-stack.sh <target_dir>
# Output: JSON to stdout

TARGET="${1:-.}"
TARGET="$(cd "$TARGET" && pwd)"

detect_node_framework() {
  local pkg="$TARGET/package.json"
  [[ ! -f "$pkg" ]] && echo "none" && return
  python3 - <<PYEOF
import json, sys
try:
    with open("$pkg") as f:
        p = json.load(f)
    deps = {**p.get("dependencies",{}), **p.get("devDependencies",{})}
    if "next" in deps: print("Next.js"); sys.exit()
    if "nuxt" in deps or "nuxt3" in deps: print("Nuxt.js"); sys.exit()
    if "@sveltejs/kit" in deps: print("SvelteKit"); sys.exit()
    if "@remix-run/node" in deps or "@remix-run/react" in deps: print("Remix"); sys.exit()
    if "astro" in deps: print("Astro"); sys.exit()
    if "@nestjs/core" in deps: print("NestJS"); sys.exit()
    if "fastify" in deps: print("Fastify"); sys.exit()
    if "express" in deps: print("Express"); sys.exit()
    if "hono" in deps: print("Hono"); sys.exit()
    if "react-native" in deps or "expo" in deps: print("React Native"); sys.exit()
    if "electron" in deps: print("Electron"); sys.exit()
    if "react" in deps: print("React (Vite/CRA)"); sys.exit()
    if "vue" in deps: print("Vue"); sys.exit()
    if "@angular/core" in deps: print("Angular"); sys.exit()
    print("Node (no framework)")
except Exception as e:
    print("unknown")
PYEOF
}

detect_framework_version() {
  local pkg="$TARGET/package.json"
  local dep="$1"
  [[ ! -f "$pkg" ]] && echo "unknown" && return
  python3 - <<PYEOF 2>/dev/null || echo "unknown"
import json
with open("$pkg") as f:
    p = json.load(f)
deps = {**p.get("dependencies",{}), **p.get("devDependencies",{})}
print(deps.get("$dep", "unknown").lstrip("^~>="))
PYEOF
}

detect_package_manager() {
  [[ -f "$TARGET/pnpm-lock.yaml" ]] && echo "pnpm" && return
  [[ -f "$TARGET/yarn.lock" ]] && echo "yarn" && return
  [[ -f "$TARGET/bun.lockb" ]] && echo "bun" && return
  [[ -f "$TARGET/package-lock.json" ]] && echo "npm" && return
  [[ -f "$TARGET/package.json" ]] && echo "npm (no lockfile)" && return
  echo "none"
}

detect_monorepo() {
  local tool="none"
  local pkg_count=0
  [[ -f "$TARGET/pnpm-workspace.yaml" ]] && tool="pnpm-workspaces"
  [[ -f "$TARGET/turbo.json" ]] && tool="turborepo"
  [[ -f "$TARGET/nx.json" ]] && tool="nx"
  [[ -f "$TARGET/lerna.json" ]] && tool="lerna"
  [[ -f "$TARGET/rush.json" ]] && tool="rush"
  [[ -f "$TARGET/go.work" ]] && tool="go-workspace"

  if [[ "$tool" != "none" ]]; then
    pkg_count=$(find "$TARGET/packages" "$TARGET/apps" -maxdepth 2 -name "package.json" 2>/dev/null | wc -l | tr -d ' ')
  fi
  echo "{\"monorepo\": $([ "$tool" != "none" ] && echo "true" || echo "false"), \"tool\": \"$tool\", \"package_count\": $pkg_count}"
}

detect_primary_language() {
  # Check manifests in priority order
  [[ -f "$TARGET/package.json" ]] && { [[ -f "$TARGET/tsconfig.json" ]] && echo "TypeScript" || echo "JavaScript"; return; }
  [[ -f "$TARGET/Cargo.toml" ]] && echo "Rust" && return
  [[ -f "$TARGET/go.mod" ]] && echo "Go" && return
  [[ -f "$TARGET/pyproject.toml" || -f "$TARGET/requirements.txt" || -f "$TARGET/setup.py" ]] && echo "Python" && return
  [[ -f "$TARGET/Gemfile" ]] && echo "Ruby" && return
  [[ -f "$TARGET/pom.xml" || -f "$TARGET/build.gradle" ]] && echo "Java/JVM" && return
  [[ -f "$TARGET/composer.json" ]] && echo "PHP" && return
  # Fallback: count source files
  local ts_count py_count go_count rs_count
  ts_count=$(find "$TARGET/src" -name "*.ts" -o -name "*.tsx" 2>/dev/null | wc -l | tr -d ' ')
  py_count=$(find "$TARGET" -maxdepth 4 -name "*.py" 2>/dev/null | grep -v node_modules | wc -l | tr -d ' ')
  go_count=$(find "$TARGET" -maxdepth 4 -name "*.go" 2>/dev/null | wc -l | tr -d ' ')
  rs_count=$(find "$TARGET" -maxdepth 4 -name "*.rs" 2>/dev/null | wc -l | tr -d ' ')
  local max=$ts_count lang="TypeScript"
  [[ $py_count -gt $max ]] && { max=$py_count; lang="Python"; }
  [[ $go_count -gt $max ]] && { max=$go_count; lang="Go"; }
  [[ $rs_count -gt $max ]] && { max=$rs_count; lang="Rust"; }
  echo "$lang"
}

detect_runtime_version() {
  local nvmrc="$TARGET/.nvmrc"
  local engines
  engines=$(python3 -c "import json; p=json.load(open('$TARGET/package.json')); print(p.get('engines',{}).get('node',''))" 2>/dev/null)
  [[ -f "$nvmrc" ]] && cat "$nvmrc" | tr -d '\n' && return
  [[ -n "$engines" ]] && echo "$engines" && return
  node --version 2>/dev/null || echo "unknown"
}

# --- Build output ---
PRIMARY_LANG=$(detect_primary_language)
FRAMEWORK=$(detect_node_framework)
PKG_MANAGER=$(detect_package_manager)
MONOREPO=$(detect_monorepo)

# Get framework version
FW_VERSION="unknown"
case "$FRAMEWORK" in
  "Next.js") FW_VERSION=$(detect_framework_version "next") ;;
  "Nuxt.js") FW_VERSION=$(detect_framework_version "nuxt") ;;
  "SvelteKit") FW_VERSION=$(detect_framework_version "@sveltejs/kit") ;;
  "NestJS") FW_VERSION=$(detect_framework_version "@nestjs/core") ;;
  "Fastify") FW_VERSION=$(detect_framework_version "fastify") ;;
  "Express") FW_VERSION=$(detect_framework_version "express") ;;
  "React (Vite/CRA)") FW_VERSION=$(detect_framework_version "react") ;;
esac

RUNTIME_VERSION=$(detect_runtime_version)

# TypeScript check
TS_STRICT="false"
if [[ -f "$TARGET/tsconfig.json" ]]; then
  TS_STRICT=$(python3 -c "
import json
try:
  with open('$TARGET/tsconfig.json') as f:
    data = f.read()
  # strip comments (basic)
  import re
  data = re.sub(r'//.*', '', data)
  obj = json.loads(data)
  opts = obj.get('compilerOptions', {})
  print('true' if opts.get('strict') else 'false')
except:
  print('unknown')
" 2>/dev/null || echo "unknown")
fi

python3 - <<PYEOF
import json
print(json.dumps({
  "primary_language": "$PRIMARY_LANG",
  "framework": "$FRAMEWORK",
  "framework_version": "$FW_VERSION",
  "runtime_version": "$RUNTIME_VERSION",
  "package_manager": "$PKG_MANAGER",
  "typescript_strict": "$TS_STRICT",
  "monorepo": $MONOREPO
}, indent=2))
PYEOF
