# YouTube Campaign — Reference

## 1. Format matrix (2026)

| Format | Length | Aspect | Bidding | Use for |
|---|---|---|---|---|
| Bumper ad | ≤6 sec non-skippable | 16:9 or 9:16 | Target CPM (tCPM) | Awareness, high-frequency reach |
| Skippable In-Stream | 12 sec minimum, 3 min max (60s recommended) | 16:9 or 9:16 | Maximum CPV (cost-per-view) | Consideration, awareness |
| Non-Skippable In-Stream | 15 sec (or 20s in some regions) | 16:9 or 9:16 | tCPM | Rarely — lower engagement |
| In-Feed Video (formerly TrueView Discovery) | any length | 16:9 | Max CPV | Consideration |
| YouTube Shorts | ≤60 sec | 9:16 | CPV or CPM | Mobile-first, younger audience |
| Video Action | 10–60 sec | 16:9 or 9:16 | Maximize conversions / tCPA | Conversions — e-commerce, lead-gen |
| Masthead | any | 16:9 | Fixed-price (sold via Google sales) | Launch day reach, not self-serve |

## 2. Video asset specs

| Format | Dimensions | File format |
|---|---|---|
| 16:9 | 1920×1080 | MP4 H.264 or H.265, YouTube-hosted |
| 9:16 Shorts | 1080×1920 | MP4 |
| Square | 1080×1080 | MP4 (for some placements) |
| Thumbnail | 1280×720 | JPG/PNG |
| Companion banner | 300×60 | JPG/PNG, ≤150 KB |

All videos must be **hosted on YouTube** (not uploaded to Google Ads directly). Unlisted visibility is fine if the video shouldn't appear on the channel's public feed.

## 3. Bidding strategies

| Strategy | Format | Use when |
|---|---|---|
| tCPM (target CPM) | Bumper, Non-Skippable | Default for reach campaigns |
| Max CPV | Skippable In-Stream, In-Feed | Default for view-through engagement |
| Max conversions | Video Action | >30 conversions/30 days |
| tCPA | Video Action | Cost-per-acquisition target, >30 conv/30 days |
| tROAS | Video Action | Revenue optimisation, >50 conv with values |

## 4. Audience layering

Best combinations by goal:

### Awareness

- Affinity (broad) + Demographics (age / gender)
- Topics (YouTube content categories the audience watches)
- Placements (specific channels, only for highly targeted brand alignment)

### Consideration

- Custom segment — keywords (from `keyword-research`)
- In-market audiences (e.g. "Home & Garden > Furnishings")
- Remarketing — website visitors, YouTube channel engagers

### Action (conversion)

- Custom segment — keywords + URLs
- Customer lists (first-party)
- Remarketing — cart abandoners, purchaser lookalikes

## 5. Creative structure (Skippable In-Stream)

```
0–1s:    HOOK — visual attention grabber
1–5s:    HOOK carries to prevent skip
5–10s:   Identify problem / show product
10–15s:  Value prop, proof, benefit
15–25s:  Demo / social proof
25–30s:  CTA + offer
```

After second 5, viewers who haven't skipped are qualified audience.

## 6. Brand lift measurement

Google Ads offers Brand Lift studies for campaigns ≥$5,000 AUD. They measure:

- Ad recall
- Brand awareness
- Consideration
- Favourability
- Purchase intent

Request when setting up the campaign. Requires ~2 weeks of data. No manual action beyond enabling.

## 7. Typical campaign structure

```
Campaign: Koala - YouTube - Awareness - Q2 2026
  └── Ad group: Bumper - AU Homeowners
        ├── Audience: Affinity - Home Decor + Demo 30-55
        ├── Bumper video (6s horizontal + 6s vertical)
        └── tCPM $8

Campaign: Koala - YouTube - Consideration - Q2 2026
  └── Ad group: Skippable - Custom Intent
        ├── Audience: Custom segment "wool throw searches" + Remarketing
        ├── Skippable In-Stream video (30s)
        ├── Companion banner 300×60
        └── Max CPV $0.08

Campaign: Koala - YouTube - Action - Q2 2026
  └── Ad group: Video Action - Purchasers LAL
        ├── Audience: Lookalike Purchasers 1% + Custom segment
        ├── Video Action video (30s with CTA overlay)
        └── Maximize conversions with tCPA $45
```
