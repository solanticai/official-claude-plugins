#!/usr/bin/env bash
# detect-cli-framework.sh
#
# Inspect a project directory and guess which CLI framework is in use.
# Prints one line: "<language> <framework>"
#
# Usage:
#   detect-cli-framework.sh <path-to-project>

set -euo pipefail

DIR="${1:-.}"

if [ ! -d "$DIR" ]; then
  echo "error: $DIR is not a directory" >&2
  exit 2
fi

cd "$DIR"

detect_node() {
  [ -f package.json ] || return 1
  local pkg
  pkg=$(cat package.json)
  case "$pkg" in
    *'"@oclif/core"'*|*'"@oclif/command"'*) echo "node oclif"; return 0 ;;
    *'"commander"'*) echo "node commander"; return 0 ;;
    *'"yargs"'*) echo "node yargs"; return 0 ;;
    *'"meow"'*) echo "node meow"; return 0 ;;
    *'"cac"'*) echo "node cac"; return 0 ;;
    *'"sade"'*) echo "node sade"; return 0 ;;
  esac
  # bin present but no known framework
  case "$pkg" in
    *'"bin"'*) echo "node raw"; return 0 ;;
  esac
  return 1
}

detect_python() {
  { [ -f pyproject.toml ] || [ -f setup.py ] || [ -f setup.cfg ]; } || return 1
  local content=""
  [ -f pyproject.toml ] && content+=$(cat pyproject.toml)
  [ -f setup.py ] && content+=$(cat setup.py)
  [ -f setup.cfg ] && content+=$(cat setup.cfg)
  case "$content" in
    *typer*) echo "python typer"; return 0 ;;
    *click*) echo "python click"; return 0 ;;
    *docopt*) echo "python docopt"; return 0 ;;
    *fire*) echo "python fire"; return 0 ;;
    *argparse*) echo "python argparse"; return 0 ;;
  esac
  # scripts entry but no known framework
  case "$content" in
    *'[project.scripts]'*|*'entry_points'*|*'console_scripts'*) echo "python raw"; return 0 ;;
  esac
  return 1
}

detect_go() {
  [ -f go.mod ] || return 1
  if grep -rq "github.com/spf13/cobra" . 2>/dev/null; then
    echo "go cobra"; return 0
  fi
  if grep -rq "github.com/urfave/cli" . 2>/dev/null; then
    echo "go urfave-cli"; return 0
  fi
  if grep -rq "flag.Parse()" . 2>/dev/null; then
    echo "go flag"; return 0
  fi
  echo "go raw"
}

detect_rust() {
  [ -f Cargo.toml ] || return 1
  if grep -q "clap" Cargo.toml; then
    echo "rust clap"; return 0
  fi
  if grep -q "structopt" Cargo.toml; then
    echo "rust structopt"; return 0
  fi
  echo "rust raw"
}

detect_ruby() {
  { [ -f Gemfile ] || [ -f *.gemspec ] 2>/dev/null; } || return 1
  if grep -rq "require 'thor'" . 2>/dev/null || grep -rq 'require "thor"' . 2>/dev/null; then
    echo "ruby thor"; return 0
  fi
  if grep -rq "OptionParser" . 2>/dev/null; then
    echo "ruby optparse"; return 0
  fi
  echo "ruby raw"
}

detect_node && exit 0
detect_python && exit 0
detect_go 2>/dev/null && exit 0
detect_rust 2>/dev/null && exit 0
detect_ruby 2>/dev/null && exit 0

echo "unknown raw"
