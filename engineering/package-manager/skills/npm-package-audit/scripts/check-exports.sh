#!/usr/bin/env bash
# check-exports.sh — Verify exports map resolves correctly
# Usage: bash scripts/check-exports.sh <project-root>

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

echo "=== Exports Map Verification ==="
echo ""

# Check if exports field exists
HAS_EXPORTS=$(node -e "const p=require('$PKG_FILE'); console.log(p.exports ? 'yes' : 'no')" 2>/dev/null || echo "no")

if [ "$HAS_EXPORTS" = "no" ]; then
  echo "  No exports field found. Checking legacy fields..."

  # Check main, module, types
  MAIN=$(node -e "const p=require('$PKG_FILE'); process.stdout.write(p.main || '')" 2>/dev/null)
  MODULE=$(node -e "const p=require('$PKG_FILE'); process.stdout.write(p.module || '')" 2>/dev/null)
  TYPES=$(node -e "const p=require('$PKG_FILE'); process.stdout.write(p.types || p.typings || '')" 2>/dev/null)

  if [ -n "$MAIN" ]; then
    if [ -f "$PROJECT_ROOT/$MAIN" ]; then
      check_pass "main: $MAIN exists"
    else
      check_fail "main: $MAIN does not exist"
    fi
  else
    check_warn "main field is missing"
  fi

  if [ -n "$MODULE" ]; then
    if [ -f "$PROJECT_ROOT/$MODULE" ]; then
      check_pass "module: $MODULE exists"
    else
      check_fail "module: $MODULE does not exist"
    fi
  fi

  if [ -n "$TYPES" ]; then
    if [ -f "$PROJECT_ROOT/$TYPES" ]; then
      check_pass "types: $TYPES exists"
    else
      check_fail "types: $TYPES does not exist"
    fi
  fi

  check_warn "No exports map — consider adding conditional exports for better Node.js resolution"
else
  # Parse and verify each export path
  node -e "
const path = require('path');
const p = require('$PKG_FILE');
const projectRoot = '$PROJECT_ROOT';

function checkCondition(exportPath, conditions) {
  if (typeof conditions === 'string') {
    // Direct string export
    const fullPath = path.join(projectRoot, conditions);
    const exists = require('fs').existsSync(fullPath);
    console.log(JSON.stringify({ path: exportPath, type: 'direct', file: conditions, exists }));
    return;
  }

  if (typeof conditions !== 'object' || conditions === null) return;

  const keys = Object.keys(conditions);
  const conditionTypes = ['types', 'import', 'require', 'default', 'node', 'browser'];

  // Check if types comes first
  const typesIndex = keys.indexOf('types');
  const importIndex = keys.indexOf('import');
  const requireIndex = keys.indexOf('require');

  if (typesIndex > 0 && (importIndex >= 0 || requireIndex >= 0)) {
    console.log(JSON.stringify({ path: exportPath, type: 'order-error', message: 'types must come before import/require' }));
  } else if (typesIndex === 0) {
    console.log(JSON.stringify({ path: exportPath, type: 'order-ok', message: 'types is first' }));
  }

  // Check each condition
  for (const [key, value] of Object.entries(conditions)) {
    if (typeof value === 'string' && !value.startsWith('.')) continue;
    if (typeof value === 'string') {
      const fullPath = path.join(projectRoot, value);
      const exists = require('fs').existsSync(fullPath);
      console.log(JSON.stringify({ path: exportPath, type: 'condition', condition: key, file: value, exists }));
    } else if (typeof value === 'object') {
      // Nested conditions
      checkCondition(exportPath + ' > ' + key, value);
    }
  }
}

if (typeof p.exports === 'string') {
  const fullPath = path.join(projectRoot, p.exports);
  const exists = require('fs').existsSync(fullPath);
  console.log(JSON.stringify({ path: '.', type: 'direct', file: p.exports, exists }));
} else {
  for (const [key, value] of Object.entries(p.exports)) {
    checkCondition(key, value);
  }
}
" 2>/dev/null | while IFS= read -r line; do
    TYPE=$(echo "$line" | node -e "const d=JSON.parse(require('fs').readFileSync(0,'utf8')); process.stdout.write(d.type)" 2>/dev/null)

    case "$TYPE" in
      direct|condition)
        FILE=$(echo "$line" | node -e "const d=JSON.parse(require('fs').readFileSync(0,'utf8')); process.stdout.write(d.file || '')" 2>/dev/null)
        EXISTS=$(echo "$line" | node -e "const d=JSON.parse(require('fs').readFileSync(0,'utf8')); process.stdout.write(String(d.exists))" 2>/dev/null)
        EPATH=$(echo "$line" | node -e "const d=JSON.parse(require('fs').readFileSync(0,'utf8')); process.stdout.write(d.path || '')" 2>/dev/null)
        COND=$(echo "$line" | node -e "const d=JSON.parse(require('fs').readFileSync(0,'utf8')); process.stdout.write(d.condition || 'entry')" 2>/dev/null)

        if [ "$EXISTS" = "true" ]; then
          check_pass "[$EPATH] $COND → $FILE"
        else
          check_fail "[$EPATH] $COND → $FILE (file does not exist)"
        fi
        ;;
      order-ok)
        check_pass "types condition is first in resolution order"
        ;;
      order-error)
        check_fail "types must come FIRST in exports conditions (before import/require)"
        ;;
    esac
  done
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
