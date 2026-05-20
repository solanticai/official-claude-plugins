#!/usr/bin/env bash
# cross-os-lint.sh — Check for cross-OS compatibility issues
# Usage: bash scripts/cross-os-lint.sh <project-root>

set -euo pipefail

PROJECT_ROOT="${1:-.}"
SRC_DIR="$PROJECT_ROOT/src"

PASS=0
FAIL=0
WARN=0

check_pass() { echo "  PASS: $1"; PASS=$((PASS + 1)); }
check_fail() { echo "  FAIL: $1"; FAIL=$((FAIL + 1)); }
check_warn() { echo "  WARN: $1"; WARN=$((WARN + 1)); }

echo "=== Cross-OS Compatibility Check ==="
echo ""

# 1. Check for hardcoded path separators in source
echo "--- Path Separators ---"
if [ -d "$SRC_DIR" ]; then
  # Look for string concatenation with '/' for paths (common pattern)
  HARDCODED=$(grep -rn "path\s*+\s*['\"]/" "$SRC_DIR" --include="*.ts" --include="*.js" --include="*.mts" --include="*.mjs" 2>/dev/null | grep -v node_modules | grep -v "http" | grep -v "url" || true)
  if [ -n "$HARDCODED" ]; then
    COUNT=$(echo "$HARDCODED" | wc -l)
    check_fail "$COUNT potential hardcoded path separator(s) found"
    echo "$HARDCODED" | head -5 | while read -r line; do
      echo "    $line"
    done
  else
    check_pass "No obvious hardcoded path separators found in source"
  fi
else
  check_warn "No src/ directory found — skipping path separator check"
fi

# 2. Check .gitattributes
echo ""
echo "--- Line Endings ---"
if [ -f "$PROJECT_ROOT/.gitattributes" ]; then
  if grep -q "text=auto" "$PROJECT_ROOT/.gitattributes"; then
    check_pass ".gitattributes has text=auto line ending normalisation"
  else
    check_warn ".gitattributes exists but may not normalise line endings"
  fi
else
  check_warn ".gitattributes is missing — line endings may vary across OS"
fi

# 3. Check bin shebangs
echo ""
echo "--- Bin Shebangs ---"
if [ -f "$PROJECT_ROOT/package.json" ]; then
  BIN_FILES=$(node -e "
const p=require('$PROJECT_ROOT/package.json');
const bins = typeof p.bin === 'string' ? [p.bin] : (p.bin ? Object.values(p.bin) : []);
bins.forEach(b => console.log(b));
" 2>/dev/null || true)

  if [ -n "$BIN_FILES" ]; then
    echo "$BIN_FILES" | while read -r binfile; do
      FULL="$PROJECT_ROOT/$binfile"
      if [ -f "$FULL" ]; then
        SHEBANG=$(head -1 "$FULL" 2>/dev/null)
        if [ "$SHEBANG" = "#!/usr/bin/env node" ]; then
          check_pass "bin $binfile: correct shebang"
        elif echo "$SHEBANG" | grep -q '^#!/'; then
          check_warn "bin $binfile: non-portable shebang: $SHEBANG"
        else
          check_fail "bin $binfile: missing shebang"
        fi
      fi
    done
  else
    echo "  No bin entries found — skipping"
  fi
fi

# 4. Check npm scripts for Unix-specific commands
echo ""
echo "--- npm Scripts ---"
if [ -f "$PROJECT_ROOT/package.json" ]; then
  UNIX_CMDS=$(node -e "
const p=require('$PROJECT_ROOT/package.json');
const scripts = p.scripts || {};
const issues = [];
for (const [name, cmd] of Object.entries(scripts)) {
  if (/\brm\s+-rf\b/.test(cmd)) issues.push(name + ': uses rm -rf (use rimraf)');
  if (/\bcp\s+-r\b/.test(cmd)) issues.push(name + ': uses cp -r (use cpy-cli)');
  if (/\bmv\s+/.test(cmd) && !/node/.test(cmd)) issues.push(name + ': uses mv (use cross-platform alternative)');
  if (/^export\s+\w+=/.test(cmd)) issues.push(name + ': uses export VAR= (use cross-env)');
}
issues.forEach(i => console.log(i));
" 2>/dev/null || true)

  if [ -n "$UNIX_CMDS" ]; then
    echo "$UNIX_CMDS" | while read -r issue; do
      check_warn "Script $issue"
    done
  else
    check_pass "npm scripts use cross-platform compatible commands"
  fi
fi

# 5. Check CI workflow for OS matrix
echo ""
echo "--- CI OS Matrix ---"
CI_DIR="$PROJECT_ROOT/.github/workflows"
if [ -d "$CI_DIR" ]; then
  HAS_WINDOWS=false
  HAS_MACOS=false
  HAS_LINUX=false

  for workflow in "$CI_DIR"/*.yml "$CI_DIR"/*.yaml; do
    [ -f "$workflow" ] || continue
    if grep -q "windows" "$workflow" 2>/dev/null; then HAS_WINDOWS=true; fi
    if grep -q "macos" "$workflow" 2>/dev/null; then HAS_MACOS=true; fi
    if grep -q "ubuntu" "$workflow" 2>/dev/null; then HAS_LINUX=true; fi
  done

  if $HAS_LINUX && $HAS_MACOS && $HAS_WINDOWS; then
    check_pass "CI tests on Linux, macOS, and Windows"
  else
    MISSING=""
    $HAS_LINUX || MISSING="${MISSING}Linux "
    $HAS_MACOS || MISSING="${MISSING}macOS "
    $HAS_WINDOWS || MISSING="${MISSING}Windows "
    check_warn "CI missing OS coverage: $MISSING"
  fi
else
  check_warn "No .github/workflows/ directory found — no CI OS matrix to check"
fi

# 6. Check for case-sensitivity issues
echo ""
echo "--- Case Sensitivity ---"
if [ -d "$SRC_DIR" ]; then
  # Find files that would collide on case-insensitive filesystems
  DUPES=$(find "$SRC_DIR" -type f 2>/dev/null | sed 's|.*/||' | sort -f | uniq -di || true)
  if [ -n "$DUPES" ]; then
    check_fail "Files with case-only differences found (will collide on Windows/macOS):"
    echo "    $DUPES"
  else
    check_pass "No case-sensitivity issues found"
  fi
else
  echo "  No src/ directory — skipping"
fi

# Summary
echo ""
echo "=== Summary ==="
echo "  Passed: $PASS"
echo "  Failed: $FAIL"
echo "  Warnings: $WARN"

if [ "$FAIL" -gt 0 ]; then
  exit 1
fi
exit 0
