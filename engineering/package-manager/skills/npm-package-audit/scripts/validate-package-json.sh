#!/usr/bin/env bash
# validate-package-json.sh — Validate package.json fields for npm publishing
# Usage: bash scripts/validate-package-json.sh <project-root>

set -euo pipefail

PROJECT_ROOT="${1:-.}"
PKG_FILE="$PROJECT_ROOT/package.json"

if [ ! -f "$PKG_FILE" ]; then
  echo "FAIL: No package.json found at $PKG_FILE"
  exit 1
fi

PASS=0
FAIL=0
WARN=0

check_pass() { echo "  PASS: $1"; PASS=$((PASS + 1)); }
check_fail() { echo "  FAIL: $1"; FAIL=$((FAIL + 1)); }
check_warn() { echo "  WARN: $1"; WARN=$((WARN + 1)); }

echo "=== package.json Validation ==="
echo ""

# Use node to parse JSON (cross-platform, no jq dependency)
get_field() {
  node -e "const p=require('$PKG_FILE'); const v=$1; process.stdout.write(String(v ?? ''))" 2>/dev/null || echo ""
}

get_field_type() {
  node -e "const p=require('$PKG_FILE'); const v=$1; console.log(typeof v)" 2>/dev/null || echo "undefined"
}

# Required: name
NAME=$(get_field "p.name")
if [ -n "$NAME" ]; then
  # Check lowercase
  if echo "$NAME" | grep -qP '[A-Z ]'; then
    check_fail "name contains uppercase or spaces: $NAME"
  else
    check_pass "name: $NAME"
  fi
else
  check_fail "name is missing"
fi

# Required: version (semver check)
VERSION=$(get_field "p.version")
if [ -n "$VERSION" ]; then
  if echo "$VERSION" | grep -qP '^\d+\.\d+\.\d+(-[a-zA-Z0-9.]+)?(\+[a-zA-Z0-9.]+)?$'; then
    check_pass "version: $VERSION (valid semver)"
  else
    check_fail "version '$VERSION' is not valid semver"
  fi
else
  check_fail "version is missing"
fi

# Required: description
DESC=$(get_field "p.description")
if [ -n "$DESC" ]; then
  DESC_LEN=${#DESC}
  if [ "$DESC_LEN" -gt 280 ]; then
    check_warn "description is $DESC_LEN chars (recommended: under 280)"
  else
    check_pass "description: ${DESC:0:80}..."
  fi
else
  check_fail "description is missing"
fi

# Required: license (SPDX)
LICENSE=$(get_field "p.license")
if [ -n "$LICENSE" ]; then
  case "$LICENSE" in
    MIT|ISC|Apache-2.0|BSD-2-Clause|BSD-3-Clause|GPL-2.0|GPL-3.0|LGPL-2.1|LGPL-3.0|MPL-2.0|0BSD|Unlicense|WTFPL)
      check_pass "license: $LICENSE (valid SPDX)";;
    *)
      check_warn "license: $LICENSE (verify it is a valid SPDX identifier)";;
  esac
else
  check_fail "license is missing"
fi

# Required: main or exports
MAIN=$(get_field "p.main")
EXPORTS_TYPE=$(get_field_type "p.exports")
if [ -n "$MAIN" ] || [ "$EXPORTS_TYPE" = "object" ] || [ "$EXPORTS_TYPE" = "string" ]; then
  check_pass "entry point defined (main or exports)"
else
  check_fail "no entry point: neither main nor exports is defined"
fi

# Required: files array
FILES_TYPE=$(get_field_type "p.files")
if [ "$FILES_TYPE" = "object" ]; then
  check_pass "files array is defined"
else
  check_fail "files array is missing — package may include unnecessary files"
fi

# Recommended: types
TYPES=$(get_field "p.types || p.typings")
if [ -n "$TYPES" ]; then
  check_pass "types: $TYPES"
else
  check_warn "types/typings field is missing — TypeScript consumers won't get type inference"
fi

# Recommended: engines
ENGINES_NODE=$(get_field "p.engines?.node")
if [ -n "$ENGINES_NODE" ]; then
  check_pass "engines.node: $ENGINES_NODE"
else
  check_warn "engines.node is missing — consumers don't know the minimum Node version"
fi

# Recommended: repository
REPO=$(get_field "p.repository?.url || (typeof p.repository === 'string' ? p.repository : '')")
if [ -n "$REPO" ]; then
  check_pass "repository: $REPO"
else
  check_warn "repository is missing"
fi

# Recommended: keywords
KEYWORD_COUNT=$(node -e "const p=require('$PKG_FILE'); console.log(Array.isArray(p.keywords) ? p.keywords.length : 0)" 2>/dev/null || echo "0")
if [ "$KEYWORD_COUNT" -ge 3 ]; then
  check_pass "keywords: $KEYWORD_COUNT terms"
elif [ "$KEYWORD_COUNT" -gt 0 ]; then
  check_warn "keywords: only $KEYWORD_COUNT terms (recommend 3+)"
else
  check_warn "keywords array is missing or empty"
fi

# Recommended: homepage
HOMEPAGE=$(get_field "p.homepage")
if [ -n "$HOMEPAGE" ]; then
  check_pass "homepage: $HOMEPAGE"
else
  check_warn "homepage is missing"
fi

# Recommended: bugs
BUGS=$(get_field "p.bugs?.url || (typeof p.bugs === 'string' ? p.bugs : '')")
if [ -n "$BUGS" ]; then
  check_pass "bugs: $BUGS"
else
  check_warn "bugs URL is missing"
fi

# Check bin shebangs
BIN_COUNT=$(node -e "
const p=require('$PKG_FILE');
if (typeof p.bin === 'string') console.log(1);
else if (typeof p.bin === 'object') console.log(Object.keys(p.bin).length);
else console.log(0);
" 2>/dev/null || echo "0")

if [ "$BIN_COUNT" -gt 0 ]; then
  echo ""
  echo "  Bin entries found: $BIN_COUNT"
  # Check shebangs of bin files
  node -e "
const p=require('$PKG_FILE');
const bins = typeof p.bin === 'string' ? {'': p.bin} : (p.bin || {});
Object.entries(bins).forEach(([name, file]) => {
  console.log(file);
});
" 2>/dev/null | while read -r binfile; do
    FULL_PATH="$PROJECT_ROOT/$binfile"
    if [ -f "$FULL_PATH" ]; then
      FIRST_LINE=$(head -1 "$FULL_PATH" 2>/dev/null)
      if echo "$FIRST_LINE" | grep -q '#!/usr/bin/env node'; then
        check_pass "bin $binfile has correct shebang"
      elif echo "$FIRST_LINE" | grep -q '^#!'; then
        check_warn "bin $binfile shebang: $FIRST_LINE (expected #!/usr/bin/env node)"
      else
        check_fail "bin $binfile missing shebang (needs #!/usr/bin/env node)"
      fi
    else
      check_warn "bin $binfile does not exist at $FULL_PATH (may need build first)"
    fi
  done
fi

# Summary
echo ""
echo "=== Summary ==="
echo "  Passed: $PASS"
echo "  Failed: $FAIL"
echo "  Warnings: $WARN"
echo ""

if [ "$FAIL" -gt 0 ]; then
  echo "Result: ISSUES FOUND ($FAIL failures, $WARN warnings)"
  exit 1
else
  echo "Result: OK ($WARN warnings)"
  exit 0
fi
