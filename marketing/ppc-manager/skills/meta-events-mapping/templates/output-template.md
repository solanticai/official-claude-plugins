# Event Dictionary — {{business_name}}

**Date:** {{DD_MM_YYYY}}
**Owner:** {{owner}}

---

## Canonical events

| Business event | GA4 | Meta Pixel | Meta CAPI | GTM DL | Notes |
|---|---|---|---|---|---|
{{#events}}
| {{business_name}} | `{{ga4}}` | `{{pixel}}` | `{{capi}}` | `{{gtm}}` | {{notes}} |
{{/events}}

---

## Param schemas per event

{{#events}}
### {{business_name}} ({{ga4}})

**GA4 params:**
{{#ga4_params}}
- `{{name}}` ({{type}}): {{notes}}
{{/ga4_params}}

**Meta Pixel params:**
{{#pixel_params}}
- `{{name}}`: {{notes}}
{{/pixel_params}}

**Meta CAPI `custom_data`:**
{{#capi_params}}
- `{{name}}`: {{notes}}
{{/capi_params}}

{{/events}}

---

## Inconsistencies found

| Finding | Severity | Fix |
|---|---|---|
{{#findings}}
| {{finding}} | {{severity}} | {{fix}} |
{{/findings}}

---

## Next steps

1. Circulate this doc to dev + marketing as the canonical reference.
2. Run `/ppc-manager:campaign-audit` to verify every event flows correctly across all platforms.
