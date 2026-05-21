#!/usr/bin/env bash
# count-metrics.sh — Count files, SLOC, and language breakdown
# Usage: count-metrics.sh <target_dir>
# Output: JSON to stdout

TARGET="${1:-.}"
TARGET="$(cd "$TARGET" && pwd)"

EXCLUDE_DIRS="node_modules|\.git|dist|build|out|\.next|coverage|__pycache__|\.nyc_output|vendor|\.cache|target|\.turbo|\.vercel"
EXCLUDE_FILES="\.min\.(js|css)|\.map$|\.lock$|\.sum$|package-lock\.json|yarn\.lock|pnpm-lock\.yaml"

count_by_ext() {
  local ext="$1"
  find "$TARGET" -type f -name "*.$ext" 2>/dev/null \
    | grep -vE "$EXCLUDE_DIRS|$EXCLUDE_FILES" \
    | wc -l | tr -d ' '
}

sloc_by_ext() {
  local ext="$1"
  find "$TARGET" -type f -name "*.$ext" 2>/dev/null \
    | grep -vE "$EXCLUDE_DIRS|$EXCLUDE_FILES" \
    | xargs wc -l 2>/dev/null | tail -1 | awk '{print $1}'
}

# File counts
TS_FILES=$(count_by_ext "ts")
TSX_FILES=$(count_by_ext "tsx")
JS_FILES=$(count_by_ext "js")
JSX_FILES=$(count_by_ext "jsx")
MJS_FILES=$(count_by_ext "mjs")
PY_FILES=$(count_by_ext "py")
GO_FILES=$(count_by_ext "go")
RS_FILES=$(count_by_ext "rs")
RB_FILES=$(count_by_ext "rb")
JAVA_FILES=$(count_by_ext "java")
CS_FILES=$(count_by_ext "cs")
PHP_FILES=$(count_by_ext "php")
SQL_FILES=$(count_by_ext "sql")
SH_FILES=$(count_by_ext "sh")
MD_FILES=$(count_by_ext "md")

TOTAL_TS=$((TS_FILES + TSX_FILES))
TOTAL_JS=$((JS_FILES + JSX_FILES + MJS_FILES))

# Total source files (excluding config/docs)
TOTAL_SOURCE_FILES=$(find "$TARGET" -type f \( \
  -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" -o -name "*.mjs" \
  -o -name "*.py" -o -name "*.go" -o -name "*.rs" -o -name "*.rb" \
  -o -name "*.java" -o -name "*.cs" -o -name "*.php" -o -name "*.sql" \
  \) 2>/dev/null | grep -vE "$EXCLUDE_DIRS|$EXCLUDE_FILES" | wc -l | tr -d ' ')

TOTAL_ALL_FILES=$(find "$TARGET" -type f 2>/dev/null \
  | grep -vE "$EXCLUDE_DIRS" | wc -l | tr -d ' ')

# SLOC estimates
TS_SLOC=$(($(sloc_by_ext "ts") + $(sloc_by_ext "tsx")))
JS_SLOC=$(($(sloc_by_ext "js") + $(sloc_by_ext "jsx") + $(sloc_by_ext "mjs")))
PY_SLOC=$(sloc_by_ext "py")
GO_SLOC=$(sloc_by_ext "go")
RS_SLOC=$(sloc_by_ext "rs")

TOTAL_SLOC=$((TS_SLOC + JS_SLOC + PY_SLOC + GO_SLOC + RS_SLOC))

# Largest files
LARGEST_FILES=$(find "$TARGET" -type f \( \
  -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.py" \
  -o -name "*.go" -o -name "*.rs" -o -name "*.rb" -o -name "*.java" \
  \) 2>/dev/null \
  | grep -vE "$EXCLUDE_DIRS|\.min\." \
  | xargs wc -l 2>/dev/null \
  | sort -rn | head -11 | grep -v "total" \
  | awk '{print "{\"lines\":"$1",\"file\":\""$2"\"}"}' \
  | head -10 | tr '\n' ',' | sed 's/,$//')

python3 - <<PYEOF
import json

total_ts = $TOTAL_TS
total_js = $TOTAL_JS
total_py = $PY_FILES
total_go = $GO_FILES
total_rs = $RS_FILES

total_sloc = $TOTAL_SLOC
if total_sloc == 0:
    total_sloc = 1  # avoid div by zero

breakdown = {}
if total_ts > 0: breakdown["TypeScript"] = round((${TS_SLOC} / total_sloc) * 100, 1)
if total_js > 0: breakdown["JavaScript"] = round((${JS_SLOC} / total_sloc) * 100, 1)
if total_py > 0: breakdown["Python"] = round((${PY_SLOC} / total_sloc) * 100, 1)
if total_go > 0: breakdown["Go"] = round((${GO_SLOC} / total_sloc) * 100, 1)
if total_rs > 0: breakdown["Rust"] = round((${RS_SLOC} / total_sloc) * 100, 1)

largest_raw = "$LARGEST_FILES"
try:
    largest = json.loads("[" + largest_raw + "]") if largest_raw else []
except:
    largest = []

print(json.dumps({
    "total_files": $TOTAL_ALL_FILES,
    "source_files": $TOTAL_SOURCE_FILES,
    "sloc": $TOTAL_SLOC,
    "language_breakdown": breakdown,
    "by_language": {
        "TypeScript": {"files": total_ts, "sloc": ${TS_SLOC}},
        "JavaScript": {"files": total_js, "sloc": ${JS_SLOC}},
        "Python": {"files": total_py, "sloc": ${PY_SLOC}},
        "Go": {"files": total_go, "sloc": ${GO_SLOC}},
        "Rust": {"files": total_rs, "sloc": ${RS_SLOC}}
    },
    "largest_files": largest
}, indent=2))
PYEOF
