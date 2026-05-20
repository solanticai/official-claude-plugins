#!/usr/bin/env bash
# Resolve a skill-evaluator target expression to an absolute skill directory.
#
# Accepts:
#   - absolute or relative directory path containing SKILL.md (or skill.md)
#   - absolute or relative path to the SKILL.md file itself
#   - plugin/skill pair (e.g. "skillops/skill-creator")
#   - bare skill name (resolved under plugins/*/skills/<name>/)
#   - empty input — emits a discovery listing and exits 2
#
# Emits key=value lines on stdout:
#   target_dir=<abs>
#   skill_name=<name>
#   plugin_name=<name or "unknown">
# On failure, emits a single `error=<message>` and exits 1.

set -euo pipefail

INPUT="${1:-}"

emit_discovery() {
  echo "error=empty-argument"
  echo "# Discoverable skills:"
  if [ -d "plugins" ]; then
    find plugins -mindepth 3 -maxdepth 3 -type d -path '*/skills/*' 2>/dev/null | sort
  fi
}

if [ -z "$INPUT" ]; then
  emit_discovery
  exit 2
fi

# Normalise backslashes (Windows paths) to forward slashes for regex matching.
NORM="${INPUT//\\//}"

# Strip trailing slashes.
NORM="${NORM%/}"

resolve_from_dir() {
  local dir="$1"
  if [ ! -d "$dir" ]; then return 1; fi
  # Accept SKILL.md or skill.md.
  if [ ! -f "$dir/SKILL.md" ] && [ ! -f "$dir/skill.md" ]; then
    return 1
  fi
  local abs
  abs="$(cd "$dir" && pwd)"
  local skill_name plugin_name
  skill_name="$(basename "$abs")"
  # Plugin is the grandparent's parent under plugins/<plugin>/skills/<skill>.
  local parent grandparent greatgrand
  parent="$(dirname "$abs")"                  # .../skills
  grandparent="$(dirname "$parent")"          # .../plugins/<plugin>
  greatgrand="$(dirname "$grandparent")"      # .../plugins
  if [ "$(basename "$parent")" = "skills" ] && [ "$(basename "$greatgrand")" = "plugins" ]; then
    plugin_name="$(basename "$grandparent")"
  else
    plugin_name="unknown"
  fi
  echo "target_dir=$abs"
  echo "skill_name=$skill_name"
  echo "plugin_name=$plugin_name"
  return 0
}

# Case 1: path to SKILL.md file.
if [ -f "$NORM" ] && [[ "${NORM,,}" =~ skill\.md$ ]]; then
  resolve_from_dir "$(dirname "$NORM")" && exit 0
fi

# Case 2: directory path.
if [ -d "$NORM" ]; then
  resolve_from_dir "$NORM" && exit 0
fi

# Case 3: plugin/skill pair.
if [[ "$NORM" == */* ]]; then
  PLUGIN="${NORM%%/*}"
  SKILL="${NORM#*/}"
  CANDIDATE="plugins/$PLUGIN/skills/$SKILL"
  resolve_from_dir "$CANDIDATE" && exit 0
fi

# Case 4: bare skill name — search.
MATCHES=()
if [ -d "plugins" ]; then
  while IFS= read -r m; do
    MATCHES+=("$m")
  done < <(find plugins -mindepth 3 -maxdepth 3 -type d -name "$NORM" -path '*/skills/*' 2>/dev/null | sort)
fi

if [ "${#MATCHES[@]}" -eq 1 ]; then
  resolve_from_dir "${MATCHES[0]}" && exit 0
elif [ "${#MATCHES[@]}" -gt 1 ]; then
  echo "error=ambiguous-skill-name"
  echo "# Matches:"
  printf '%s\n' "${MATCHES[@]}"
  exit 1
fi

echo "error=target-not-found: $INPUT"
exit 1
