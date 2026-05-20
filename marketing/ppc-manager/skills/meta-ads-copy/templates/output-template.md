# Meta Ads Copy — {{product}} — {{audience}}

**Brand:** {{brand}}
**Objective:** {{objective}}
**CTA button:** {{cta_button}}
**Date:** {{DD_MM_YYYY}}

---

## Primary text (6 variations)

{{#primary_texts}}
### {{angle}}

{{text}}

*{{visible_before_cutoff}} chars visible before "See more" • {{total_chars}} total*

{{/primary_texts}}

---

## Headlines (5, ≤27 chars)

{{#headlines}}
- {{text}} ({{chars}}/27)
{{/headlines}}

---

## Descriptions (3, ≤27 chars)

{{#descriptions}}
- {{text}} ({{chars}}/27)
{{/descriptions}}

---

## A/B test matrix

| Variant | Primary text | Headline | Description |
|---|---|---|---|
{{#ab_matrix}}
| {{variant}} | {{primary}} | {{headline}} | {{description}} |
{{/ab_matrix}}

---

## QA summary

- **All within character limits:** {{qa_pass}}
- **Emoji count:** {{emoji_count}}
- **Voice consistency with brand-manager:** {{voice_match}}

---

## Next steps

1. Paste into `/ppc-manager:meta-creative-brief` output for final production brief.
2. Upload via `ppc-meta:create_creative` once creative assets are ready.
3. Launch A/B test with 2 variants per ad set.
