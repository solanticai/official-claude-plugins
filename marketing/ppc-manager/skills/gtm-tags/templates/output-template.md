# GTM Tags — {{goal}} — {{container_name}}

**Container:** {{container_public_id}}
**Workspace:** {{workspace_name}}
**Version:** {{version_name}} ({{version_id}}) — **{{version_status}}**
**Date:** {{DD_MM_YYYY}}

---

## Goal

{{one_paragraph_goal}}

---

## Changes applied

### Variables created

| Name | Type | Parameter |
|---|---|---|
{{#variables_created}}
| {{name}} | {{type}} | {{summary}} |
{{/variables_created}}

### Triggers created

| Name | Type | Filter |
|---|---|---|
{{#triggers_created}}
| {{name}} | {{type}} | {{filter_summary}} |
{{/triggers_created}}

### Tags created

| Name | Type | Firing trigger | Key parameters |
|---|---|---|---|
{{#tags_created}}
| {{name}} | {{type}} | {{trigger}} | {{key_params}} |
{{/tags_created}}

### Tags updated

| Name | What changed |
|---|---|
{{#tags_updated}}
| {{name}} | {{change}} |
{{/tags_updated}}

---

## Preview verification

- **Preview URL:** {{preview_url}}
- **Steps performed:** {{verification_steps}}
- **Tags fired in preview:** {{tags_fired}}
- **Parameter values observed:** {{params_observed}}
- **Verification confirmed by user:** yes at {{verified_at}}

---

## Published version

- **Version ID:** {{version_id}}
- **Published at:** {{published_at}}
- **Published by:** the ppc-gtm MCP (user-authorised)

---

## Next steps

1. Monitor the new tags in GA4/Meta Events Manager for 24–48 hours.
2. Run `/ppc-manager:campaign-audit` at the end of the first week to verify downstream platforms are receiving the data.
3. If rolling out to multiple campaigns, run `/ppc-manager:gtm-tags` again per campaign.
