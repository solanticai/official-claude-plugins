#!/usr/bin/env bash
# check-activation.sh — FAST-MODE-ONLY deterministic activation classifier.
#
# Usage:
#   check-activation.sh <target_dir> <user_input>
#
# Output (key=value):
#   verdict=true|false
#   reason=<short string>
#
# This is the harness's `--mode=fast` fallback. The default `--mode=full`
# path uses an Agent invocation against templates/activation-prompt-template.md
# (canonical implementation: a fresh Claude subagent reads the skill's
# description + paths and the user input, then returns a structured
# verdict). That path is implemented in the harness SKILL.md, not here —
# this script intentionally remains a deterministic proxy.
#
# Approximation strategy:
#   1. Tokenise the skill's `description` and `name` fields.
#   2. Tokenise the user_input.
#   3. Compute keyword overlap.
#   4. Return true if ≥ 2 content tokens overlap, otherwise false.
# It also returns true if the input contains the skill name as a token.
#
# Known limitations of the fast mode:
#   - Cannot distinguish paraphrased queries that share zero keywords with
#     the description (semantic similarity is not captured).
#   - Treats every keyword equally — no weighting by specificity.
# Use --mode=full for accuracy; use this for speed.

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
