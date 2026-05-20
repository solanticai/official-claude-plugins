# GTM Setup — Change Log — {{container_name}}

**Container:** {{container_public_id}} ({{container_id}})
**Account:** {{account_name}} ({{account_id}})
**Workspace:** {{workspace_name}}
**Version:** {{version_name}} ({{version_id}}) — **{{version_status}}**
**Date:** {{DD_MM_YYYY}}

---

## Summary

{{one_paragraph_summary}}

---

## Baseline status

| Item | Before | After |
|---|---|---|
| GA4 Configuration tag | {{before_ga4_config}} | {{after_ga4_config}} |
| All Pages trigger | {{before_page_view}} | {{after_page_view}} |
| Consent Mode v2 stub | {{before_consent}} | {{after_consent}} |
| Legacy UA tags | {{before_ua}} | {{after_ua}} |
| Naming convention compliance | {{before_naming}}% | {{after_naming}}% |

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

| Name | Type | Firing trigger |
|---|---|---|
{{#tags_created}}
| {{name}} | {{type}} | {{trigger}} |
{{/tags_created}}

### Tags renamed

| Old name | New name |
|---|---|
{{#tags_renamed}}
| {{old}} | {{new}} |
{{/tags_renamed}}

### Tags deleted

| Name | Reason |
|---|---|
{{#tags_deleted}}
| {{name}} | {{reason}} |
{{/tags_deleted}}

---

## Preview & verification

- **Tag Assistant preview URL:** {{preview_url}}
- **Verification steps:** open the preview URL, confirm the GA4 Config tag fires on Page View, check GA4 DebugView for the corresponding page_view event.

---

## Recommended next steps

1. Run `/ppc-manager:gtm-datalayer` to design the dataLayer schema.
2. Run `/ppc-manager:ga4-events` to wire events end-to-end.
3. Run `/ppc-manager:meta-pixel-setup` if using Meta Ads.
