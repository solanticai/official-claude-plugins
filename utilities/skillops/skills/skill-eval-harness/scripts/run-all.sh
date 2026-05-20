#!/usr/bin/env bash
# run-all.sh — print every evals/suite.yaml in the repo as a JSON array.
#
# Usage:
#   run-all.sh
#
# The SKILL.md then iterates the list. This script just produces the
# discovery output deterministically so it is testable in isolation.

set -u

paths=$(find lifestyle smb marketing engineering data-science economics utilities \
  -maxdepth 5 -type f -name 'suite.yaml' -path '*/evals/suite.yaml' 2>/dev/null \
  | sort)

if [ -z "$paths" ]; then
  echo '{"suites":[],"count":0}'
  exit 0
fi

node -e '
const fs = require("node:fs");
const paths = process.argv[1].split("\n").filter(Boolean);
const suites = paths.map(p => {
  const skill = p.split("/").slice(-3, -2)[0];   // <skill>/evals/suite.yaml
  const plugin = p.split("/").slice(-5, -4)[0];  // <plugin>/skills/...
  const category = p.split("/")[0];
  return { path: p, category, plugin, skill };
});
console.log(JSON.stringify({suites, count: suites.length}, null, 2));
' "$paths"
