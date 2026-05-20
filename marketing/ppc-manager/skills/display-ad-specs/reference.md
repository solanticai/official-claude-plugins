# Display Ad Specs — Reference

---

## 1. Google Ads image sizes (2026)

### Responsive Display Ads

| Purpose | Aspect ratio | Dimensions | Min count | Max file size |
|---|---|---|---|---|
| Marketing image (landscape) | 1.91:1 | 1200×628 px | 1 (≥5 recommended) | 5 MB |
| Marketing image (square) | 1:1 | 1200×1200 px | 1 (≥5 recommended) | 5 MB |
| Marketing image (portrait) | 4:5 | 960×1200 px | 0 (recommended) | 5 MB |
| Logo (square) | 1:1 | 128×128 px min, 1200×1200 recommended | 1 | 5 MB |
| Logo (landscape) | 4:1 | 512×128 px min, 1200×300 recommended | 0 (recommended) | 5 MB |

### Performance Max

Same as above but totals: **≥20 images across ≥3 aspect ratios** for best delivery. Minimum per asset group: 15.

### Video

| Aspect ratio | Dimensions | Length | Hosting |
|---|---|---|---|
| 16:9 (horizontal) | 1920×1080 | ≥10 sec | YouTube (public or unlisted) |
| 1:1 (square) | 1080×1080 | ≥10 sec | YouTube |
| 9:16 (vertical) | 1080×1920 | ≥10 sec | YouTube |

## 2. Safe zones

Text must stay within these margins from the edge:

- **Square (1:1, 1200×1200):** 60 px from each edge.
- **Landscape (1.91:1, 1200×628):** 50 px from each edge.
- **Portrait (4:5, 960×1200):** 40 px from each edge.

Reason: mobile UI chrome (navigation, share bar, CTA overlay) can cover 10–15% of each edge.

## 3. File formats

- **Preferred:** JPG for photography, PNG for logos and graphics.
- **Acceptable:** GIF (up to 150 KB, static or animated).
- **Not recommended:** WebP (accepted but inconsistent support).
- **Not allowed:** SVG, AVIF, HEIC.

## 4. Copy limits (2026)

| Asset | Limit |
|---|---|
| Short headline | 30 chars, 5 required for PMax |
| Long headline | 90 chars, 1–5 for PMax |
| Short description | 60 chars, 1 required |
| Long description | 90 chars, 1–4 |
| Business name | 25 chars |

## 5. Image content guidance

**Do:**
- Real photography of real products / real people / real environments.
- High-contrast, clean backgrounds.
- One clear focal point per image.
- Brand logo visible but not dominating.
- Text overlay ≤20% of image area if any.

**Don't:**
- Stock photos (visible in ML detection, hurts quality score).
- Collages of multiple products.
- Text-heavy images (Google may down-rank).
- Drastic colour shifts from the brand palette.
- Lifestyle shots with blurry or off-brand aesthetic.
- Over-processed HDR or oversaturated colours.

## 6. Naming convention

```
{brand}_{campaign}_{aspect}_{##}.{ext}
```

Examples:

- `koala_pmax-homewares-q2_square_01.jpg`
- `koala_pmax-homewares-q2_landscape_03.jpg`
- `koala_pmax-homewares-q2_portrait_05.jpg`
- `koala_pmax-homewares-q2_logo-square.png`
- `koala_pmax-homewares-q2_video-16x9.mp4`

## 7. Production checklist

- [ ] ≥15 images total
- [ ] ≥5 square 1:1
- [ ] ≥5 landscape 1.91:1
- [ ] ≥5 portrait 4:5 (recommended)
- [ ] ≥1 square logo (PNG, transparent)
- [ ] ≥1 landscape logo (PNG, transparent)
- [ ] ≥1 video (≥10 sec, YouTube-hosted)
- [ ] All files under 5 MB
- [ ] All files named per convention
- [ ] All copy assets ≤ limits (cross-check with `google-ads-copy` output)
- [ ] Safe zones respected
- [ ] No stock imagery
- [ ] Brand logo + palette match `brand-manager` spec
