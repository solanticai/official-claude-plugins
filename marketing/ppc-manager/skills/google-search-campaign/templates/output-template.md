# Google Search Campaign — {{campaign_name}}

**Customer:** {{customer_id}} ({{customer_name}})
**Campaign:** {{campaign_name}}
**Budget:** AUD {{daily_budget}} / day
**Status:** PAUSED (awaiting user enable)
**Date:** {{DD_MM_YYYY}}

---

## Structure

| Ad group | Keywords | Match mix | RSA |
|---|---|---|---|
{{#ad_groups}}
| {{name}} | {{keyword_count}} | {{match_mix}} | {{rsa_summary}} |
{{/ad_groups}}

---

## Ad group detail

{{#ad_groups}}
### {{name}}

**Landing page:** {{final_url}}
**Default CPC bid:** AUD {{cpc_bid}}

**Keywords:**

| Keyword | Match type |
|---|---|
{{#keywords}}
| {{text}} | {{match_type}} |
{{/keywords}}

**RSA:**

- Headlines: {{headlines_count}} (pinned: {{pinned_count}})
- Descriptions: {{descriptions_count}}
- Path: /{{path1}}/{{path2}}

{{/ad_groups}}

---

## Negative keywords

| Keyword | Match type | Source |
|---|---|---|
{{#negative_keywords}}
| {{text}} | {{match_type}} | {{source}} |
{{/negative_keywords}}

---

## Readiness checklist

- [{{checkbox_conversions}}] Conversion tracking imported from GA4
- [{{checkbox_billing}}] Billing active
- [{{checkbox_mc}}] Merchant Center linked (if relevant)
- [{{checkbox_extensions}}] Ad extensions installed
- [{{checkbox_lp}}] Landing page live (HTTP 200)
- [{{checkbox_budget}}] Daily budget approved
- [{{checkbox_confirm}}] User confirmed ENABLE

---

## Next steps

1. Tick every readiness checkbox.
2. Run `/ppc-manager:google-search-campaign --enable <campaign-id>` (or enable in the Google Ads UI).
3. In 7 days, run `/ppc-manager:campaign-audit` to review initial performance.
