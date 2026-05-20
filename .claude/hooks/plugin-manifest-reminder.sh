#!/usr/bin/env bash
# PostToolUse hook for Write|Edit.
#
# When any file inside <category>/<name>/ is modified (skills, hooks, settings,
# scripts, docs — anything that changes plugin behaviour), require BOTH:
#   1. <category>/<name>/.claude-plugin/plugin.json (version bump)
#   2. .claude-plugin/marketplace.json (matching version bump + description
#      refresh if skills changed)
# to also have unstaged changes before Claude is allowed to finish the turn.
#
# Rationale: Claude Code's plugin marketplace caches do not auto-refresh, and
# the marketplace catalogue is the only signal users see when running
# /plugin update. A skill edit without a manifest version bump means the new
# behaviour ships silently and users on cached versions never receive it.
#
# Chains with changelog-reminder.sh: this hook nudges manifest updates,
# changelog-reminder.sh then nudges the CHANGELOG entry.
#
# Implemented without jq so it runs on bare Git Bash on Windows.

set -euo pipefail

INPUT=$(cat)

FILE_PATH=$(printf '%s' "$INPUT" \
  | tr -d '\r' \
  | grep -oE '"file_path"[[:space:]]*:[[:space:]]*"[^"]*"' \
  | head -n 1 \
  | sed -E 's/.*"file_path"[[:space:]]*:[[:space:]]*"([^"]*)".*/\1/')

if [ -z "${FILE_PATH:-}" ]; then
  exit 0
fi

# Normalise Windows backslashes so path matching works in Git Bash.
NORMALISED=$(printf '%s' "$FILE_PATH" | tr '\\' '/')

# Only fire for files inside <category>/<name>/. Skip the plugin manifests and
# the marketplace catalogue themselves — those are the files we want Claude
# to update, not what triggers the reminder.
case "$NORMALISED" in
  */.claude-plugin/marketplace.json) exit 0 ;;
  */lifestyle/*/.claude-plugin/plugin.json|*/smb/*/.claude-plugin/plugin.json|*/marketing/*/.claude-plugin/plugin.json|*/engineering/*/.claude-plugin/plugin.json|*/data-science/*/.claude-plugin/plugin.json|*/economics/*/.claude-plugin/plugin.json|*/utilities/*/.claude-plugin/plugin.json) exit 0 ;;
  */lifestyle/*|*/smb/*|*/marketing/*|*/engineering/*|*/data-science/*|*/economics/*|*/utilities/*) ;;
  *) exit 0 ;;
esac

# Resolve the repo root from the edited file's directory.
TARGET_DIR=$(dirname "$NORMALISED")
if [ ! -d "$TARGET_DIR" ]; then
  TARGET_DIR=$(dirname "$TARGET_DIR")
fi
REPO_ROOT=$(git -C "$TARGET_DIR" rev-parse --show-toplevel 2>/dev/null) || exit 0

# Only act when this hook script lives in *this* repo's .claude/. Prevents
# the hook from firing if a copy of it ends up under another repo via a
# user-level settings.json.
if [ ! -f "$REPO_ROOT/.claude/hooks/plugin-manifest-reminder.sh" ]; then
  exit 0
fi

if [ ! -f "$REPO_ROOT/.claude-plugin/marketplace.json" ]; then
  exit 0
fi

# Extract the category and plugin name from the path:
#   .../<category>/<plugin>/...
PLUGIN_CATEGORY=$(printf '%s' "$NORMALISED" \
  | sed -nE 's@.*/(lifestyle|smb|marketing|engineering|data-science|economics|utilities)/([^/]+)/.*@\1@p')
PLUGIN_NAME=$(printf '%s' "$NORMALISED" \
  | sed -nE 's@.*/(lifestyle|smb|marketing|engineering|data-science|economics|utilities)/([^/]+)/.*@\2@p')

if [ -z "${PLUGIN_NAME:-}" ] || [ -z "${PLUGIN_CATEGORY:-}" ]; then
  exit 0
fi

PLUGIN_MANIFEST="${PLUGIN_CATEGORY}/${PLUGIN_NAME}/.claude-plugin/plugin.json"

# Sanity-check that this is actually a plugin folder (not e.g. a category README).
if [ ! -f "$REPO_ROOT/$PLUGIN_MANIFEST" ]; then
  exit 0
fi

cd "$REPO_ROOT"

# Has the source file actually changed vs HEAD? PostToolUse fires on every
# Write/Edit, but if the user reverted to the original content there is
# nothing to bump. Use `git status --porcelain` so newly-created (untracked)
# skill files count too — `git diff HEAD` would miss them.
SOURCE_REL="${NORMALISED#$REPO_ROOT/}"
SOURCE_DIRTY=$(git status --porcelain -- "$SOURCE_REL" 2>/dev/null || true)
if [ -z "$SOURCE_DIRTY" ]; then
  exit 0
fi

PLUGIN_DIRTY=$(git status --porcelain -- "$PLUGIN_MANIFEST" 2>/dev/null || true)
MARKETPLACE_DIRTY=$(git status --porcelain -- ".claude-plugin/marketplace.json" 2>/dev/null || true)

MISSING=""
if [ -z "$PLUGIN_DIRTY" ]; then
  MISSING="${PLUGIN_MANIFEST}"
fi
if [ -z "$MARKETPLACE_DIRTY" ]; then
  if [ -n "$MISSING" ]; then
    MISSING="${MISSING} and .claude-plugin/marketplace.json"
  else
    MISSING=".claude-plugin/marketplace.json"
  fi
fi

if [ -z "$MISSING" ]; then
  exit 0
fi

REASON="Plugin source changed (${PLUGIN_NAME}: ${SOURCE_REL}) but ${MISSING} has not been updated. Bump the version in ${PLUGIN_MANIFEST} (semver: patch for fixes, minor for new skills/features, major for breaking changes) AND update the matching entry in .claude-plugin/marketplace.json (version + description if the skill list or scope changed). Both files must stay in sync — marketplace caches do not auto-refresh, so users only see the new version once both manifests advertise it."

printf '{"decision":"block","reason":"%s"}\n' "$REASON"
exit 0
