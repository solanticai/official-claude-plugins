#!/usr/bin/env bash
# Anthril — npm Package Audit: Pre-Tool Check for npm availability

# Only check on first Bash invocation per session
CHECK_FLAG="/tmp/.npm-package-audit-check-done"
if [ -f "$CHECK_FLAG" ]; then
  exit 0
fi

# Check for npm
if ! command -v npm &>/dev/null; then
  echo "{\"systemMessage\": \"⚠ npm is not installed or not in PATH. The npm-package-audit skill requires npm to run audit commands. Install Node.js from https://nodejs.org/\"}"
  touch "$CHECK_FLAG"
  exit 0
fi

# Check for node
if ! command -v node &>/dev/null; then
  echo "{\"systemMessage\": \"⚠ Node.js is not installed or not in PATH. The npm-package-audit skill requires Node.js. Install from https://nodejs.org/\"}"
  touch "$CHECK_FLAG"
  exit 0
fi

touch "$CHECK_FLAG"
exit 0
