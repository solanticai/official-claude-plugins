# Google Performance Max Campaign — {{campaign_name}}

**Customer:** {{customer_id}} ({{customer_name}})
**Campaign:** {{campaign_name}}
**Budget:** AUD {{daily_budget}} / day
**Bidding:** {{bidding_strategy}} {{bidding_target}}
**Status:** draft (manual setup required in v1.0)
**Date:** {{DD_MM_YYYY}}

---

## Asset groups

{{#asset_groups}}
### {{name}}

- **Theme:** {{theme}}
- **Final URL:** {{final_url}}
- **Audience signal:** {{audience_signal}}

**Headlines (short):**
{{#short_headlines}}
1. {{text}}
{{/short_headlines}}

**Headlines (long):**
{{#long_headlines}}
1. {{text}}
{{/long_headlines}}

**Descriptions:**
{{#descriptions}}
- {{text}} ({{length}} chars, {{type}})
{{/descriptions}}

**Image brief:** {{image_brief}}

**Video brief:** {{video_brief}}

{{/asset_groups}}

---

## URL expansion exclusions

```
{{url_exclusions}}
```

---

## Merchant Center feed filter (retail)

{{feed_filter}}

---

## Readiness checklist

- [{{mc}}] Merchant Center linked and feed approved
- [{{conv}}] Conversion actions Primary with values
- [{{images}}] ≥15 images per asset group
- [{{video}}] ≥1 video per asset group
- [{{audience}}] Audience signals defined
- [{{exclusions}}] URL expansion exclusions configured
- [{{budget}}] Daily budget approved
- [{{learning}}] Learning period expectations set with stakeholders

---

## Next steps

1. Create the campaign via Google Ads UI (PMax-specific APIs not yet exposed in v1.0 MCP).
2. Upload all assets per asset group brief.
3. Link Merchant Center feed with the filter above.
4. Launch in PAUSED state.
5. Run `/ppc-manager:campaign-audit --scope pmax` after the 2-week learning period.
