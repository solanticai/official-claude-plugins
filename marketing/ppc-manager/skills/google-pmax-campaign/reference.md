# Google Performance Max — Reference

---

## 1. Asset group requirements (per group)

| Asset type | Min count | Max count | Size / constraint |
|---|---|---|---|
| Short headline | 3 | 5 | ≤30 chars |
| Long headline | 1 | 5 | ≤90 chars |
| Short description | 1 | 1 | ≤60 chars |
| Long description | 1 | 4 | ≤90 chars |
| Marketing image (square 1:1) | 1 | 20 | ≥1200×1200 px |
| Marketing image (landscape 1.91:1) | 1 | 20 | ≥1200×628 px |
| Marketing image (portrait 4:5) | 0 | 20 | ≥960×1200 px |
| Logo (square 1:1) | 1 | 5 | ≥128×128 px |
| Logo (landscape 4:1) | 0 | 5 | ≥512×128 px |
| Video | 0 (but do it) | 5 | ≥10 seconds, YouTube hosted |
| Business name | 1 | 1 | ≤25 chars |
| Final URL | 1 | N | one canonical URL per asset group |

## 2. Audience signal types

| Signal type | How to build | Strength |
|---|---|---|
| Customer list | Upload hashed email list via Audience Manager | Strongest |
| Website visitors (first-party) | GA4 audience or Google Ads remarketing tag | Very strong |
| Custom segment — search terms | List of 50+ high-intent search queries | Strong |
| Custom segment — URLs | Competitor / reviewer URLs | Medium |
| In-market interests | Google's pre-built segments | Medium |
| Affinity audiences | Google's pre-built broad-interest segments | Weak |
| Demographics (age/gender) | Google's defaults | Hint only |

## 3. Bidding strategy by goal

| Goal | Strategy | Target |
|---|---|---|
| Max revenue, high conversion volume | Maximize conversion value + tROAS | Start at 300%, tighten monthly |
| Max conversions, no value | Maximize conversions + tCPA | Start at 1.5× account avg CPA |
| Pure learning (<30 conv / 30 days) | Maximize conversion value (no target) | — |
| Customer acquisition | Max conv value + Customer Acquisition goal (new customers only) | — |

## 4. URL expansion exclusions

Always exclude:

```
*/blog/*
*/about/*
*/contact/*
*/faq/*
*/terms/*
*/privacy/*
*/careers/*
*/login*
*/admin/*
*/wp-*
```

Retail sites often also exclude out-of-stock pages via a Merchant Center custom_label.

## 5. Typical asset group blueprint

```
Asset group: Cosy Winter Throws
├── Headlines
│   ├── H1: "Koala Wool Throws" (short)
│   ├── H2: "Aussie-Made Warmth" (short)
│   ├── H3: "Natural Merino Blankets" (short)
│   ├── H4: "Timeless throws for every home, made in Australia" (long)
│   └── H5: "Shop handmade wool and linen throws from Koala & Co." (long)
├── Descriptions
│   ├── D1: "Shop Koala & Co. throws — free shipping over $150." (short)
│   ├── D2: "Handmade wool throws, curated linen blankets, natural fibres." (long)
│   └── D3: "Bring home the warmth. Shop the Koala throws collection now." (long)
├── Images
│   ├── square_01.jpg (product shot, lifestyle)
│   ├── square_02.jpg (lifestyle, bedroom)
│   ├── square_03.jpg (macro texture)
│   ├── landscape_01.jpg (hero shot)
│   ├── landscape_02.jpg (lifestyle, living room)
│   └── … 10+ more
├── Videos
│   └── YouTube: "Koala Throws — Winter 2026" (30 seconds, hosted on brand channel)
├── Logo
│   ├── square: koala_logo_square.png
│   └── landscape: koala_logo_landscape.png
├── Audience signal
│   └── Customer list "Throw buyers 2025" + custom segment "wool throw searches"
└── Final URL
    └── https://koalahomewares.com.au/collections/throws
```
