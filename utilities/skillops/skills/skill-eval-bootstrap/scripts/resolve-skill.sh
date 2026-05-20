#!/usr/bin/env bash
# resolve-skill.sh — same shape as the harness's resolve-suite.sh, but does
# NOT require an existing evals/suite.yaml (the whole point of bootstrap).
#
# Usage:
#   resolve-skill.sh "<argument>"
#
# Output (key=value):
#   target_dir=<absolute path>
#   skill_name=<basename>
# Or:
#   error=<empty-argument|target-not-found|ambiguous-skill-name>
#   message=<hint>

set -u

ARG="${1:-}"
ARG="${ARG%% --force*}"   # strip a trailing --force flag if present

if [ -z "$ARG" ]; then
  echo "error=empty-argument"
  echo "message=Pass a skill path or bare skill name."
  exit 1
fi

# Direct path?
if [ -d "$ARG" ] && [ -f "$ARG/SKILL.md" ]; then
  ABS=$(cd "$ARG" && pwd)
  echo "target_dir=$ABS"
  echo "skill_name=$(basename "$ABS")"
  exit 0
fi

# Plugin/skill pair?
if [[ "$ARG" == */* ]]; then
  matches=$(find {lifestyle,smb,marketing,engineering,data-science,economics,utilities} -maxdepth 3 -type d -path "*/${ARG%/*}/skills/${ARG##*/}" 2>/dev/null)
  count=$(echo "$matches" | grep -c .)
  if [ "$count" = "1" ]; then
    ABS=$(cd "$matches" && pwd)
    echo "target_dir=$ABS"
    echo "skill_name=$(basename "$ABS")"
    exit 0
  fi
fi

# Bare name search.
matches=$(find {lifestyle,smb,marketing,engineering,data-science,economics,utilities} -maxdepth 4 -type d -name "$ARG" 2>/dev/null | grep '/skills/')
count=$(echo "$matches" | grep -c .)
if [ "$count" = "1" ]; then
  ABS=$(cd "$matches" && pwd)
  echo "target_dir=$ABS"
  echo "skill_name=$(basename "$ABS")"
  exit 0
fi
if [ "$count" -gt 1 ]; then
  echo "error=ambiguous-skill-name"
  echo "message=Multiple skills match '$ARG'."
  echo "candidates=$(echo "$matches" | paste -sd ',' -)"
  exit 1
fi

echo "error=target-not-found"
echo "message=No skill matched '$ARG'."
exit 1
