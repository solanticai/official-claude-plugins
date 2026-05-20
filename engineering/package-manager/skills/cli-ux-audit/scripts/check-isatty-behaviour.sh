#!/usr/bin/env bash
set -euo pipefail
# check-isatty-behaviour.sh
#
# Compare a CLI's output when attached to a TTY vs when piped to a file.
# A well-behaved CLI strips ANSI escapes, spinners, and cursor control
# when stdout is not a TTY.
#
# Usage:
#   check-isatty-behaviour.sh <binary> [args...]
#
# Example:
#   check-isatty-behaviour.sh gh issue list

set -u

BIN="${1:-}"
shift || true

if [ -z "$BIN" ]; then
  echo "usage: check-isatty-behaviour.sh <binary> [args...]" >&2
  exit 2
fi

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

TTY_OUT="$TMP/tty.out"
PIPE_OUT="$TMP/pipe.out"
NOCOLOR_OUT="$TMP/nocolor.out"

# Pipe to file — this is the non-TTY case.
"$BIN" "$@" >"$PIPE_OUT" 2>/dev/null || true

# NO_COLOR override — should also strip ANSI even if isatty check is missing.
NO_COLOR=1 "$BIN" "$@" >"$NOCOLOR_OUT" 2>/dev/null || true

# TTY case — approximate by running via `script` (macOS and Linux both have it).
if command -v script >/dev/null 2>&1; then
  if [ "$(uname)" = "Darwin" ]; then
    script -q "$TTY_OUT" "$BIN" "$@" >/dev/null 2>&1 || true
  else
    script -q -c "$BIN $*" "$TTY_OUT" >/dev/null 2>&1 || true
  fi
else
  echo "note: 'script' not available — skipping TTY capture" >&2
  TTY_OUT="/dev/null"
fi

count_ansi() {
  # Count ANSI escape sequences in a file.
  grep -ac $'\x1b\\[' "$1" 2>/dev/null || echo 0
}

PIPE_ANSI=$(count_ansi "$PIPE_OUT")
NOCOLOR_ANSI=$(count_ansi "$NOCOLOR_OUT")
TTY_ANSI=$(count_ansi "$TTY_OUT")

printf "ANSI escape counts:\n"
printf "  piped stdout      : %s\n" "$PIPE_ANSI"
printf "  NO_COLOR=1        : %s\n" "$NOCOLOR_ANSI"
printf "  TTY (via script)  : %s\n" "$TTY_ANSI"
echo

VERDICT_PIPE="pass"
VERDICT_NOCOLOR="pass"

if [ "$PIPE_ANSI" -gt 0 ]; then
  VERDICT_PIPE="FAIL — leaks ANSI on pipe"
fi
if [ "$NOCOLOR_ANSI" -gt 0 ]; then
  VERDICT_NOCOLOR="FAIL — ignores NO_COLOR"
fi

printf "Piped isatty check : %s\n" "$VERDICT_PIPE"
printf "NO_COLOR check     : %s\n" "$VERDICT_NOCOLOR"

if [ "$VERDICT_PIPE" != "pass" ] || [ "$VERDICT_NOCOLOR" != "pass" ]; then
  exit 1
fi
