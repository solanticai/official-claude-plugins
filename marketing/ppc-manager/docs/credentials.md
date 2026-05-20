# PPC Manager — Credential Architecture

This document explains how `ppc-manager` stores, loads, and refreshes credentials for Google Tag Manager, Google Analytics 4, Google Ads, and Meta Business Manager. Read this if you want to understand what's on disk, how tokens rotate, and how to revoke or back up the vault.

---

## Quick reference

| Where | What | Protection |
|---|---|---|
| Claude Code keychain (via `userConfig.sensitive=true`) | `ppc_vault_passphrase`, `google_ads_developer_token`, `meta_app_secret` | OS keychain (macOS) or `~/.claude/.credentials.json` mode 0600 (Linux/Windows) |
| `${CLAUDE_PLUGIN_DATA}/tokens.enc` | Google refresh tokens, Google access token cache, Meta long-lived tokens, ad account metadata | Fernet (AES-128-CBC + HMAC-SHA256), key derived from vault passphrase via PBKDF2-HMAC-SHA256 100 000 iterations |
| `${CLAUDE_PLUGIN_DATA}/venv/` | Python dependencies (fastmcp, google-ads, facebook_business, cryptography, etc.) | None — not secrets |
| `${CLAUDE_PLUGIN_DATA}/install.log` | pip install stderr | None — diagnostic only |
| `${CLAUDE_PLUGIN_DATA}/requirements.stamp` | Copy of `requirements.txt` to skip pip when unchanged | None |
| `${CLAUDE_PLUGIN_DATA}/python_path.txt` | Resolved path to the venv's Python interpreter | None |

No tokens are ever stored in `settings.json`, environment variables in the shell, or the filesystem outside `${CLAUDE_PLUGIN_DATA}`.

---

## Two-tier architecture

### Tier 1 — Claude Code `userConfig` with `sensitive: true`

Three fields are stored in the OS keychain via Claude Code's built-in sensitive-value mechanism:

- `ppc_vault_passphrase` — the passphrase used to decrypt the vault file.
- `google_ads_developer_token` — the ~22-character Google Ads API developer token (rarely rotates).
- `meta_app_secret` — the Meta app secret (rarely rotates).

These are set **once** during plugin enable. You will be prompted for them in a dialog. They never appear in the transcript, the skill output, or any log file.

Non-sensitive `userConfig` fields (`google_oauth_client_secret_path`, `meta_app_id`, `google_ads_login_customer_id`, `ppc_default_google_account`, `ppc_default_meta_account`) live in the plugin's `settings.json` under `pluginConfigs.ppc-manager.options`. These are not secrets.

At runtime, the fields are exposed to subprocesses via:

- `CLAUDE_PLUGIN_OPTION_PPC_VAULT_PASSPHRASE`
- `CLAUDE_PLUGIN_OPTION_GOOGLE_ADS_DEVELOPER_TOKEN`
- `CLAUDE_PLUGIN_OPTION_META_APP_ID`
- `CLAUDE_PLUGIN_OPTION_META_APP_SECRET`
- etc.

### Tier 2 — Encrypted vault

The vault lives at `${CLAUDE_PLUGIN_DATA}/tokens.enc` and contains:

```json
{
  "version": 1,
  "updated_at": "<ISO-8601 timestamp>",
  "google": {
    "client_secret": "<from GCP client_secret.json>",
    "accounts": {
      "<label>": {
        "email": "...",
        "client_id": "...",
        "refresh_token": "...",
        "access_token": "...",
        "access_token_expires_at": "<ISO-8601>",
        "scopes": ["tagmanager.edit.containers", "analytics.readonly", "adwords", ...],
        "connected_at": "<ISO-8601>"
      }
    }
  },
  "google_ads": {
    "accounts": {
      "<label>": {
        "customer_id": "...",
        "login_customer_id": "...",
        "linked_google_account": "default"
      }
    }
  },
  "meta": {
    "app_secret": "<same as userConfig, duplicated here for app_secret-less re-exchanges>",
    "accounts": {
      "<label>": {
        "user_id": "...",
        "long_lived_user_token": "EAAB...",
        "long_lived_user_token_expires_at": "<ISO-8601>",
        "ad_accounts": [...]
      }
    }
  }
}
```

The file is **encrypted at rest** with Fernet. The encryption key is derived from the vault passphrase via PBKDF2-HMAC-SHA256 with 100 000 iterations and a fixed salt tied to this plugin's identity. If you copy `tokens.enc` to another machine, you need both the file and the passphrase to decrypt it.

Writes are atomic: the library writes to `tokens.enc.tmp`, fsync's, and then `os.replace()` to the final path. A `filelock` around the write prevents races between the four MCP server processes that may be trying to persist refreshed tokens simultaneously.

On POSIX, the file is `chmod 0600` after each write. On Windows, the file inherits the user's profile ACLs.

---

## On-disk location by OS

| OS | Vault path |
|---|---|
| macOS | `~/.claude/plugins/data/ppc-manager/tokens.enc` |
| Linux | `~/.claude/plugins/data/ppc-manager/tokens.enc` |
| Windows | `%USERPROFILE%\.claude\plugins\data\ppc-manager\tokens.enc` |

All OSes also host: `venv/`, `install.log`, `requirements.stamp`, `python_path.txt` in the same directory.

---

## Token refresh flow

### Google (GTM + GA4 + Google Ads)

1. Every MCP tool call starts with `auth.get_google_credentials(label)` via the shared `scripts/lib/ppc_auth.py`.
2. That function decrypts the vault (cached in memory for the server process lifetime), reads the account entry.
3. If `access_token_expires_at` is within 60 seconds of now or past, calls `google.auth.transport.requests.Request()` + `creds.refresh(Request())`.
4. On success, writes the new `access_token` + `access_token_expires_at` back to the vault (under `filelock`) and returns the live `Credentials` object.
5. If the refresh token itself is invalid (`invalid_grant`), raises `AuthError` with a message directing the user to `/ppc-manager:oauth-setup`.

### Meta

1. Every MCP tool call starts with `auth.get_meta_access_token(label)`.
2. Reads the vault entry. If `long_lived_user_token_expires_at` is > 5 days away, returns the token as-is.
3. If within 5 days of expiry, hits `https://graph.facebook.com/v22.0/oauth/access_token?grant_type=fb_exchange_token` with `app_id` + `app_secret` + current token. Meta issues a new token with a fresh 60-day expiry.
4. Writes the new token + expiry back to the vault.
5. If the current token has already expired, raises `AuthError` — the user must re-run `/ppc-manager:oauth-setup`.

Meta long-lived tokens can be **re-exchanged indefinitely** as long as they're still valid — this is the intended way to keep them fresh. The skill's SessionStart credential check hook warns 7 days before expiry so the user can re-exchange proactively.

---

## Running `/ppc-manager:oauth-setup` for the first time

1. Enable the plugin in Claude Code. You'll be prompted for 8 `userConfig` fields:
   - **3 sensitive:** `ppc_vault_passphrase`, `google_ads_developer_token`, `meta_app_secret`
   - **5 non-sensitive:** `google_oauth_client_secret_path`, `meta_app_id`, `google_ads_login_customer_id`, `ppc_default_google_account`, `ppc_default_meta_account`
   - Only `ppc_vault_passphrase` is strictly required upfront — fill the rest during `oauth-setup` if easier.
2. Run `/ppc-manager:oauth-setup` and follow the skill's phases:
   - Phase 2 walks through GCP OAuth client creation if you don't have one.
   - Phase 3 runs `scripts/oauth_google.py` which opens your browser, catches the OAuth redirect on a local loopback, and writes refresh tokens to the vault.
   - Phase 4 captures Google Ads developer token + optional MCC ID + account labels.
   - Phase 5 runs `scripts/oauth_meta.py` which opens your browser for Meta OAuth consent and exchanges the code for a long-lived token.
   - Phase 6 runs `scripts/token_validator.py --json` to verify every account in the vault.
3. After successful completion, the vault is created and every other skill can use it.

---

## Manually rotating Meta tokens

The SessionStart hook warns 7 days before expiry. To rotate manually:

```
/ppc-manager:oauth-setup refresh meta default
```

This re-runs the Meta OAuth flow for the `default` account and rewrites the vault entry. Browser consent is required again (Meta doesn't expose a refresh token — every rotation requires user consent).

Alternatively, you can force a re-exchange (without browser consent) via the CLI:

```bash
python scripts/oauth_meta.py \
  --app-id $META_APP_ID \
  --app-secret $META_APP_SECRET \
  --vault-path $VAULT_PATH \
  --vault-passphrase $VAULT_PASSPHRASE
```

---

## Backing up the vault

Because the vault is encrypted, you can safely back it up via any mechanism:

```bash
# Simple copy — the file is useless without the passphrase
cp ~/.claude/plugins/data/ppc-manager/tokens.enc ~/backups/tokens-2026-04-11.enc
```

To restore on a new machine:

1. Install the plugin on the new machine.
2. Copy `tokens.enc` to `${CLAUDE_PLUGIN_DATA}/tokens.enc` on the new machine.
3. Enable the plugin. Set `ppc_vault_passphrase` to the same value as on the original machine.
4. Run a skill — it will decrypt the vault and use the tokens as if nothing changed.

Google refresh tokens are portable — they don't care which machine uses them. Meta long-lived tokens are also portable but will expire on their original timeline.

---

## Revoking access

To fully revoke ppc-manager's access to your accounts:

### Google

1. Go to [myaccount.google.com/permissions](https://myaccount.google.com/permissions).
2. Find the OAuth client named `ppc-manager` (or whatever you named it in GCP).
3. Click **Remove access**.
4. This invalidates every refresh token issued to that client.

### Meta

1. Go to [business.facebook.com/settings/system-users](https://business.facebook.com/settings/system-users).
2. Find your ppc-manager app connection.
3. Remove it.

### Local cleanup

After revoking upstream, delete the vault and plugin data directory:

```bash
rm -rf ~/.claude/plugins/data/ppc-manager
```

Disable and re-enable the plugin in Claude Code — you'll be prompted for a new passphrase. Then run `/ppc-manager:oauth-setup` to reconnect.

---

## Security model

- **Confidentiality:** Vault is encrypted at rest. An attacker with read access to `tokens.enc` needs either the passphrase or a PBKDF2 cracking run to decrypt it.
- **Integrity:** Fernet includes an HMAC, so any tampering with `tokens.enc` fails to decrypt. You cannot trivially swap tokens without re-encrypting.
- **Availability:** Atomic writes and filelock prevent torn writes and races.
- **Key management:** The passphrase lives in the OS keychain; the vault file lives in `${CLAUDE_PLUGIN_DATA}`. Both are needed to decrypt.
- **Logging:** `masking_logger.py` filters out anything matching `ya29.*`, `1//.*`, or `EAAB.*` from log output. Raw tokens never appear in `install.log` or the transcript.
- **Process isolation:** Each of the four MCP servers is a separate Python process. A crash in one doesn't leak state from another.

### What the security model does NOT protect against

- **Malicious access to the running Claude Code process.** If an attacker has code execution on your machine, they can read the passphrase from the process environment and decrypt the vault.
- **Keylogger during the initial passphrase prompt.** Same threat model.
- **A compromised pip package pulled in by `requirements.txt`.** Mitigated by pinning major versions, but ultimately you're trusting the Python ecosystem.
- **A compromised upstream provider** (Google OAuth infrastructure, Meta Graph API).

For a hardened deployment, run ppc-manager in a dedicated VM or sandbox with no access to other secrets.

---

## Troubleshooting

### "Vault not found. Run /ppc-manager:oauth-setup first."

The vault file doesn't exist yet. Run `/ppc-manager:oauth-setup`.

### "Failed to decrypt vault. Passphrase is wrong or the vault is corrupt."

Either:
- You entered a different passphrase in the plugin enable dialog than originally.
- The `tokens.enc` file is corrupted (rare, usually due to an unclean system shutdown during a write).

Fix: disable and re-enable the plugin to re-prompt for the passphrase. If that doesn't work, delete `tokens.enc` and re-run `/ppc-manager:oauth-setup`.

### "AuthError: Google account 'default' has no refresh token."

The vault is missing a refresh token for that account. Either OAuth was interrupted mid-flow, or the refresh token was never issued (Google sometimes omits it on second consent — the scripts set `prompt=consent` to force it). Re-run `/ppc-manager:oauth-setup`.

### "AuthError: Meta token for account 'default' expired on ..."

More than 60 days since last re-exchange. Re-run `/ppc-manager:oauth-setup refresh meta`.

### "ensure-venv hook failed"

Check `${CLAUDE_PLUGIN_DATA}/install.log` for the pip error. Common causes:
- Python < 3.11 on PATH.
- No internet during first install.
- Missing compiler for `cryptography` (install platform build tools).

### SessionStart hook prints a credential warning

The `check-credentials.sh` hook ran `token_validator.py --quiet` and something failed. The message tells you which account and platform. Run `/ppc-manager:oauth-setup refresh <platform> <label>` to fix.
