# ppc-manager OAuth Setup — Summary

**Date:** {{DD_MM_YYYY}}
**Vault:** `{{vault_path}}`
**Status:** {{overall_status}}

---

## Google accounts

{{#google_accounts}}
- **{{label}}** — {{email}}
  - Scopes: {{scopes_summary}}
  - Connected: {{connected_at}}
  - Last refresh: {{access_token_refreshed_at}}
{{/google_accounts}}

## Google Ads accounts

{{#google_ads_accounts}}
- **{{label}}** — customer_id `{{customer_id}}` (linked to Google account `{{linked_google_account}}`)
{{/google_ads_accounts}}

- **Developer token:** {{developer_token_status}}
- **MCC login_customer_id:** {{login_customer_id}}

## Meta accounts

{{#meta_accounts}}
- **{{label}}** — {{user_name}} (user_id {{user_id}})
  - Ad accounts: {{ad_accounts_list}}
  - Token expires: {{long_lived_user_token_expires_at}} ({{days_left}} days)
{{/meta_accounts}}

---

## Validation results

| Platform | Account | Status | Detail |
|---|---|---|---|
{{#validation_rows}}
| {{platform}} | {{account}} | {{status}} | {{detail}} |
{{/validation_rows}}

---

## Next steps

1. Run `/ppc-manager:gtm-setup` to configure Google Tag Manager.
2. Run `/ppc-manager:ga4-setup` to configure Google Analytics 4.
3. Run `/ppc-manager:google-ads-account-setup` to audit your Google Ads baseline.
4. Run `/ppc-manager:meta-pixel-setup` to wire up Meta tracking.
