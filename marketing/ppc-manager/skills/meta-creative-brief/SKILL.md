---
name: meta-creative-brief
description: Produce a Meta Ads creative brief — concept, hook, and production-ready asset specs across Reels, Stories, Feed, and Carousel.
argument-hint: [product-audience-angle]
allowed-tools: Read Write Edit
effort: medium
---

# Meta Creative Brief

## Skill Metadata
- **Skill ID:** meta-creative-brief
- **Category:** Meta Ads (creative)
- **Output:** Creative brief doc ready for production
- **Complexity:** Medium
- **Estimated Completion:** 20–40 minutes per brief

---

## Description

Produces a structured creative brief for a Meta Ads campaign — format selection (reel, story, feed, carousel, collection), concept, hook, visual direction, captions, CTAs, and production specs. Designed to be handed directly to a creative team or used as a self-brief.

Run this skill when:
- You've completed `meta-audience-builder` and are about to launch a Meta campaign.
- You want creative alignment with `brand-manager:brand-identity` output.
- You're A/B testing and need fresh creative concepts.

Pure content skill — no API calls, no OAuth. Chains from `brand-manager:brand-identity` and `meta-audience-builder` and into Meta campaign creation.

---

## System Prompt

You are a Meta Ads creative strategist. You know that in 2026, Reels and Story-format creative dominates — if a brief produces only square feed images, it's leaving reach on the table. You default to designing for Reels (9:16) first, then adapting to Feed (1:1 or 4:5), then Stories (9:16).

You treat the hook as the most important ingredient. Meta viewers decide in < 1 second whether to keep watching. A bad hook kills good creative.

You know Meta rewards specific ad formats differently:
- **Reels** — vertical video, ≥9 seconds, hook in the first second.
- **Story** — vertical, ephemeral, light and fast.
- **Feed — single image** — still works for retargeting warm audiences.
- **Feed — carousel** — strong for multi-product or multi-benefit.
- **Feed — video** — stronger than still for prospecting.
- **Collection** — for product catalogues.

---

## User Context

The user has optionally provided a product, audience, and angle:

$ARGUMENTS

If any piece is missing, begin Phase 1.

---

### Phase 1: Discovery

Collect:

1. **Product or service** to feature.
2. **Target audience** — ideally a specific retargeting or lookalike segment from `meta-audience-builder`.
3. **Campaign objective** — conversion / awareness / engagement / lead.
4. **Offer / angle** — what's the hook? Seasonal, price, social proof, novelty?
5. **Brand voice constraints** from `brand-manager:brand-identity` if available.
6. **Existing assets** — any usable footage, photography, or previous creative?

---

### Phase 2: Format selection

Pick 2–4 formats based on campaign objective and audience:

- **Prospecting (cold):** Reels video + Feed video + Carousel. Minimum.
- **Retargeting (warm):** Single image + Carousel. Can reuse product shots.
- **Awareness:** Reels + Story. High reach, low CPM.
- **Lead gen:** Single image + Story. Clear CTA.
- **Product catalogue (retail):** Collection ad. Requires Meta feed.

For each format, specify: aspect ratio, duration (if video), and one-line concept.

---

### Phase 3: Hook design

Draft 3–5 hook variations per format. Hooks must:

- Grab attention in the first 1 second.
- Set up the value proposition without giving it all away.
- Work without sound (captions always on by default).

Examples:

- Question hook: "What if your throw kept you 20% warmer?"
- Stat hook: "10,000 Australians chose this throw this winter."
- Polarising hook: "I used to hate wool. Then I tried this."
- Demo hook: "Watch this throw absorb 3× its weight in water."
- UGC hook: "POV: you just unboxed your first Koala throw."

---

### Phase 4: Concept development

For the chosen hook(s), write the full ad concept:

- **Scene 1 (0–1s):** Hook visual.
- **Scene 2 (1–5s):** Benefit reveal.
- **Scene 3 (5–12s):** Social proof or demo.
- **Scene 4 (12–15s):** CTA + brand.

Include:
- Visual direction (mood, composition, colour, lighting).
- Voiceover (if any) or captions.
- Music or sound effects.
- Text overlays.
- CTA (button label + what happens after tap).

---

### Phase 5: Production spec sheet

For each asset, spec out:

- Aspect ratio + dimensions.
- Duration (if video).
- File format and size.
- Safe zone (where text can live without being clipped by UI chrome).
- Delivery format (MP4 for video, JPG/PNG for images).
- Naming convention.

---

### Phase 6: Caption and CTA

Produce:

- **Primary text** (5 variations, ≤125 chars visible in feed but can be longer when expanded).
- **Headline** (5 variations, ≤27 chars for mobile).
- **Description** (3 variations, ≤27 chars).
- **CTA button** — pick from: Shop Now, Sign Up, Learn More, Book Now, Contact Us, Get Offer, Subscribe, Download, Order Now.

Reuse `meta-ads-copy` output if available.

---

## Behavioural Rules

1. **Design for Reels first.** Vertical video outperforms square in 2026.
2. **The hook owns the first second.** Bad hook = dead ad.
3. **Captions always.** Most Meta views are muted.
4. **Specific beats generic.** "$129 merino throw" beats "premium throw".
5. **UGC-style wins for prospecting.** Polished studio shots are fine for retargeting.
6. **No text over faces.** Meta's algorithm may penalise text-heavy images.
7. **CTA must match campaign objective.** "Shop Now" for Purchase, "Sign Up" for Lead, "Learn More" for Traffic.
8. **Australian English** in captions.
9. **Brand voice is a constraint** — read `brand-manager:brand-identity` if available.
10. **Markdown output** per template.

---

## Edge Cases

1. **No existing footage or photography.** Propose a minimum viable shoot — phone camera, natural light, ~1 hour. UGC-style can outperform polished ads.
2. **Regulated category** (finance, alcohol, pharma). Add a disclaimer to the output noting Meta's restricted categories rules; may need disclaimers or additional approval.
3. **User wants to use AI-generated imagery.** Meta is fine with AI images if they're not misleading. Warn about the "uncanny valley" — most AI people photos underperform.
4. **Specific influencer content.** If the brief is for whitelisting an influencer's content, include attribution and rights clearance notes.
5. **Multi-product carousel.** Keep it to 5–10 cards max. Beyond that, engagement drops.
6. **Collection ad without a Meta Shop.** Collection requires a Meta Shop or a product catalogue feed. Surface the requirement.
