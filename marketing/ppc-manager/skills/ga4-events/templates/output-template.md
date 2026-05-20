# GA4 Events — {{property_display_name}}

**Property:** {{property_id}}
**Date:** {{DD_MM_YYYY}}

---

## Event inventory (last 30 days)

| Event name | Event count | Source | Conversion? |
|---|---|---|---|
{{#event_inventory}}
| `{{name}}` | {{count}} | {{source}} | {{is_conversion}} |
{{/event_inventory}}

---

## Conversions

### Already marked

| Event name | Marked at |
|---|---|
{{#existing_conversions}}
| `{{event_name}}` | {{create_time}} |
{{/existing_conversions}}

### Newly marked

| Event name | Rationale | Google Ads import? |
|---|---|---|
{{#new_conversions}}
| `{{event_name}}` | {{rationale}} | {{import}} |
{{/new_conversions}}

---

## Custom dimensions

### Already exist

| Parameter name | Display name | Scope |
|---|---|---|
{{#existing_dimensions}}
| `{{parameter_name}}` | {{display_name}} | {{scope}} |
{{/existing_dimensions}}

### Newly created

| Parameter name | Display name | Scope | Rationale |
|---|---|---|---|
{{#new_dimensions}}
| `{{parameter_name}}` | {{display_name}} | {{scope}} | {{rationale}} |
{{/new_dimensions}}

---

## Custom metrics

{{#new_metrics}}
- **{{parameter_name}}** — {{display_name}} ({{measurement_unit}}, {{scope}}): {{rationale}}
{{/new_metrics}}

---

## DebugView verification

For each newly-marked conversion:

1. Open `{{debug_url_example}}` in Chrome.
2. Perform the action: {{action_description}}.
3. Admin → DebugView — confirm the event appears within 10 seconds.
4. Click the event — confirm these params are present: {{expected_params}}.
5. Mark verified: {{verified_at}}.

---

## Open issues to revisit later

1. {{issue_1}}
2. {{issue_2}}

---

## Next steps

1. Wait 24 hours, then re-run `/ppc-manager:ga4-events` in audit mode to confirm the new conversions are accumulating data.
2. Run `/ppc-manager:google-ads-account-setup` to import the GA4 conversions into Google Ads.
3. Run `/ppc-manager:meta-events-mapping` to reconcile the taxonomy with Meta Pixel and CAPI.
