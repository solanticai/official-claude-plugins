# Keyword Research — Reference

## 1. Match type strategy

| Match type | When | Expected CTR | Expected conversion rate |
|---|---|---|---|
| Exact `[keyword]` | Brand, specific product names | 3–6% | 4–8% |
| Phrase `"keyword"` | Most keywords (default) | 2–4% | 2–5% |
| Broad `keyword` | Only with Smart Bidding + strong negative list | 0.5–2% | 0.5–3% |

**Rule:** 70% Phrase / 25% Exact / 5% Broad for new campaigns.

## 2. Commercial intent classification

| Signal | Intent | Examples |
|---|---|---|
| "buy", "order", "shop" | Purchase | `buy wool throw` |
| "best", "top", "vs" | Research | `best wool throws australia` |
| "cheap", "sale", "discount" | Price-sensitive | (often low margin — add to negatives for premium brands) |
| "how to", "tutorial" | Informational (low intent) | (usually add as negative) |
| "review", "rating" | Research | `koala throw review` (defensive bidding) |
| "jobs", "career" | Not in-market | always negative |

## 3. Seed list template

For an AU homewares retailer selling wool throws:

```
wool throw
wool throw blanket
merino throw
merino wool throw
throw blanket australia
cosy throw
winter throw
natural wool throw
handmade throw blanket
australian made throw
```

10 seeds. Mix of specific product terms, qualifiers, and origin modifiers. Not too narrow (just one seed word), not too broad (just "throw").

## 4. Canonical negative keyword list (generic)

```
free
cheap
cheapest
wholesale
bulk
job
jobs
career
hire
internship
diy
tutorial
how to
youtube
wikipedia
craigslist
gumtree
facebook marketplace
ebay
review
reviews
recall
lawsuit
complaint
```

## 5. CPC benchmarks (AU, 2026, selected verticals)

| Vertical | Low end | High end |
|---|---|---|
| Homewares / furniture | $0.80 | $2.50 |
| Fashion / apparel | $0.50 | $1.80 |
| Professional services | $3.00 | $15.00 |
| Insurance | $15.00 | $60.00 |
| Legal (personal injury) | $30.00 | $200.00 |
| Trades (plumber, electrician) | $5.00 | $20.00 |
| SaaS (SMB) | $4.00 | $20.00 |
| Local services (food, café) | $1.00 | $3.00 |

These are rough ranges. Real bids vary with quality score, bid strategy, and competition.

## 6. Google Ads language + geo IDs

- `language_id=1000` → English
- `geo_target_id=2036` → Australia
- `geo_target_id=2840` → United States
- `geo_target_id=2826` → United Kingdom
- `geo_target_id=2554` → New Zealand
- `geo_target_id=2724` → Spain
- `geo_target_id=2250` → France

See [developers.google.com/google-ads/api/reference/data/geotargets](https://developers.google.com/google-ads/api/reference/data/geotargets) for the full list.
