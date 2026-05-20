#!/usr/bin/env bash
# diff-runs.sh — compare two run JSON sidecars and emit regression/win JSON.
#
# Usage:
#   diff-runs.sh <prev.json> <current.json>
#
# Output JSON on stdout:
#   { "new_failures": [...], "new_passes": [...], "unchanged": N, "new_cases": [...] }
#
# Matches cases by `id`. A "new_failure" is a case that was pass in prev and
# is fail/partial in current. A "new_pass" is the reverse. "new_cases" are
# case IDs present in current but not prev.
#
# Exit codes:
#   0 — diff emitted
#   1 — bad input

set -u

PREV="${1:-}"
CUR="${2:-}"
if [ ! -f "$PREV" ] || [ ! -f "$CUR" ]; then
  echo "{\"error\":\"missing-input\",\"prev\":\"$PREV\",\"current\":\"$CUR\"}" >&2
  exit 1
fi

node -e '
const fs = require("node:fs");
const prev = JSON.parse(fs.readFileSync(process.argv[1], "utf8"));
const cur  = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
const prevMap = Object.fromEntries((prev.results || []).map(r => [r.id, r]));
const curMap  = Object.fromEntries((cur.results  || []).map(r => [r.id, r]));

const new_failures = [], new_passes = [], unchanged = [];
const new_cases = [];

for (const id of Object.keys(curMap)) {
  const c = curMap[id];
  const p = prevMap[id];
  if (!p) { new_cases.push(id); continue; }
  const pPass = p.verdict === "pass";
  const cPass = c.verdict === "pass";
  if (pPass && !cPass)      new_failures.push({id, prev: p.verdict, current: c.verdict});
  else if (!pPass && cPass) new_passes.push({id, prev: p.verdict, current: c.verdict});
  else                       unchanged.push(id);
}

console.log(JSON.stringify({
  new_failures,
  new_passes,
  unchanged: unchanged.length,
  new_cases
}, null, 2));
' "$PREV" "$CUR"
