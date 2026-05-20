---
name: seo-disconnect
description: Remove a configured SEO provider's credentials from the vault. Requires confirmation before deletion.
argument-hint: "<provider>"
---

# /seo-toolkit:seo-disconnect

You are removing a provider's credentials from the seo-toolkit encrypted vault. This action is irreversible — the credentials will need to be re-entered via `/seo-toolkit:seo-connect` if the user wants to reconnect.

## Supported providers

`serpapi`, `dataforseo`, `ahrefs`, `moz`, `psi`, `gsc`, `ga4`

## Workflow

### 1. Parse the provider argument

Parse `$ARGUMENTS` for the provider name. Valid values: `serpapi`, `dataforseo`, `ahrefs`, `moz`, `psi`, `gsc`, `ga4`.

If no argument is provided, ask via AskUserQuestion: "Which provider do you want to disconnect? Options: serpapi, dataforseo, ahrefs, moz, psi, gsc, ga4"

If the argument is not a valid provider name, list the valid options and stop.

### 2. Confirm with the user

Ask via AskUserQuestion:

> Are you sure you want to remove the **{provider}** credentials from the seo-toolkit vault? This cannot be undone. Any skills that rely on {provider} will stop working until you reconnect via `/seo-toolkit:seo-connect {provider}`.
>
> Type **yes** to confirm, or anything else to cancel.

If the user does not type `yes` (case-insensitive), abort with: "Disconnection cancelled. No changes made."

### 3. Obtain the vault passphrase

Read `CLAUDE_PLUGIN_OPTION_SEO_VAULT_PASSPHRASE` from the environment. If not set, ask via AskUserQuestion: "Enter your vault passphrase to authorise the removal."

### 4. Remove the provider

Execute:

```bash
"${CLAUDE_PLUGIN_ROOT}/.venv/bin/python" "${CLAUDE_PLUGIN_ROOT}/scripts/lib/seo_vault.py" \
  remove <provider> --passphrase "$PASSPHRASE"
```

If the script exits with an error, surface the error message to the user and stop.

### 5. Confirm removal

Tell the user: "**{provider}** credentials have been removed from the vault."

Run the validator to show the updated status:

```bash
"${CLAUDE_PLUGIN_ROOT}/.venv/bin/python" "${CLAUDE_PLUGIN_ROOT}/scripts/token_validator.py" --json
```

Display the updated provider table (same format as `/seo-toolkit:seo-status`).

### 6. Suggest reconnection

If the user may have disconnected by mistake, remind them: "To reconnect, run `/seo-toolkit:seo-connect {provider}`."

## Security note

Never print vault passphrase, API keys, or OAuth tokens in the transcript. The removal script only deletes the vault entry — it does not revoke API keys or OAuth tokens on the provider's side. If the user wants to fully revoke access, they should also go to the provider's dashboard and revoke the key there.
