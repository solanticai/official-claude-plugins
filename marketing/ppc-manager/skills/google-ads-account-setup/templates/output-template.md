# Google Ads Account Setup — {{account_name}}

**Customer ID:** {{customer_id}}
**Currency:** {{currency}}
**Time zone:** {{time_zone}}
**Test account:** {{test_account}}
**Date:** {{DD_MM_YYYY}}

---

## Audit findings

| Area | Current | Desired | Severity |
|---|---|---|---|
{{#findings}}
| {{area}} | {{current}} | {{desired}} | {{severity}} |
{{/findings}}

---

## Conversion actions

| Name | Category | Primary? | Attribution | Source | Status |
|---|---|---|---|---|---|
{{#conversions}}
| {{name}} | {{category}} | {{primary}} | {{attribution}} | {{source}} | {{status}} |
{{/conversions}}

---

## Linked accounts

| Link type | Target | Status |
|---|---|---|
| GA4 | {{ga4_property}} | {{ga4_status}} |
| Merchant Center | {{mc_id}} | {{mc_status}} |
| YouTube channel | {{youtube_id}} | {{youtube_status}} |

---

## Fix plan

### Automatable fixes applied via MCP

{{#automated_fixes}}
- **{{action}}** — {{detail}}
{{/automated_fixes}}

### Manual fixes

1. {{manual_fix_1}}
2. {{manual_fix_2}}

### Wait for data

- {{wait_for_data_1}}
- {{wait_for_data_2}}

---

## Next steps

1. Run `/ppc-manager:google-search-campaign` to build the first Search campaign.
2. Run `/ppc-manager:google-pmax-campaign` for Performance Max.
3. Run `/ppc-manager:keyword-research` if Search is the first priority.
