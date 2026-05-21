#!/usr/bin/env bash
# detect-test-posture.sh — Detect test framework, file counts, and coverage config
# Usage: detect-test-posture.sh <target_dir>
# Output: JSON to stdout

TARGET="${1:-.}"
TARGET="$(cd "$TARGET" && pwd)"

EXCLUDE="node_modules|\.git|dist|build|out|\.next|__pycache__|coverage|\.nyc_output"

# Test framework detection
FRAMEWORK="none"
E2E_FRAMEWORK="none"

[[ -n "$(find "$TARGET" -maxdepth 3 -name "jest.config.*" 2>/dev/null | grep -v node_modules | head -1)" ]] && FRAMEWORK="Jest"
[[ -n "$(find "$TARGET" -maxdepth 3 -name "vitest.config.*" 2>/dev/null | grep -v node_modules | head -1)" ]] && FRAMEWORK="Vitest"
[[ -n "$(find "$TARGET" -maxdepth 3 -name ".mocharc*" 2>/dev/null | grep -v node_modules | head -1)" ]] && FRAMEWORK="Mocha"
[[ -n "$(find "$TARGET" -maxdepth 3 -name "pytest.ini" -o -name "conftest.py" 2>/dev/null | grep -v node_modules | head -1)" ]] && FRAMEWORK="Pytest"
[[ -n "$(find "$TARGET" -maxdepth 4 -name "*_test.go" 2>/dev/null | head -1)" ]] && FRAMEWORK="Go testing"
[[ -n "$(find "$TARGET" -maxdepth 3 -name "*.test.rs" 2>/dev/null | head -1)" ]] || \
  grep -rl "#\[test\]" "$TARGET/src" 2>/dev/null | head -1 | grep -q . && FRAMEWORK="Rust testing"

# E2E framework
[[ -n "$(find "$TARGET" -maxdepth 3 -name "cypress.config.*" 2>/dev/null | grep -v node_modules | head -1)" ]] && E2E_FRAMEWORK="Cypress"
[[ -n "$(find "$TARGET" -maxdepth 3 -name "playwright.config.*" 2>/dev/null | grep -v node_modules | head -1)" ]] && E2E_FRAMEWORK="Playwright"

# Test file counts
TEST_FILES=$(find "$TARGET" -type f \( \
  -name "*.test.ts" -o -name "*.test.tsx" -o -name "*.test.js" -o -name "*.test.jsx" \
  -o -name "*.spec.ts" -o -name "*.spec.tsx" -o -name "*.spec.js" -o -name "*.spec.jsx" \
  -o -name "*_test.go" -o -name "test_*.py" -o -name "*_test.py" \
  \) 2>/dev/null | grep -vE "$EXCLUDE" | wc -l | tr -d ' ')

# Source files (non-test)
SOURCE_FILES=$(find "$TARGET/src" -type f \( \
  -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" \
  -o -name "*.py" -o -name "*.go" -o -name "*.rs" \
  \) 2>/dev/null \
  | grep -vE "\.test\.|\.spec\.|_test\.|test_\.|$EXCLUDE" \
  | wc -l | tr -d ' ')
# Fallback if no src/
if [[ "$SOURCE_FILES" == "0" ]]; then
  SOURCE_FILES=$(find "$TARGET" -maxdepth 4 -type f \( \
    -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" \
    \) 2>/dev/null \
    | grep -vE "\.test\.|\.spec\.|$EXCLUDE" \
    | wc -l | tr -d ' ')
fi

# Coverage config
COVERAGE_CONFIG="false"
find "$TARGET" -maxdepth 3 \( \
  -name "jest.config.*" -o -name "vitest.config.*" -o -name ".nycrc*" \
  -o -name "pytest.ini" -o -name "pyproject.toml" \
  \) 2>/dev/null | grep -v node_modules | head -1 | grep -q . && COVERAGE_CONFIG="true"

# Coverage report
COVERAGE_REPORT="none"
COVERAGE_PCT="null"
COVERAGE_FILE=$(find "$TARGET" -maxdepth 4 \
  -name "coverage-summary.json" \
  -o -name "lcov.info" \
  -o -name ".coverage" \
  2>/dev/null | grep -v node_modules | head -1)

if [[ -n "$COVERAGE_FILE" ]]; then
  COVERAGE_REPORT="$COVERAGE_FILE"
  if [[ "$COVERAGE_FILE" == *"coverage-summary.json" ]]; then
    COVERAGE_PCT=$(python3 -c "
import json
try:
    with open('$COVERAGE_FILE') as f:
        data = json.load(f)
    total = data.get('total', {})
    pct = total.get('lines', {}).get('pct')
    print(pct if pct is not None else 'null')
except:
    print('null')
" 2>/dev/null || echo "null")
  fi
fi

python3 - <<PYEOF
import json

test_files = $TEST_FILES
source_files = $SOURCE_FILES
ratio = round(test_files / max(source_files, 1), 2)

print(json.dumps({
    "framework": "$FRAMEWORK",
    "e2e_framework": "$E2E_FRAMEWORK",
    "test_file_count": test_files,
    "source_file_count": source_files,
    "test_to_source_ratio": ratio,
    "coverage_config_present": $COVERAGE_CONFIG,
    "coverage_report": "$COVERAGE_REPORT",
    "coverage_pct": $COVERAGE_PCT
}, indent=2))
PYEOF
