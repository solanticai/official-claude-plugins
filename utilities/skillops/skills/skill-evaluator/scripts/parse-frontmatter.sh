#!/usr/bin/env bash
# Extract the YAML frontmatter block from a SKILL.md file and emit it as JSON.
#
# Usage: parse-frontmatter.sh <path-to-SKILL.md>
# Exit codes:
#   0 — frontmatter parsed successfully
#   1 — file not found
#   2 — no frontmatter present (file does not start with ---)
#   3 — unterminated frontmatter block
#
# Prefers `yq` if available; otherwise falls back to an awk reducer that handles
# the field shapes actually used in this repo (name, description, argument-hint,
# allowed-tools, effort, context, agent, paths, disable-model-invocation, etc).

set -euo pipefail

FILE="${1:-}"
[ -z "$FILE" ] && { echo '{"error":"no-file-argument"}'; exit 1; }
[ ! -f "$FILE" ] && { echo '{"error":"file-not-found"}'; exit 1; }

FIRST_LINE="$(head -1 "$FILE" 2>/dev/null || echo "")"
if [ "$FIRST_LINE" != "---" ]; then
  echo '{"error":"no-frontmatter"}'
  exit 2
fi

# Extract the block between the first two --- delimiters.
FM="$(awk '
  NR==1 && /^---$/ { inblock=1; next }
  inblock && /^---$/ { exit }
  inblock { print }
' "$FILE")"

if [ -z "$FM" ]; then
  echo '{"error":"unterminated-frontmatter"}'
  exit 3
fi

if command -v yq >/dev/null 2>&1; then
  printf '%s\n' "$FM" | yq -o=json -I=0 '.' 2>/dev/null && exit 0
fi

# Awk fallback — handles simple scalars and single-line quoted strings.
printf '%s\n' "$FM" | awk '
  BEGIN { printf "{" ; sep = "" }
  function esc(s) {
    gsub(/\\/, "\\\\", s)
    gsub(/"/, "\\\"", s)
    gsub(/\t/, "\\t", s)
    gsub(/\r/, "", s)
    return s
  }
  /^[[:space:]]*#/ { next }
  /^[[:space:]]*$/ { next }
  /^[^[:space:]].*:/ {
    key = $0
    sub(/:.*$/, "", key)
    gsub(/^[[:space:]]+|[[:space:]]+$/, "", key)
    val = $0
    sub(/^[^:]*:[[:space:]]*/, "", val)
    gsub(/[[:space:]]+$/, "", val)
    if (val ~ /^".*"$/) { gsub(/^"|"$/, "", val) }
    else if (val ~ /^'\''.*'\''$/) { gsub(/^'\''|'\''$/, "", val) }
    printf "%s\"%s\":\"%s\"", sep, esc(key), esc(val)
    sep = ","
  }
  END { printf "}\n" }
'
