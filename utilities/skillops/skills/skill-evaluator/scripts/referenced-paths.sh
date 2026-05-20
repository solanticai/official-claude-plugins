#!/usr/bin/env bash
# Extract local file references from a SKILL.md — markdown links, code-fence
# paths, and inline backtick paths that point at sibling files within the skill
# directory.
#
# Usage: referenced-paths.sh <path-to-SKILL.md>
# Emits: one path per line, relative to the skill directory.
#
# Strips URLs (http/https/mailto), anchors (#section), and absolute paths. Used
# by the evaluator to verify every referenced file actually exists on disk.

set -euo pipefail

FILE="${1:-}"
[ -z "$FILE" ] && { echo "usage: referenced-paths.sh <path>" >&2; exit 1; }
[ ! -f "$FILE" ] && { echo "error: not found: $FILE" >&2; exit 1; }

awk '
  BEGIN { in_code = 0 }
  /^```/ { in_code = !in_code; next }

  # Markdown link targets: ](path)
  {
    line = $0
    while (match(line, /\]\([^)]+\)/)) {
      token = substr(line, RSTART + 2, RLENGTH - 3)
      print token
      line = substr(line, RSTART + RLENGTH)
    }
  }

  # Relative-looking tokens in code fences or backticks (e.g. `scripts/foo.sh`)
  in_code == 1 || /`/ {
    # Collapse backticks for pattern scanning.
    txt = $0
    while (match(txt, /`[^`]+`/)) {
      tok = substr(txt, RSTART + 1, RLENGTH - 2)
      # Heuristic: token contains a slash or a known skill filename.
      if (tok ~ /\// || tok ~ /^(SKILL|skill|LICENSE|reference)\.(md|txt)$/) {
        print tok
      }
      txt = substr(txt, RSTART + RLENGTH)
    }
  }
' "$FILE" \
  | awk '
      # Drop URLs, mailtos, anchors-only, and empties.
      /^https?:\/\// { next }
      /^mailto:/ { next }
      /^#/ { next }
      /^$/ { next }
      {
        p = $0
        sub(/#.*$/, "", p)          # strip anchor
        sub(/[[:space:]].*$/, "", p) # strip trailing description after whitespace
        if (p ~ /^\.\.?\//) sub(/^\.\//, "", p)
        if (p ~ /^\//) next         # drop absolute paths
        if (p == "") next
        print p
      }
    ' \
  | sort -u
