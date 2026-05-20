#!/usr/bin/env bash
# Anthril — Package Manager Plugin Welcome Hook

PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/../.." && pwd)}"

# Check npm availability
NPM_VERSION=$(npm --version 2>/dev/null)
NODE_VERSION=$(node --version 2>/dev/null)

if [ -n "$NPM_VERSION" ] && [ -n "$NODE_VERSION" ]; then
  ENV_INFO="Environment: Node ${NODE_VERSION}, npm ${NPM_VERSION}"
else
  ENV_INFO="⚠ Warning: npm or Node.js not detected. Some audit features require npm to be installed."
fi

MESSAGE="Anthril — Package Manager plugin loaded. 2 skills available:\n  - npm-package-audit — publishing quality, types, security, CI/CD\n  - cli-ux-audit — terminal UX, help text, errors, output formatting\n\n${ENV_INFO}"

echo "{\"systemMessage\": \"$(echo -e "$MESSAGE" | sed 's/"/\\"/g' | sed ':a;N;$!ba;s/\n/\\n/g')\"}"
