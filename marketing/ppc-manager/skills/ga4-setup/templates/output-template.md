# GA4 Setup — {{property_display_name}}

**Property:** {{property_name}}
**Account:** {{account_name}} ({{account_id}})
**Date:** {{DD_MM_YYYY}}

---

## Snapshot

- **Currency:** {{currency_code}}
- **Time zone:** {{time_zone}}
- **Industry:** {{industry_category}}
- **Created:** {{create_time}}
- **Data streams:** {{stream_count}} ({{stream_types}})
- **Google Ads links:** {{ads_link_count}}

---

## Audit findings

### Already correct

| Area | Setting |
|---|---|
{{#already_correct}}
| {{area}} | {{setting}} |
{{/already_correct}}

### Needs fixing

| Area | Current | Desired | Severity | How to fix |
|---|---|---|---|---|
{{#fixes}}
| {{area}} | {{current}} | {{desired}} | {{severity}} | {{fix_method}} |
{{/fixes}}

### Manual steps (not automatable in v1.0)

1. {{manual_step_1}}
2. {{manual_step_2}}
3. …

---

## Changes applied via MCP

{{#mcp_changes}}
- **{{action}}** on `{{resource}}` — {{summary}}
{{/mcp_changes}}

---

## Smoke report (last 30 days)

| Event name | Event count |
|---|---|
{{#smoke_rows}}
| `{{eventName}}` | {{eventCount}} |
{{/smoke_rows}}

**Top 5 observations:**

1. {{observation_1}}
2. {{observation_2}}
3. {{observation_3}}
4. {{observation_4}}
5. {{observation_5}}

---

## Next steps

1. Run `/ppc-manager:ga4-events` to define the conversion taxonomy.
2. Run `/ppc-manager:google-ads-account-setup` to align Google Ads conversions.
3. Run `/ppc-manager:meta-events-mapping` to reconcile cross-platform events.
