#!/usr/bin/env bash
# extract-error-codes.sh — list every `error=<code>` literal the skill's
# scripts emit, deduped.
#
# Usage:
#   extract-error-codes.sh <target_dir>
#
# Output: one code per line on stdout. Empty if none found.

set -u

TARGET="${1:-}"
if [ ! -d "$TARGET/scripts" ]; then
  exit 0
fi

grep -rhoE 'error=[a-z][a-z0-9-]+' "$TARGET/scripts" 2>/dev/null \
  | sed 's/^error=//' \
  | sort -u
