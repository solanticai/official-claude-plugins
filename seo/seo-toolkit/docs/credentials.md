# SEO Toolkit — Credential Architecture

This document explains how `seo-toolkit` stores, loads, and validates credentials for SerpAPI, DataForSEO, Ahrefs, Moz, PageSpeed Insights, Google Search Console (OAuth), and Google Analytics 4 (OAuth). Read this if you want to understand what is on disk, how tokens rotate, and how to revoke or back up the vault.

---

## Quick reference

| Where | What | Protection |
|---|---|---|
| Claude Code keychain (via `userConfig.sensitive=true`) | `seo_vault_passphrase` | OS keychain (macOS) or `~/.claude/.credentials.json` mode 0600 (Linux/Windows) |
| `${CLAUDE_PLUGIN_DATA}/tokens.enc` | API keys for SerpAPI/DataForSEO/Ahrefs/Moz/PSI; OAuth refresh tokens for GSC and GA4 | Fernet (AES-128-CBC + HMAC-SHA256), key derived from vault passphrase via PBKDF2-HMAC-SHA256 100 000 iterations |
| `${CLAUDE_PLUGIN_ROOT}/.venv/` | Python dependencies (cryptography, httpx, google-auth, etc.) | None — not secrets |
| `${CLAUDE_PLUGIN_DATA}/install.log` | pip install stderr | None — diagnostic only |
| `${CLAUDE_PLUGIN_DATA}/requirements.stamp` | Copy of `requirements.txt` to skip pip when unchanged | None |
| `${CLAUDE_PLUGIN_DATA}/python_path.txt` | Resolved path to the venv's Python interpreter | None |
| `${CLAUDE_PLUGIN_DATA}/cache/` | HTTP response cache (24h TTL, keyed by URL + params SHA-256) | None — no secrets cached |

No tokens are ever stored in `settings.json`, shell environment variables, or the filesystem outside `${CLAUDE_PLUGIN_DATA}`.

---

## Two-tier architecture

### Tier 1 — Claude Code `userConfig` with `sensitive: true`

One field is stored in the OS keychain:

- `seo_vault_passphrase` — the passphrase used to derive the vault encryption key.

This is set once during plugin setup. It never appears in the transcript, skill output, or any log file.

At runtime it is exposed to scripts via:

```
CLAUDE_PLUGIN_OPTION_SEO_VAULT_PASSPHRASE
```

### Tier 2 — Encrypted vault

The vault lives at `${CLAUDE_PLUGIN_DATA}/tokens.enc` and contains:

```json
{
  "version": 1,
  "updated_at": "<ISO-8601>",
  "serpapi": {
    "api_key": "..."
  },
  "dataforseo": {
    "login": "...",
    "password": "..."
  },
  "ahrefs": {
    "api_key": "..."
  },
  "moz": {
    "access_id": "...",
    "secret": "..."
  },
  "psi": {
    "api_key": "..."
  },
  "gsc": {
    "client_id": "...",
    "client_secret": "...",
    "refresh_token": "...",
    "access_token": "...",
    "access_token_expires_at": "<ISO-8601>"
  },
  "ga4": {
    "client_id": "...",
    "client_secret": "...",
    "refresh_token": "...",
    "access_token": "...",
    "access_token_expires_at": "<ISO-8601>"
  }
}
```

The file is **encrypted at rest** with Fernet. The key is derived from the vault passphrase via PBKDF2-HMAC-SHA256 with 100 000 iterations. If you copy `tokens.enc` to another machine, you need both the file and the passphrase to decrypt it.

Writes are atomic: `seo_vault.py` writes to `tokens.enc.tmp`, fsyncs, and then `os.replace()`s to the final path. A `filelock` around the write prevents concurrent writes from multiple scripts.

On POSIX, the file is `chmod 0600` after each write. On Windows, it inherits the user's profile ACLs.

---

## On-disk location by OS

| OS | Vault path |
|---|---|
| macOS | `~/.claude/plugins/data/seo-toolkit/tokens.enc` |
| Linux | `~/.claude/plugins/data/seo-toolkit/tokens.enc` |
| Windows | `%USERPROFILE%\.claude\plugins\data\seo-toolkit\tokens.enc` |

---

## Environment variable table

| Variable | Source | Maps to provider |
|---|---|---|
| `CLAUDE_PLUGIN_OPTION_SEO_VAULT_PASSPHRASE` | userConfig (sensitive) | Used to derive vault encryption key |
| `SEO_VAULT_PATH` | Set by hook scripts | Override vault file path (testing) |
| `SEO_VAULT_PASSPHRASE` | Set by hook scripts | Override passphrase (testing) |

Scripts read credentials directly from the vault via `scripts/lib/seo_vault.py` — they do not rely on additional environment variables per provider.

---

## OAuth flow diagrams

### Google Search Console (GSC)

```
User runs /seo-toolkit:seo-connect gsc
  │
  ├─► oauth_gsc.py starts loopback server on localhost:PORT
  │
  ├─► Opens browser to Google OAuth consent URL
  │     (scope: webmasters.readonly)
  │
  ├─► User grants consent in browser
  │
  ├─► Google redirects to http://localhost:PORT/?code=AUTH_CODE
  │
  ├─► oauth_gsc.py exchanges code for access + refresh tokens
  │
  └─► Writes refresh_token + access_token to vault under "gsc"
```

### Google Analytics 4 (GA4)

Identical flow to GSC, with scope `analytics.readonly` and vault key `ga4`.

---

## Token refresh

### API keys (SerpAPI, DataForSEO, Ahrefs, Moz, PSI)

API keys do not expire. They are read from the vault at runtime by each client module and used directly in HTTP requests. No refresh logic is needed.

### OAuth tokens (GSC, GA4)

1. Each client module calls `get_secret(provider, "refresh_token", passphrase)`.
2. If the cached access token is within 60 seconds of expiry (or absent), the client uses `google-auth` to call `google.auth.transport.requests.Request()` and refresh the token.
3. The new access token and expiry are written back to the vault.
4. If the refresh token itself is invalid (`invalid_grant`), the client raises an error directing the user to re-run `/seo-toolkit:seo-connect <provider>`.

---

## Threat model

| Threat | Mitigation | Residual risk |
|---|---|---|
| Attacker reads `tokens.enc` from disk | Fernet encryption + PBKDF2 key derivation — useless without passphrase | PBKDF2 cracking if weak passphrase chosen |
| Tampering with `tokens.enc` | Fernet includes HMAC-SHA256 — any modification fails decryption | None (integrity is verified on every read) |
| Torn vault write during crash | Atomic write via `.tmp` + `os.replace()` + `filelock` | None (file is either old or new, never partial) |
| Passphrase leaked via environment | Passphrase stored in OS keychain; injected at runtime; never logged | Claude Code process environment is accessible to local code execution |
| API key leaked via logs | `install.log` contains only pip output; no credential-writing steps log values | None |
| Compromised pip package | Requirements are version-pinned; `cryptography` is a well-audited library | Supply-chain risk inherent to any Python project |

---

## Backing up the vault

The vault is safe to back up anywhere — it is encrypted:

```bash
cp ~/.claude/plugins/data/seo-toolkit/tokens.enc ~/backups/seo-tokens-2026-05-20.enc
```

To restore: copy the file to `${CLAUDE_PLUGIN_DATA}/tokens.enc` on the target machine and ensure the `seo_vault_passphrase` plugin setting matches the original.

---

## Revoking access

### API key providers

Delete the key from the provider's dashboard, then run `/seo-toolkit:seo-disconnect <provider>` to remove it from the local vault.

### OAuth providers (GSC, GA4)

1. Go to [myaccount.google.com/permissions](https://myaccount.google.com/permissions) and revoke the OAuth app's access.
2. Run `/seo-toolkit:seo-disconnect gsc` (or `ga4`) to remove the refresh token from the vault.

### Full reset

```bash
rm -rf ~/.claude/plugins/data/seo-toolkit
```

Then re-enable the plugin and run `/seo-toolkit:seo-connect` to start fresh.

---

## Troubleshooting

### "Vault passphrase not set"

Set `seo_vault_passphrase` in the plugin settings (Claude Code userConfig). It should appear in the plugin enable dialog.

### "Failed to decrypt vault — wrong passphrase or corrupt file"

Either the passphrase changed or `tokens.enc` is corrupted. If you remember the passphrase, re-enter it in plugin settings. If the file is corrupt, delete `tokens.enc` and re-run `/seo-toolkit:seo-connect`.

### "Credential vault not found — run seo-connect"

No vault exists yet. Run `/seo-toolkit:seo-connect` to create one and add credentials.

### "pip install failed — see install.log"

Check `${CLAUDE_PLUGIN_DATA}/install.log`. Common causes: Python < 3.11 on PATH, no internet during first install, or missing C build tools for the `cryptography` package (install platform build tools, then restart the session).
