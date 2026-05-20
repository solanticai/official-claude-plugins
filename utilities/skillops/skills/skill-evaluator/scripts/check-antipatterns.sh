#!/usr/bin/env bash
# check-antipatterns.sh — emit C41–C45 findings for a skill directory.
#
# Usage:
#   check-antipatterns.sh <target_dir>
#
# Always exits 0; prints a JSON array on stdout, e.g.
#   [
#     {"id":"C41","severity":"warn","file":"SKILL.md","line":42,"evidence":"...","fix":"..."},
#     ...
#   ]
# An empty result emits "[]".
#
# Dependencies: bash, awk, grep, find. No jq required.
#
# C41 — too many options offered
# C42 — scripts punt errors to Claude
# C43 — hook schema non-compliance
# C44 — skills architecture non-compliance
# C45 — over-broad allowed-tools
#
# We deliberately do NOT use `set -e` here — the script runs many best-effort
# regex passes that frequently return non-zero (grep with no match, etc.).
# Strict mode would mask real findings behind pipefail exits.

set -u

TARGET="${1:-}"
if [ -z "$TARGET" ] || [ ! -d "$TARGET" ]; then
  echo "[]"
  exit 0
fi

SKILL_MD=""
if [ -f "$TARGET/SKILL.md" ]; then
  SKILL_MD="$TARGET/SKILL.md"
elif [ -f "$TARGET/skill.md" ]; then
  SKILL_MD="$TARGET/skill.md"
fi

# Buffer findings as bash array of JSON objects.
findings=()

# JSON-escape helper. Escapes backslashes, double-quotes, and control chars.
json_escape() {
  awk 'BEGIN{ ORS="" }
    {
      gsub(/\\/, "\\\\");
      gsub(/"/, "\\\"");
      gsub(/\t/, "\\t");
      gsub(/\r/, "");
      printf "%s%s", (NR==1?"":"\\n"), $0;
    }' <<<"$1"
}

add_finding() {
  # add_finding ID severity file line evidence fix
  local id="$1" sev="$2" file="$3" line="$4" evidence="$5" fix="$6"
  local ev_esc fix_esc file_esc
  ev_esc=$(json_escape "$evidence")
  fix_esc=$(json_escape "$fix")
  file_esc=$(json_escape "$file")
  findings+=("{\"id\":\"${id}\",\"severity\":\"${sev}\",\"file\":\"${file_esc}\",\"line\":${line:-0},\"evidence\":\"${ev_esc}\",\"fix\":\"${fix_esc}\"}")
}

# ---------- C41: too many options ----------
# Heuristic: count AskUserQuestion blocks where >3 "label:" entries appear within
# 40 lines of the AskUserQuestion mention; or numbered-list steps containing
# more than two " or " sequences in a single line.
if [ -n "$SKILL_MD" ]; then
  # Numbered-step "or" overload.
  while IFS=: read -r ln rest; do
    or_count=$(echo "$rest" | grep -oE ' or ' | wc -l | tr -d ' ')
    if [ "${or_count:-0}" -gt 2 ]; then
      add_finding "C41" "warn" "SKILL.md" "$ln" "$rest" "Trim alternatives; collapse to a single recommended path."
    fi
  done < <(grep -nE '^[[:space:]]*[0-9]+\.' "$SKILL_MD" || true)
fi

# ---------- C42: scripts punt errors ----------
while IFS= read -r script; do
  [ -z "$script" ] && continue
  rel="${script#$TARGET/}"
  if ! grep -qE '^[[:space:]]*set[[:space:]]+-[euo]+' "$script"; then
    add_finding "C42" "fail" "$rel" "1" "Script missing 'set -e' or stricter." "Add 'set -euo pipefail' near the top."
  fi
  # echo "error..." followed by exit 0 anywhere in script (allow up to 3 lines between).
  bad_line=$(awk '
    /^[[:space:]]*echo[[:space:]]+["'"'"'][[:space:]]*error/ { armed=NR }
    armed && NR<=armed+3 && /^[[:space:]]*exit[[:space:]]+0[[:space:]]*$/ { print NR; exit }
  ' "$script")
  if [ -n "$bad_line" ]; then
    add_finding "C42" "fail" "$rel" "$bad_line" "Script prints 'error' but exits 0." "Use a non-zero exit code on failure paths."
  fi
done < <(find "$TARGET/scripts" -maxdepth 3 -type f -name '*.sh' 2>/dev/null || true)

# ---------- C43: hook schema ----------
HOOKS_JSON=""
# Hooks may live at <skill>/hooks/hooks.json (skill-local) or at the plugin root.
if [ -f "$TARGET/hooks/hooks.json" ]; then HOOKS_JSON="$TARGET/hooks/hooks.json"; fi

if [ -n "$HOOKS_JSON" ]; then
  rel="${HOOKS_JSON#$TARGET/}"
  # Absolute path detection: any "command": "/..." or "C:\..." literal.
  if grep -nE '"command"[[:space:]]*:[[:space:]]*"(/|[A-Za-z]:[\\/])' "$HOOKS_JSON" >/dev/null; then
    bad_line=$(grep -nE '"command"[[:space:]]*:[[:space:]]*"(/|[A-Za-z]:[\\/])' "$HOOKS_JSON" | head -n 1 | cut -d: -f1)
    add_finding "C43" "fail" "$rel" "$bad_line" "Hook command uses absolute path." "Use \${CLAUDE_PLUGIN_ROOT} relative paths."
  fi
  # Missing timeout: any { "type": "command", "command": ... } without a sibling "timeout".
  if grep -nE '"type"[[:space:]]*:[[:space:]]*"command"' "$HOOKS_JSON" >/dev/null && ! grep -nE '"timeout"' "$HOOKS_JSON" >/dev/null; then
    add_finding "C43" "fail" "$rel" "1" "Command hook missing 'timeout' field." "Add a 'timeout' (seconds) to every command hook."
  fi
  # PreToolUse/PostToolUse without matcher.
  for evt in PreToolUse PostToolUse; do
    if grep -nE "\"${evt}\"" "$HOOKS_JSON" >/dev/null && ! grep -nE '"matcher"' "$HOOKS_JSON" >/dev/null; then
      add_finding "C43" "fail" "$rel" "1" "${evt} hook missing 'matcher'." "Add a tool matcher (e.g. 'Bash', 'Write|Edit')."
    fi
  done
  # Unknown event name.
  while IFS=: read -r ln field; do
    name=$(echo "$field" | sed -nE 's/.*"([A-Za-z]+)"[[:space:]]*:.*/\1/p')
    case "$name" in
      hooks|PreToolUse|PostToolUse|UserPromptSubmit|Stop|SubagentStop|Notification|PreCompact|SessionStart|SessionEnd|"") ;;
      *)
        # Only flag top-level event-like keys; ignore deeper fields.
        if echo "$field" | grep -qE '^[[:space:]]{2,4}"[A-Z][A-Za-z]+"[[:space:]]*:[[:space:]]*\['; then
          add_finding "C43" "warn" "$rel" "$ln" "Unknown hook event: $name" "Use a documented hook event name."
        fi
        ;;
    esac
  done < <(grep -nE '^[[:space:]]+"[A-Z][A-Za-z]+"[[:space:]]*:' "$HOOKS_JSON" || true)
fi

# ---------- C44: skills-architecture ----------
if [ -n "$SKILL_MD" ]; then
  lines=$(awk 'END{print NR}' "$SKILL_MD")
  if [ "$lines" -gt 500 ]; then
    add_finding "C44" "warn" "SKILL.md" "$lines" "SKILL.md is $lines lines (cap 500)." "Extract dense content into reference.md."
  fi
  if [ "$lines" -gt 350 ] && [ ! -f "$TARGET/reference.md" ]; then
    add_finding "C44" "warn" "SKILL.md" "1" "SKILL.md > 350 lines but reference.md absent." "Create a reference.md for dense material."
  fi
fi
if [ ! -d "$TARGET/templates" ]; then
  add_finding "C44" "warn" "templates/" "0" "templates/ directory missing." "Add templates/output-template.md."
fi
if [ ! -d "$TARGET/examples" ]; then
  add_finding "C44" "warn" "examples/" "0" "examples/ directory missing." "Add examples/example-output.md."
fi

# ---------- C45: allowed-tools usage ----------
if [ -n "$SKILL_MD" ]; then
  # Extract allowed-tools value (single line).
  tools_line=$(grep -nE '^allowed-tools:' "$SKILL_MD" | head -n 1 || true)
  if [ -n "$tools_line" ]; then
    ln="${tools_line%%:*}"
    raw="${tools_line#*allowed-tools:}"
    # Strip leading whitespace.
    raw="${raw## }"
    # Tokenise on whitespace, drop arg-scoped parenthetical suffixes.
    # If the skill itself is launched as a subagent (via `agent:` frontmatter
    # or `context: fork`), Agent in allowed-tools is justified by the runtime
    # invocation pattern — exempt it from the unused-tool check.
    agent_field_present=0
    if awk 'NR<=20 && /^(agent|context)[[:space:]]*:/ { print; exit }' "$SKILL_MD" | grep -q .; then
      agent_field_present=1
    fi

    for tok in $raw; do
      base="${tok%%(*}"
      # Only check special / explicit-by-name tools. CRUD tools (Read, Write,
      # Edit, Glob, Grep, Bash) are routinely used by Claude without being
      # named in the body, so flagging them as "unused" produces noise.
      case "$base" in
        Agent|WebFetch|WebSearch|TaskCreate|TaskUpdate|TaskList|NotebookEdit) ;;
        *) continue ;;
      esac
      # Skip Agent when the skill runs in a forked/subagent context.
      if [ "$base" = "Agent" ] && [ "$agent_field_present" = "1" ]; then
        continue
      fi
      if ! awk -v t="$base" 'NR>20 && $0 ~ ("\\<" t "\\>") { found=1; exit } END { exit !found }' "$SKILL_MD" \
         && ! grep -rqE "\\b$base\\b" "$TARGET/scripts" 2>/dev/null; then
        add_finding "C45" "warn" "SKILL.md" "$ln" "Tool '$base' is in allowed-tools but never used." "Remove unused tool from allowed-tools."
      fi
    done
  fi
fi

# ---------- emit JSON array ----------
if [ "${#findings[@]}" -eq 0 ]; then
  echo "[]"
else
  printf '['
  for i in "${!findings[@]}"; do
    if [ "$i" -gt 0 ]; then printf ','; fi
    printf '%s' "${findings[$i]}"
  done
  printf ']\n'
fi
