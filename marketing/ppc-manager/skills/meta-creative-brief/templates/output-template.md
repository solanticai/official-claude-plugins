# Meta Creative Brief — {{product}} — {{audience}}

**Brand:** {{brand}}
**Product:** {{product}}
**Audience:** {{audience}}
**Objective:** {{objective}}
**Angle:** {{angle}}
**Date:** {{DD_MM_YYYY}}

---

## Formats

{{#formats}}
### {{format_name}} — {{aspect}}

- **Concept:** {{concept}}
- **Duration:** {{duration}}
- **Hook:** {{hook}}

{{/formats}}

---

## Scene-by-scene (primary Reel)

| Time | Visual | Audio | Text overlay |
|---|---|---|---|
{{#scenes}}
| {{time}} | {{visual}} | {{audio}} | {{overlay}} |
{{/scenes}}

---

## Captions

### Primary text (5 variations)

{{#primary_texts}}
- {{text}} ({{chars}} chars)
{{/primary_texts}}

### Headlines (5 variations)

{{#headlines}}
- {{text}} ({{chars}}/27 chars)
{{/headlines}}

### Descriptions (3 variations)

{{#descriptions}}
- {{text}} ({{chars}}/27 chars)
{{/descriptions}}

### CTA button

{{cta_button}}

---

## Production spec

{{#production_specs}}
- **{{asset}}:** {{specs}}
{{/production_specs}}

---

## Brand and voice constraints

{{voice_constraints}}

---

## Timeline

- Script lock: {{script_lock_date}}
- Shoot: {{shoot_date}}
- Edit: {{edit_date}}
- Delivery: {{delivery_date}}

---

## Next steps

1. Run `/ppc-manager:meta-ads-copy` for finalised copy variants.
2. Pass this brief to the production team.
3. Upload assets to `/ppc-manager:meta-creative-brief` output → Meta Ads creative via `ppc-meta:create_creative`.
