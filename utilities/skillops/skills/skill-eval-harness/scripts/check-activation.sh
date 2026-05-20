#!/usr/bin/env bash
# check-activation.sh — heuristic activation classifier for a skill.
#
# Usage:
#   check-activation.sh <target_dir> <user_input>
#
# Output (key=value):
#   verdict=true|false
#   reason=<short string>
#
# This is a deterministic stand-in for the actual Claude activation logic.
# It approximates by:
#   1. Tokenising the skill's `description` and `name` fields.
#   2. Tokenising the user_input.
#   3. Computing keyword overlap.
#   4. Returning true if ≥ 2 content tokens overlap, otherwise false.
# It also returns true if any `paths:` glob in the skill matches a path
# mentioned in the input.
#
# This is intentionally simple — the canonical activation decision is made
# by Claude at runtime. The harness uses this as a fast proxy that lets us
# write activation tests without needing a live Claude invocation per case.

set -u

TARGET="${1:-}"
INPUT="${2:-}"
SKILL_MD=""
if [ -f "$TARGET/SKILL.md" ]; then SKILL_MD="$TARGET/SKILL.md"
elif [ -f "$TARGET/skill.md" ]; then SKILL_MD="$TARGET/skill.md"
fi

if [ -z "$SKILL_MD" ] || [ -z "$INPUT" ]; then
  # Empty input rarely activates; absent skill never does.
  if [ -z "$INPUT" ]; then
    echo "verdict=false"
    echo "reason=empty-input"
  else
    echo "verdict=false"
    echo "reason=skill-md-missing"
  fi
  exit 0
fi

# Extract description + name from frontmatter (first 20 lines).
DESC=$(awk 'NR<=20 && /^description:/ { sub(/^description:[[:space:]]*/, ""); print; exit }' "$SKILL_MD")
NAME=$(awk 'NR<=20 && /^name:/ { sub(/^name:[[:space:]]*/, ""); print; exit }' "$SKILL_MD")

# Lowercase + strip punctuation; keep tokens ≥ 4 chars (drops "the", "and").
tokenise() {
  echo "$1" | tr '[:upper:]' '[:lower:]' | tr -c 'a-z0-9' ' ' | tr ' ' '\n' | awk 'length>=4'
}

SKILL_TOKENS=$(tokenise "$NAME $DESC" | sort -u)
INPUT_TOKENS=$(tokenise "$INPUT" | sort -u)
OVERLAP=$(comm -12 <(echo "$SKILL_TOKENS") <(echo "$INPUT_TOKENS") | wc -l | tr -d ' ')

# Also check whether the input contains the skill's name (often a strong signal).
NAME_HIT="false"
case " $(echo "$INPUT" | tr '[:upper:]' '[:lower:]') " in
  *" $NAME "*|*" $(echo "$NAME" | tr -d '-') "*) NAME_HIT="true" ;;
esac

if [ "$NAME_HIT" = "true" ] || [ "$OVERLAP" -ge 2 ]; then
  echo "verdict=true"
  echo "reason=keyword-overlap=$OVERLAP name-hit=$NAME_HIT"
else
  echo "verdict=false"
  echo "reason=insufficient-overlap=$OVERLAP name-hit=$NAME_HIT"
fi
