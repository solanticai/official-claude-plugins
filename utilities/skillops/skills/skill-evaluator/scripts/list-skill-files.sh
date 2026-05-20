#!/usr/bin/env bash
# Enumerate every file under a skill directory with size and line count.
#
# Usage: list-skill-files.sh <skill-dir>
# Emits: one JSON object per line: { "path": <rel>, "size": N, "lines": N }

set -euo pipefail

DIR="${1:-}"
[ -z "$DIR" ] && { echo "usage: list-skill-files.sh <skill-dir>" >&2; exit 1; }
[ ! -d "$DIR" ] && { echo "error: not a directory: $DIR" >&2; exit 1; }

# Portable across Git Bash on Windows and Linux CI runners.
find "$DIR" -type f -not -path '*/.*' | while IFS= read -r f; do
  rel="${f#"$DIR"/}"
  size=$(wc -c < "$f" 2>/dev/null | tr -d '[:space:]' || echo 0)
  lines=$(wc -l < "$f" 2>/dev/null | tr -d '[:space:]' || echo 0)
  # Escape backslashes and quotes for JSON safety.
  esc_rel="${rel//\\/\\\\}"
  esc_rel="${esc_rel//\"/\\\"}"
  printf '{"path":"%s","size":%s,"lines":%s}\n' "$esc_rel" "$size" "$lines"
done
