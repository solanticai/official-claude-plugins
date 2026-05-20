# Google Performance Max Campaign — Koala - PMax - Homewares Q2

**Customer:** 1234567890 (Koala & Co. AU)
**Campaign:** Koala - PMax - Homewares Q2
**Budget:** AUD 150.00 / day
**Bidding:** Maximize conversion value, no tROAS for first 30 days
**Status:** draft (manual setup required in v1.0)
**Date:** 11/04/2026

---

## Asset groups

### Cosy Winter Throws

- **Theme:** Winter warmth, natural fibres, bedroom lifestyle
- **Final URL:** https://koalahomewares.com.au/collections/throws
- **Audience signal:** Customer list "Throws buyers 2024-2025" + custom segment "wool/linen throw searches" (50+ seed queries)

**Headlines (short):**
1. Koala Wool Throws
2. Aussie Made Warmth
3. Merino & Linen Throws
4. Shop Handmade Throws
5. Free Shipping Over $150

**Headlines (long):**
1. Handmade wool and linen throws for the Australian winter
2. Shop Koala & Co. throws — natural fibres, timeless design
3. Premium merino and linen throws, made in Australia

**Descriptions:**
- Shop Koala throws online — free shipping over $150. (53 chars, short)
- Handmade wool and linen throws, curated for Australian homes. (62 chars, long)
- Natural, timeless, and warm. Shop the Koala throws collection. (63 chars, long)

**Image brief:** 20 images total — 10 square (1200×1200) and 10 landscape (1200×628). Mix of hero product shots (5), styled bedroom lifestyle (7), and macro texture / material detail (8). Warm palette (rust, ochre, ivory, charcoal). All photography in-house — no stock.

**Video brief:** 1× 30-second hero video showcasing the throws collection — slow pans, soft morning light, 2–3 scene cuts, no voiceover, text overlay with brand + tagline + URL. Upload to Koala & Co. YouTube channel.

### Living Room Rugs

- **Theme:** Living room refresh, natural texture, family rooms
- **Final URL:** https://koalahomewares.com.au/collections/rugs
- **Audience signal:** Customer list "Rug buyers 2024-2025" + URL visits to `kmart.com.au/rugs`, `fantasticfurniture.com.au/rugs`, `adairs.com.au/rugs`

(... same structure as above)

### Cushion Collection

(... same structure)

---

## URL expansion exclusions

```
koalahomewares.com.au/blog/*
koalahomewares.com.au/about
koalahomewares.com.au/contact
koalahomewares.com.au/shipping-returns
koalahomewares.com.au/terms
koalahomewares.com.au/privacy
koalahomewares.com.au/account/*
```

---

## Merchant Center feed filter (retail)

Include:
- `product_type CONTAINS "Throws"` OR `product_type CONTAINS "Rugs"` OR `product_type CONTAINS "Cushions"`
- `custom_label_0 != "clearance"` (exclude sunset stock)
- `price > 79.00` (exclude low-margin accessories)

---

## Readiness checklist

- [x] Merchant Center linked and feed approved
- [x] Conversion actions Primary with values (GA4 `purchase` with `value` field)
- [ ] ≥15 images per asset group — **not yet ready**, photo shoot scheduled 18/04/2026
- [ ] ≥1 video per asset group — **not yet ready**, video production week of 22/04/2026
- [x] Audience signals defined
- [x] URL expansion exclusions configured
- [x] Daily budget approved
- [x] Learning period expectations set (no judgement until 2 weeks in)

---

## Next steps

1. Complete photo and video production (scheduled 18–26/04/2026).
2. Create the campaign manually in Google Ads UI → Campaigns → New campaign → Sales → Performance Max.
3. Paste each asset group's inputs exactly as specified above.
4. Upload Merchant Center feed with the filter above.
5. Launch in PAUSED.
6. Review together before enabling.
7. Run `/ppc-manager:campaign-audit --scope pmax` on day 15 (not earlier — first 2 weeks are learning).
