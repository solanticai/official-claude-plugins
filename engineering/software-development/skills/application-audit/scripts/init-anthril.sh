#!/usr/bin/env bash
# init-anthril.sh — Idempotently scaffold the .anthril/ folder structure under the target project.
# Usage: bash scripts/init-anthril.sh <project-root>
# Output: a short report of what was created/already-existed. Exit 0 unless a write fails.

set -euo pipefail

PROJECT_ROOT="${1:-.}"

if [ ! -d "$PROJECT_ROOT" ]; then
  echo "ERROR: target is not a directory: $PROJECT_ROOT" >&2
  exit 1
fi

cd "$PROJECT_ROOT"

mkdir_if_absent() {
  local dir="$1"
  if [ -d "$dir" ]; then
    echo "  = $dir (existing)"
  else
    mkdir -p "$dir"
    echo "  + $dir (created)"
  fi
}

write_if_absent() {
  local path="$1"
  local content="$2"
  if [ -f "$path" ]; then
    echo "  = $path (existing, untouched)"
  else
    printf '%s\n' "$content" > "$path"
    echo "  + $path (created)"
  fi
}

echo "Scaffolding .anthril/ under $PROJECT_ROOT"

mkdir_if_absent ".anthril"
mkdir_if_absent ".anthril/audits"
mkdir_if_absent ".anthril/audits/latest"
mkdir_if_absent ".anthril/questions"
mkdir_if_absent ".anthril/questions/.resolved"

write_if_absent ".anthril/README.md" "# .anthril/

Managed by the \`software-development:application-audit\` Claude Code skill.

- \`preset-profile.md\` — canonical project profile (regenerated when stale)
- \`audits/<YYYYMMDD-HHMM>/\` — one folder per audit run
- \`audits/latest/\` — mirror of the most recent run
- \`questions/\` — open questions filed by auditors; \`questions/.resolved/\` archives answered ones

Re-run the skill any time. Audit folders accumulate so older runs can be diffed
against newer ones. The skill never modifies application source — it only writes
inside this folder.
"

write_if_absent ".anthril/.gitignore" "# Audit artefacts can stay in git or be gitignored — your choice.
# Default: keep audits + profile, ignore the resolved-question archive.
questions/.resolved/
"

# Non-fatal hint: warn if .anthril/ isn't already covered by the project's gitignore
# but never modify it ourselves (.gitignore touches outside .anthril/ are forbidden).
if [ -f ".gitignore" ] && ! grep -q '^\.anthril' .gitignore 2>/dev/null && ! grep -q '^\.anthril/' .gitignore 2>/dev/null; then
  echo ""
  echo "  ℹ  Hint: .anthril/ is not in your project .gitignore. If you don't want audit"
  echo "     artefacts in git, add '.anthril/' to your .gitignore. The skill will not"
  echo "     modify your .gitignore for you."
fi

echo ""
echo "Done."
exit 0
