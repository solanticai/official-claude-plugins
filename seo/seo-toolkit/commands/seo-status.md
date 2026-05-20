---
name: seo-status
description: Show the connection status of all configured SEO data providers — which are connected, when they were last validated, and when OAuth tokens expire.
argument-hint: ""
---

# /seo-toolkit:seo-status

You are checking and displaying the credential status for all SEO data providers configured in the seo-toolkit vault.

## Workflow

### 1. Locate Python interpreter

Read `${CLAUDE_PLUGIN_DATA}/python_path.txt` to get the venv Python path. If the file does not exist, tell the user to start a new Claude Code session so the `ensure-venv.sh` hook can run, then try again.

### 2. Run the validator

Execute:

```bash
"$PYTHON" "${CLAUDE_PLUGIN_ROOT}/scripts/token_validator.py" --json
```

Capture both stdout and the exit code. If the script fails to run (missing file, syntax error), report the error directly.

### 3. Parse and render the results

Parse the JSON output. Render a markdown table:

```markdown
## SEO Toolkit — Credential Status

| Provider     | Connected | Last Validated         | Expires In    | Notes            |
|-------------|:---------:|------------------------|---------------|-----------------|
| SerpAPI      | ✓         | 2026-05-20 14:32 AEST  | Never (API key) | —              |
| DataForSEO   | ✓         | 2026-05-20 14:32 AEST  | Never (API key) | —              |
| Ahrefs       | ✗         | —                      | —             | Not configured  |
| Moz          | ✗         | —                      | —             | Not configured  |
| PSI          | ✓         | 2026-05-20 14:32 AEST  | Never (API key) | —              |
| GSC (OAuth)  | ✓         | 2026-05-20 14:32 AEST  | 58 days       | —              |
| GA4 (OAuth)  | ✗         | —                      | —             | Not configured  |
```

Rules for the table:
- **Connected**: ✓ if the provider's status is `ok`, ✗ otherwise.
- **Last Validated**: ISO timestamp from the validator output, formatted as `YYYY-MM-DD HH:mm AEST`. If never validated, show `—`.
- **Expires In**: For OAuth providers, show days until token expiry. For API-key providers, show `Never (API key)`. If token is expired, show `EXPIRED` in bold.
- **Notes**: Surface any warning from the validator (e.g. "expiring soon", "invalid key").

### 4. Overall health summary

Below the table, add a one-line summary:
- If all configured providers are healthy: "All configured providers are connected and healthy."
- If any provider is expiring within 7 days: "Warning: GSC token expires in N days. Run `/seo-toolkit:seo-connect gsc` to refresh."
- If any provider is missing or stale: "N provider(s) need attention. Run `/seo-toolkit:seo-connect <provider>` to reconnect."

### 5. Suggest next step

If no providers are configured at all, tell the user to run `/seo-toolkit:seo-connect` to get started.

## Security note

Never print API keys, passwords, or OAuth tokens — the validator output never includes raw credentials, only status fields.
