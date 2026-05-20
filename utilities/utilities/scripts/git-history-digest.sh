#!/usr/bin/env bash
# git-history-digest.sh — Structured JSON-style digest of git log between two refs.
#
# Usage:
#   bash git-history-digest.sh <from-ref> <to-ref>
#   bash git-history-digest.sh v1.2.0 HEAD
#
# Output: tab-separated lines per commit, plus a summary header.

set -e

FROM="${1:-HEAD~20}"
TO="${2:-HEAD}"

if ! git rev-parse "$FROM" >/dev/null 2>&1; then
  echo "ERROR: ref '$FROM' not found" >&2
  exit 1
fi

if ! git rev-parse "$TO" >/dev/null 2>&1; then
  echo "ERROR: ref '$TO' not found" >&2
  exit 1
fi

COMMIT_COUNT=$(git rev-list --count "$FROM".."$TO")
echo "# Git History Digest"
echo "# From: $FROM"
echo "# To:   $TO"
echo "# Commits: $COMMIT_COUNT"
echo

if [ "$COMMIT_COUNT" -eq 0 ]; then
  echo "# (no commits)"
  exit 0
fi

# Conventional-commits classification — count by type
echo "## Counts by conventional-commit type"
git log "$FROM".."$TO" --pretty='%s' | grep -oE '^(feat|fix|docs|chore|refactor|perf|test|build|ci|style|revert)(\([^)]+\))?!?:' | sort | uniq -c | sort -rn
echo

# Files changed summary
echo "## Files changed"
git diff --name-only "$FROM".."$TO" | sort -u | wc -l | awk '{printf "Total unique files changed: %s\n", $1}'
echo

# Commit list (subject only, oldest first)
echo "## Commits (chronological)"
echo
git log --reverse "$FROM".."$TO" --pretty='%h%x09%ad%x09%s' --date=short
echo

# Breaking changes
echo
echo "## Breaking changes"
BREAKING=$(git log "$FROM".."$TO" --grep='BREAKING' --pretty='%h %s')
if [ -z "$BREAKING" ]; then
  echo "(none detected via BREAKING marker or \"!:\" suffix in subject)"
else
  echo "$BREAKING"
fi
