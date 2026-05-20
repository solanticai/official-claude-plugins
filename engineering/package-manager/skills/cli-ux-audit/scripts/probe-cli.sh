#!/usr/bin/env bash
set -euo pipefail
# probe-cli.sh
#
# Run a CLI through a standard battery of invocations and capture stdout,
# stderr, and exit code for each. Seeds most findings in Phases 2-4.
#
# Usage:
#   probe-cli.sh <binary> [outdir]
#
# Default outdir is ./.cli-ux-audit/probes

set -u

BIN="${1:-}"
OUTDIR="${2:-./.cli-ux-audit/probes}"

if [ -z "$BIN" ]; then
  echo "usage: probe-cli.sh <binary> [outdir]" >&2
  exit 2
fi

if ! command -v "$BIN" >/dev/null 2>&1 && [ ! -x "$BIN" ]; then
  echo "error: '$BIN' is not on PATH and is not an executable file" >&2
  exit 66
fi

mkdir -p "$OUTDIR"

run_probe() {
  local name="$1"; shift
  local stdout="$OUTDIR/$name.stdout"
  local stderr="$OUTDIR/$name.stderr"
  local exitfile="$OUTDIR/$name.exit"
  "$@" >"$stdout" 2>"$stderr"
  echo $? >"$exitfile"
  printf "%-28s exit=%s  stdout=%sb  stderr=%sb\n" \
    "$name" \
    "$(cat "$exitfile")" \
    "$(wc -c <"$stdout" | tr -d ' ')" \
    "$(wc -c <"$stderr" | tr -d ' ')"
}

echo "Probing '$BIN' — artefacts in $OUTDIR"
echo

run_probe "help-long"     "$BIN" --help
run_probe "help-short"    "$BIN" -h
run_probe "help-sub"      "$BIN" help
run_probe "version"       "$BIN" --version
run_probe "no-args"       "$BIN"
run_probe "bad-flag"      "$BIN" --definitely-not-a-real-flag
run_probe "bad-command"   "$BIN" definitely-not-a-real-subcommand
run_probe "help-narrow"   env COLUMNS=40 "$BIN" --help
run_probe "help-nocolor"  env NO_COLOR=1 "$BIN" --help

echo
echo "Done. Inspect $OUTDIR/*.{stdout,stderr,exit}."
