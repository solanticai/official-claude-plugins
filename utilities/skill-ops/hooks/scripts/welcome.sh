#!/usr/bin/env bash
# Anthril — SkillOps Plugin Welcome Hook

MESSAGE="Anthril — SkillOps plugin loaded. 2 skills available:\n  - skill-creator\n  - skill-evaluator\n\nUse /skill-creator [skill-name-and-purpose] to scaffold a new Claude Code skill.\nUse /skill-evaluator [skill-path-or-name] to audit an existing skill for quality."

echo "{\"systemMessage\": \"$(echo -e "$MESSAGE" | sed 's/"/\\"/g' | sed ':a;N;$!ba;s/\n/\\n/g')\"}"
