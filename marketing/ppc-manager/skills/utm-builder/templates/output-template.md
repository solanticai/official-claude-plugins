# UTM URLs — {{campaign_name}}

**Campaign:** {{campaign_name}}
**Date:** {{DD_MM_YYYY}}

---

## URLs

| # | Source | Medium | Content | Tagged URL |
|---|---|---|---|---|
{{#urls}}
| {{n}} | {{source}} | {{medium}} | {{content}} | {{tagged_url}} |
{{/urls}}

---

## CSV export

`utm_{{campaign_name}}_{{date}}.csv` — full list for distribution to marketing team.

---

## Validation

- Current GA4 sources matching: {{matched_count}} / {{total_count}}
- New source/medium pairs added: {{new_count}}
- Flagged inconsistencies: {{flagged_count}}

---

## Next steps

1. Distribute the tagged URLs to each channel owner.
2. Do NOT paste Google Ads destination URLs with UTMs — use auto-tagging.
3. Verify in GA4 DebugView once campaigns launch.
