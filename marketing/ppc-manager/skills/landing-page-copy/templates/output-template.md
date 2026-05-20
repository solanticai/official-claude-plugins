# Landing Page Copy — {{page_name}}

**Product/offer:** {{product_offer}}
**Ad angle:** {{ad_angle}}
**Audience:** {{audience}}
**Funnel stage:** {{funnel_stage}}
**Structure:** {{structure_type}}
**Word count target:** {{word_count_target}}
**Date:** {{DD_MM_YYYY}}

---

## Hero

**Headline:** {{hero_headline}}

**Subheadline:** {{hero_subheadline}}

**Primary CTA:** {{primary_cta}}

**Hero visual brief:** {{hero_visual_brief}}

---

## Value propositions

{{#value_props}}
### {{headline}}

{{body}}

*Supporting fact: {{fact}}*

{{/value_props}}

---

## Social proof

{{#testimonials}}
> "{{quote}}"
> — {{attribution}}

{{/testimonials}}

**Trust badges:** {{trust_badges}}

---

## Objection handling

{{#objections}}
### {{objection_headline}}

{{objection_body}}

{{/objections}}

---

## Pricing / offer

{{pricing_section}}

---

## FAQ

{{#faqs}}
**Q:** {{question}}

**A:** {{answer}}

{{/faqs}}

---

## Final CTA

{{final_cta_copy}}

**Button:** {{final_cta_button}}

---

## Scent trail cross-reference

| Ad copy element | Landing page section | Match |
|---|---|---|
{{#scent_trail}}
| {{ad_element}} | {{page_section}} | {{match}} |
{{/scent_trail}}

---

## CRO checklist

- [{{cta_above_fold}}] Primary CTA above the fold
- [{{single_cta}}] Single primary CTA
- [{{mobile_opt}}] Mobile-optimised (short paragraphs)
- [{{trust_signals}}] Trust signals visible
- [{{loading_speed}}] No heavy hero video
- [{{value_3sec}}] Clear value prop in first 3 seconds
- [{{no_stock}}] No generic stock imagery
- [{{price_clear}}] Price clear and unambiguous
- [{{returns}}] Return/guarantee policy visible

---

## Next steps

1. Pass copy to designer / developer for implementation.
2. Run `/ppc-manager:display-ad-specs` to align visual direction.
3. After launch, monitor via `/ppc-manager:campaign-audit` weekly.
