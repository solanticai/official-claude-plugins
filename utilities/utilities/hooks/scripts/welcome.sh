#!/usr/bin/env bash
# Anthril — Utilities Plugin Welcome Hook

MESSAGE="Anthril — Utilities plugin loaded.\n\nGeneric utility skills:\n  - plan-completion-audit\n\nUse /plan-completion-audit [path-to-project-root-or-plan-file] to audit plan versus implementation."

echo "{\"systemMessage\": \"$(echo -e "$MESSAGE" | sed 's/"/\\"/g' | sed ':a;N;$!ba;s/\n/\\n/g')\"}"
