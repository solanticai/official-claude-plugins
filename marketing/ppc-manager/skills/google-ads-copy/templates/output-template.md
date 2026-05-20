# Google Ads Copy — {{product}} (for {{audience}})

**Brand:** {{brand}}
**Angle:** {{angle}}
**Final URL:** {{final_url}}
**Voice:** {{voice_summary}}
**Date:** {{DD_MM_YYYY}}

---

## Headlines (15)

| # | Headline | Chars | Pin |
|---|---|---|---|
{{#headlines}}
| {{n}} | {{text}} | {{chars}} | {{pin}} |
{{/headlines}}

**Pin rationale:**

- **H1:** {{h1_rationale}}
- **H2:** {{h2_rationale}}
- **H3:** {{h3_rationale}}

---

## Descriptions (4)

| # | Description | Chars | Purpose |
|---|---|---|---|
{{#descriptions}}
| {{n}} | {{text}} | {{chars}} | {{purpose}} |
{{/descriptions}}

---

## Path fields

- **Path 1:** `{{path1}}` ({{path1_chars}}/15)
- **Path 2:** `{{path2}}` ({{path2_chars}}/15)

---

## Sitelinks (6)

| # | Headline | Description 1 | Description 2 | Link |
|---|---|---|---|---|
{{#sitelinks}}
| {{n}} | {{headline}} ({{hchars}}/25) | {{desc1}} ({{d1chars}}/35) | {{desc2}} ({{d2chars}}/35) | {{url}} |
{{/sitelinks}}

---

## Callouts (5)

| # | Callout | Chars |
|---|---|---|
{{#callouts}}
| {{n}} | {{text}} | {{chars}}/25 |
{{/callouts}}

---

## QA summary

Every asset within limits: {{qa_pass}}. Total assets: {{total_assets}}.

---

## Next steps

1. Paste into `/ppc-manager:google-search-campaign` or `/ppc-manager:google-pmax-campaign`.
2. Run `/ppc-manager:landing-page-copy` to align landing page messaging with this ad copy.
