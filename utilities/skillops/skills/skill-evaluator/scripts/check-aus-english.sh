#!/usr/bin/env bash
# Report American spellings found in narrative markdown (outside fenced code
# blocks). Emits one finding per line as tab-separated: path<TAB>line<TAB>word.
#
# Usage: check-aus-english.sh <file-or-dir>
#
# The common-words list matches the spellings the Anthril CLAUDE.md flags as
# Australian-English violations. Code blocks (``` fences) are skipped so that
# function names and shell tokens (e.g. `normalize()`, `color=red`) do not fire.

set -euo pipefail

TARGET="${1:-}"
[ -z "$TARGET" ] && { echo "usage: check-aus-english.sh <file-or-dir>" >&2; exit 1; }

# Case-insensitive word boundaries; targeted list only — avoids false positives
# such as "license" (legal use is acceptable in both dialects).
PATTERN='\b(color|colors|behavior|behaviors|analyze|analyzing|analyzes|organize|organized|organizing|optimize|optimized|optimizing|catalog|center|centered|favorite|favorites|labor|defense|defenses|realize|realized|realizing|harbor|flavor|armor|humor|rumor|neighbor|neighbors|traveler|traveling|modeling)\b'

process_file() {
  local f="$1"
  [[ "$f" != *.md ]] && return 0
  awk -v FILE="$f" -v PAT="$PATTERN" '
    BEGIN { IGNORECASE = 1; in_code = 0 }
    /^```/ { in_code = !in_code; next }
    !in_code {
      if (match($0, PAT)) {
        hit = substr($0, RSTART, RLENGTH)
        printf "%s\t%d\t%s\n", FILE, NR, hit
      }
    }
  ' "$f"
}

if [ -d "$TARGET" ]; then
  while IFS= read -r -d '' f; do
    process_file "$f"
  done < <(find "$TARGET" -type f -name '*.md' -print0)
else
  process_file "$TARGET"
fi
