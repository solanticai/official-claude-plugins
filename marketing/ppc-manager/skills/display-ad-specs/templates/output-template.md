# Display Ad Specs — {{brand}} — {{campaign_name}}

**Campaign type:** {{campaign_type}}
**Product:** {{product}}
**Mood:** {{mood}}
**CTA:** {{cta}}
**Deadline:** {{deadline}}
**Date:** {{DD_MM_YYYY}}

---

## Image spec matrix

| Purpose | Aspect ratio | Dimensions | Min count | File size | Safe zone |
|---|---|---|---|---|---|
{{#image_specs}}
| {{purpose}} | {{aspect}} | {{dimensions}} | {{min}} | {{max_size}} | {{safe_zone}} |
{{/image_specs}}

---

## Logo specs

- **Square:** {{logo_square_dims}}, PNG transparent, ≤5 MB
- **Landscape:** {{logo_landscape_dims}}, PNG transparent, ≤5 MB

---

## Video spec

- **Aspect ratio:** {{video_aspect}}
- **Dimensions:** {{video_dimensions}}
- **Length:** ≥{{video_min_length}} seconds
- **Hosting:** YouTube ({{youtube_visibility}})

---

## Copy assets

### Short headlines (5, ≤30 chars)

{{#short_headlines}}
- {{text}} ({{chars}}/30)
{{/short_headlines}}

### Long headlines (5, ≤90 chars)

{{#long_headlines}}
- {{text}} ({{chars}}/90)
{{/long_headlines}}

### Descriptions

- **Short (1, ≤60 chars):** {{short_description}} ({{short_chars}}/60)

**Long (4, ≤90 chars):**
{{#long_descriptions}}
- {{text}} ({{chars}}/90)
{{/long_descriptions}}

---

## Designer brief

### Brand context

{{brand_context_paragraph}}

### Composition

{{composition_paragraph}}

### Do-not list

- {{dont_1}}
- {{dont_2}}
- {{dont_3}}

### Production notes

- Shoot list: {{shoot_list}}
- Delivery format: {{delivery_format}}
- File naming: `{{naming_convention}}`
- Deadline: {{deadline}}

---

## Production checklist

- [ ] ≥15 images total
- [ ] ≥5 square 1:1
- [ ] ≥5 landscape 1.91:1
- [ ] ≥5 portrait 4:5
- [ ] Square logo (PNG transparent)
- [ ] Landscape logo (PNG transparent)
- [ ] Video ≥10 sec, YouTube-hosted
- [ ] All files ≤5 MB
- [ ] Naming convention applied
- [ ] Safe zones respected
- [ ] No stock imagery
- [ ] Brand palette honoured

---

## Next steps

1. Brief the designer. Confirm deadline and deliverables.
2. QA delivered assets against the checklist.
3. Paste into `/ppc-manager:google-pmax-campaign` as asset group inputs.
