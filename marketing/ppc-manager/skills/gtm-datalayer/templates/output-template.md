# DataLayer Schema — {{site_name}}

**Site type:** {{site_type}}
**Container:** {{container_public_id}}
**Date:** {{DD_MM_YYYY}}

---

## Summary

{{one_paragraph_summary}}

---

## Event catalogue

| Event | Trigger | Required params | Optional params | Purpose |
|---|---|---|---|---|
{{#events}}
| `{{name}}` | {{trigger}} | {{required}} | {{optional}} | {{purpose}} |
{{/events}}

---

## Schema per event

{{#events}}
### `{{name}}`

**Trigger:** {{trigger_description}}

**Schema:**

| Field | Type | Required | Example | Notes |
|---|---|---|---|---|
{{#fields}}
| `{{name}}` | {{type}} | {{required}} | `{{example}}` | {{notes}} |
{{/fields}}

**Inline push:**

```js
window.dataLayer = window.dataLayer || [];
window.dataLayer.push({{inline_example}});
```

{{/events}}

---

## Helper function

Recommended pattern for React/Vue/Angular/SPA sites:

```js
{{helper_function_code}}
```

Usage:

```js
{{helper_usage_example}}
```

---

## GTM data layer variables created

| Variable name | Data layer key | Status |
|---|---|---|
{{#variables_created}}
| {{name}} | `{{key}}` | {{status}} |
{{/variables_created}}

---

## Rollout checklist for the dev team

1. Copy the helper function into `src/analytics.js` (or equivalent).
2. Wire each event's trigger to a `trackEvent(...)` call.
3. Verify in GTM Preview mode that each event appears with the documented params.
4. Compare against GA4 DebugView — each event should appear with the right `event_name` and `event_params`.
5. Once verified, pair with the `ga4-events` skill to mark conversions and add custom dims/metrics.

---

## Next steps

1. Run `/ppc-manager:ga4-events` to register the conversion events and dimensions.
2. Run `/ppc-manager:gtm-tags` to create the platform-specific tags (Meta Pixel event tags, Google Ads conversion tags) that consume these dataLayer variables.
3. Run `/ppc-manager:meta-events-mapping` to reconcile this schema against Meta Pixel and CAPI.
