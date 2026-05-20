#!/usr/bin/env bash
# Anthril — Business Economics Plugin Welcome Hook

PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/../.." && pwd)}"
SKILLS_DIR="$PLUGIN_ROOT/skills"

# Count skills
SKILL_COUNT=0
SKILL_LIST=""
WARNINGS=""

if [ -d "$SKILLS_DIR" ]; then
  for skill_dir in "$SKILLS_DIR"/*/; do
    skill_file=""
    if [ -f "${skill_dir}SKILL.md" ]; then
      skill_file="${skill_dir}SKILL.md"
    elif [ -f "${skill_dir}skill.md" ]; then
      skill_file="${skill_dir}skill.md"
    fi

    if [ -n "$skill_file" ]; then
      SKILL_COUNT=$((SKILL_COUNT + 1))
      skill_name=$(basename "$skill_dir")
      SKILL_LIST="${SKILL_LIST}\n  - ${skill_name}"

      line_count=$(wc -l < "$skill_file" 2>/dev/null || echo 0)
      if [ "$line_count" -gt 500 ]; then
        WARNINGS="${WARNINGS}\n  ⚠ ${skill_name}: ${line_count} lines (exceeds 500-line limit — extract to reference.md)"
      elif [ "$line_count" -gt 450 ]; then
        WARNINGS="${WARNINGS}\n  ⚡ ${skill_name}: ${line_count} lines (approaching 500-line limit)"
      fi
    fi
  done
fi

MESSAGE="Anthril — Business Economics plugin loaded. ${SKILL_COUNT} skills available:${SKILL_LIST}"

if [ -n "$WARNINGS" ]; then
  MESSAGE="${MESSAGE}\n\nQuality warnings:${WARNINGS}"
fi

echo "{\"systemMessage\": \"$(echo -e "$MESSAGE" | sed 's/"/\\"/g' | sed ':a;N;$!ba;s/\n/\\n/g')\"}"
