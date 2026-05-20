#!/usr/bin/env bash
# resolve-suite.sh — translate user input into a concrete evals/suite.yaml path.
#
# Usage:
#   resolve-suite.sh "<argument>"
#
# Output (key=value on stdout, one per line):
#   target_dir=<absolute path to skill directory>
#   suite_path=<absolute path to suite.yaml>
#   skill_name=<basename of target_dir>
#
# Or, on failure:
#   error=<empty-argument|no-suite|target-not-found|ambiguous-skill-name>
#   message=<human-readable hint>
#   candidates=<comma-separated list, when applicable>
#
# Exit code:
#   0 — success (target_dir/suite_path/skill_name emitted)
#   1 — error (error=/message= emitted; calling SKILL inspects them)

set -u

ARG="${1:-}"

if [ -z "$ARG" ]; then
  echo "error=empty-argument"
  echo "message=Pass a skill path (e.g. 'utilities/skillops/skills/skill-creator') or a bare skill name."
  exit 1
fi

# Already an absolute or repo-relative path with a suite.yaml present?
if [ -f "$ARG/evals/suite.yaml" ]; then
  ABS=$(cd "$ARG" && pwd)
  echo "target_dir=$ABS"
  echo "suite_path=$ABS/evals/suite.yaml"
  echo "skill_name=$(basename "$ABS")"
  exit 1
fi

# Repo-relative skill dir without suite.
if [ -d "$ARG" ] && [ -f "$ARG/SKILL.md" ]; then
  ABS=$(cd "$ARG" && pwd)
  echo "error=no-suite"
  echo "message=Skill found at $ABS but evals/suite.yaml is missing. Run skill-eval-bootstrap to scaffold one."
  exit 1
fi

# Plugin/skill pair like "skillops/skill-creator".
if [[ "$ARG" == */* && "$ARG" != *.yaml ]]; then
  matches=$(find {lifestyle,smb,marketing,engineering,data-science,economics,utilities} -maxdepth 3 -type d -path "*/${ARG%/*}/skills/${ARG##*/}" 2>/dev/null)
  count=$(echo "$matches" | grep -c .)
  if [ "$count" = "1" ]; then
    ABS=$(cd "$matches" && pwd)
    if [ -f "$ABS/evals/suite.yaml" ]; then
      echo "target_dir=$ABS"
      echo "suite_path=$ABS/evals/suite.yaml"
      echo "skill_name=$(basename "$ABS")"
      exit 0
    fi
    echo "error=no-suite"
    echo "message=Skill found at $ABS but evals/suite.yaml is missing."
    exit 1
  fi
fi

# Bare skill name — search every plugin's skills/.
matches=$(find {lifestyle,smb,marketing,engineering,data-science,economics,utilities} -maxdepth 4 -type d -name "$ARG" 2>/dev/null | grep '/skills/')
count=$(echo "$matches" | grep -c .)
if [ "$count" = "1" ]; then
  ABS=$(cd "$matches" && pwd)
  if [ -f "$ABS/evals/suite.yaml" ]; then
    echo "target_dir=$ABS"
    echo "suite_path=$ABS/evals/suite.yaml"
    echo "skill_name=$(basename "$ABS")"
    exit 0
  fi
  echo "error=no-suite"
  echo "message=Skill found at $ABS but evals/suite.yaml is missing."
  exit 1
fi
if [ "$count" -gt 1 ]; then
  echo "error=ambiguous-skill-name"
  echo "message=Multiple skills match '$ARG'. Disambiguate with plugin/skill form."
  echo "candidates=$(echo "$matches" | paste -sd ',' -)"
  exit 1
fi

echo "error=target-not-found"
echo "message=No skill matched '$ARG'. Try a path or run with no args to discover."
exit 1
