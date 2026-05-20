#!/usr/bin/env bash
# ppc-manager SessionStart hook — validates the encrypted vault exists and
# every credential inside is usable. Emits a systemMessage on the first error
# or on near-expiry warnings. Never blocks.

set -e

PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/../.." && pwd)}"
DATA_DIR="${CLAUDE_PLUGIN_DATA:-$HOME/.claude/plugins/data/ppc-manager}"
PY_PATH_FILE="$DATA_DIR/python_path.txt"

# If the venv bootstrap hasn't written a python path yet, bail silently.
if [ ! -f "$PY_PATH_FILE" ]; then
  exit 0
fi

PY=$(cat "$PY_PATH_FILE")
if [ ! -x "$PY" ] && [ ! -f "$PY" ]; then
  exit 0
fi

PASSPHRASE="${CLAUDE_PLUGIN_OPTION_PPC_VAULT_PASSPHRASE:-}"
VAULT_PATH="${PPC_VAULT_PATH:-$DATA_DIR/tokens.enc}"

if [ -z "$PASSPHRASE" ]; then
  echo '{"systemMessage":"ppc-manager: vault passphrase not set. Configure ppc_vault_passphrase in plugin settings."}'
  exit 0
fi

if [ ! -f "$VAULT_PATH" ]; then
  echo '{"systemMessage":"ppc-manager: credential vault not found. Run /ppc-manager:oauth-setup to connect Google and Meta."}'
  exit 0
fi

export PPC_VAULT_PATH="$VAULT_PATH"
export PPC_VAULT_PASSPHRASE="$PASSPHRASE"

# Run the validator in quiet mode. Exit code 0 = all good, 1 = something failed.
OUTPUT=$("$PY" "$PLUGIN_ROOT/scripts/token_validator.py" --quiet --json 2>&1) || true
EC=$?

if [ $EC -eq 0 ]; then
  exit 0
fi

# Surface the first problem as a systemMessage so Claude can tell the user.
FIRST_ISSUE=$(echo "$OUTPUT" | "$PY" -c 'import json, sys; d=json.loads(sys.stdin.read() or "{}"); rs=d.get("results",[]); bad=[r for r in rs if r.get("status") not in ("ok","expiring_soon")] or rs; print(json.dumps(bad[0]) if bad else "{}")' 2>/dev/null || echo '{}')
echo "{\"systemMessage\":\"ppc-manager: credential check failed — $FIRST_ISSUE. Run /ppc-manager:oauth-setup refresh.\"}"
exit 0
