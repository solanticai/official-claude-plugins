#!/usr/bin/env bash
# extract-triggers.sh — emit JSON with description / name / argument-hint / paths
# from a skill's SKILL.md frontmatter.
#
# Usage:
#   extract-triggers.sh <target_dir>
#
# Output JSON on stdout:
#   { "name": "...", "description": "...", "argument_hint": "...", "paths": [...] }

set -u

TARGET="${1:-}"
SKILL_MD="$TARGET/SKILL.md"
[ ! -f "$SKILL_MD" ] && SKILL_MD="$TARGET/skill.md"
if [ ! -f "$SKILL_MD" ]; then
  echo "{\"error\":\"skill-md-missing\"}" >&2
  exit 1
fi

node -e '
const fs = require("node:fs");
const raw = fs.readFileSync(process.argv[1], "utf8").replace(/\r\n/g, "\n").replace(/^﻿/, "");
const fmMatch = raw.match(/^---\n([\s\S]*?)\n---/);
const text = raw;
if (!fmMatch) { console.log("{}"); process.exit(0); }
const lines = fmMatch[1].split("\n");
const fm = {};
let cur = null;
let pathsList = [];
let inPaths = false;
for (const raw of lines) {
  const line = raw.replace(/\r$/, "");
  if (inPaths) {
    const m = line.match(/^\s+-\s+(.+)$/);
    if (m) { pathsList.push(m[1].replace(/^["'\'']|["'\'']$/g, "")); continue; }
    inPaths = false;
  }
  const kv = line.match(/^([a-zA-Z_-]+):\s*(.*)$/);
  if (!kv) continue;
  const [, k, v] = kv;
  if (k === "paths" && v.trim() === "") { inPaths = true; continue; }
  fm[k] = v.replace(/^["'\'']|["'\'']$/g, "").trim();
}
const out = {
  name: fm.name || "",
  description: fm.description || "",
  argument_hint: fm["argument-hint"] || "",
  paths: pathsList
};
console.log(JSON.stringify(out));
' "$SKILL_MD"
