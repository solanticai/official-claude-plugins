#!/usr/bin/env bash
# seo-toolkit SessionStart hook — validates that at least one SEO credential is
# configured and usable. Emits a systemMessage if nothing is configured or if a
# provider token has expired. Never blocks session startup.

set -euo pipefail

PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/../.." && pwd)}"
DATA_DIR="${CLAUDE_PLUGIN_DATA:-$HOME/.claude/plugins/data/seo-toolkit}"
PY_PATH_FILE="$DATA_DIR/python_path.txt"

# If the venv bootstrap hasn't written a python path yet, bail silently.
if [ ! -f "$PY_PATH_FILE" ]; then
  exit 0
fi

PY=$(cat "$PY_PATH_FILE")
if [ ! -x "$PY" ] && [ ! -f "$PY" ]; then
  exit 0
fi

PASSPHRASE="${CLAUDE_PLUGIN_OPTION_SEO_VAULT_PASSPHRASE:-}"

if [ -z "$PASSPHRASE" ]; then
  echo '{"systemMessage":"seo-toolkit: vault passphrase not set. Configure seo_vault_passphrase in plugin settings."}'
  exit 0
fi

VAULT_PATH="${SEO_VAULT_PATH:-$DATA_DIR/tokens.enc}"

if [ ! -f "$VAULT_PATH" ]; then
  echo '{"systemMessage":"seo-toolkit: credential vault not found — run `/seo-toolkit:seo-connect` to set up SerpAPI/GSC/etc."}'
  exit 0
fi

export SEO_VAULT_PATH="$VAULT_PATH"
export SEO_VAULT_PASSPHRASE="$PASSPHRASE"

# Run the validator in quiet mode. Exit 0 = healthy, 1 = something failed.
OUTPUT=$("$PY" "$PLUGIN_ROOT/scripts/token_validator.py" --quiet --json 2>&1) || true
EC=$?

if [ $EC -eq 0 ]; then
  exit 0
fi

# Check for the "missing" status specifically
STATUS=$(echo "$OUTPUT" | "$PY" -c 'import json, sys; d=json.loads(sys.stdin.read() or "{}"); print(d.get("status",""))' 2>/dev/null || echo "")
if [ "$STATUS" = "missing" ]; then
  echo '{"systemMessage":"seo-toolkit: SEO credentials not configured — run `/seo-toolkit:seo-connect` to set up SerpAPI/GSC/etc."}'
  exit 0
fi

# Surface the first problem as a systemMessage
FIRST_ISSUE=$(echo "$OUTPUT" | "$PY" -c '
import json, sys
d = json.loads(sys.stdin.read() or "{}")
providers = d.get("providers", {})
bad = {k: v for k, v in providers.items() if v.get("status") not in ("ok",)}
if bad:
    first_key = next(iter(bad))
    print(f"{first_key}: {bad[first_key].get(\"status\", \"unknown\")}")
else:
    print("unknown issue")
' 2>/dev/null || echo "unknown issue")

echo "{\"systemMessage\":\"seo-toolkit: credential check failed ($FIRST_ISSUE). Run \`/seo-toolkit:seo-connect\` to reconnect.\"}"
exit 0
