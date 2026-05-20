# YouTube Campaign — Koala Winter Throws Launch

**Goal:** Awareness + consideration + action (full-funnel launch)
**Budget:** AUD 150 / day (split across 3 campaigns)
**Formats:** Bumper + Skippable In-Stream + Video Action
**Date:** 11/04/2026

---

## Campaigns

### Koala - YouTube - Awareness - Winter 2026

- **Format:** Bumper (6s non-skippable)
- **Bidding:** tCPM AUD 8
- **Audience:** Affinity "Home Decor Enthusiasts" + Demo 30–55 + AU only
- **Video asset:** 6s bumper (vertical + horizontal versions)
- **Landing page:** n/a (no click, recall is the goal)
- **Daily budget:** AUD 50

### Koala - YouTube - Consideration - Winter 2026

- **Format:** Skippable In-Stream
- **Bidding:** Max CPV (target CPV AUD 0.08)
- **Audience:** Custom segment "wool throw intent" (50 seed keywords from `keyword-research`) + Remarketing (All website visitors 180d)
- **Video asset:** 30s skippable video (horizontal + vertical)
- **Landing page:** `https://koalahomewares.com.au/collections/throws`
- **Daily budget:** AUD 60

### Koala - YouTube - Action - Winter 2026

- **Format:** Video Action (Skippable In-Stream with CTA card)
- **Bidding:** Maximize conversions, tCPA AUD 45
- **Audience:** Lookalike Purchasers 1% (from `meta-audience-builder`) + Custom intent
- **Video asset:** 30s action-focused video with end card
- **Landing page:** `https://koalahomewares.com.au/collections/throws`
- **Daily budget:** AUD 40

---

## Video asset briefs

### 6s Bumper (horizontal + vertical)

- **Duration:** 6 seconds
- **Aspect:** 16:9 and 9:16 (two versions)
- **Dimensions:** 1920×1080 / 1080×1920
- **Hook:** Close-up of wool throw texture on a couch, morning sunlight
- **Scene-by-scene:**
  - 0–2s: Texture close-up + text "Koala Wool Throws"
  - 2–4s: Wider shot — throw on couch, styled bedroom
  - 4–6s: Brand logo + URL overlay
- **CTA:** (none — bumper is non-clickable)

### 30s Skippable In-Stream

- **Duration:** 30 seconds
- **Aspect:** 16:9 primary + 9:16 for mobile
- **Dimensions:** 1920×1080 / 1080×1920
- **Hook:** "Every Australian winter, the same problem: thin blankets, synthetic throws that pill." (shown with matching visuals)
- **Scene-by-scene:**
  - 0–5s: Hook + problem visualised
  - 5–10s: Reveal the Koala wool throw
  - 10–18s: Value props — handmade, merino, Australian-made (text overlays)
  - 18–25s: Social proof — "10,000 Australian homes"
  - 25–30s: CTA — "Shop Koala throws" + URL + brand logo
- **CTA:** "Shop Now" end card with `koalahomewares.com.au`

### 30s Video Action (same video, different end card)

- Same as above but with Google Ads CTA overlay from second 10 onwards, URL clickable throughout.

---

## Companion banner

- **Dimensions:** 300×60 px
- **File:** `koala_companion_banner_2026_winter.jpg`
- **CTA:** "Shop Koala throws" with brand logo and URL

---

## Readiness checklist

- [x] YouTube channel linked to Google Ads (via `google-ads-account-setup`)
- [ ] Videos uploaded — **pending** production on 18/04/2026
- [x] Videos meet format minimums (6s bumper + 30s skippable)
- [x] Landing page works (`https://koalahomewares.com.au/collections/throws`)
- [ ] Companion banner uploaded — **pending** design on 15/04/2026
- [x] Conversion tracking imported (GA4 `purchase` is Primary conversion)
- [x] Audience defined
- [x] Budget approved ($150/day total, $4,500/month)

---

## Next steps

1. Complete video production (shoot 16/04, edit 17/04, delivery 18/04).
2. Upload all 3 videos to the Koala & Co. YouTube channel (unlisted).
3. Create the 3 campaigns in Google Ads UI:
   - Awareness → New campaign → Awareness and consideration → Video → Efficient reach → pick Bumper.
   - Consideration → Video → Consideration → Skippable In-Stream.
   - Action → Video → Sales → Video Action.
4. Add video URLs, audiences, bidding.
5. Launch in PAUSED, verify configuration, then enable.
6. Run `/ppc-manager:campaign-audit --scope youtube` on day 15 to review initial performance.
