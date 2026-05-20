# Google Search Campaign — Reference

---

## 1. Match type cheat sheet

| Match type | Syntax | When to use |
|---|---|---|
| Exact | `[keyword]` | High-intent brand and product terms you want to defend |
| Phrase | `"keyword"` | Default for most keywords |
| Broad | `keyword` | Only with Smart Bidding + large negative list |

**Rule:** start with 70% Phrase, 25% Exact, 5% Broad. Iterate from there.

## 2. Responsive Search Ad (RSA) structure

- **Headlines:** 15 max, 30 chars each.
- **Descriptions:** 4 max, 90 chars each.
- **Pinning positions:** HEADLINE_1 / HEADLINE_2 / HEADLINE_3, DESCRIPTION_1 / DESCRIPTION_2.
- **Path fields:** 15 chars each, affects display URL.

Google tests combinations and picks the best performers. Over-pinning defeats the point — pin only the ones that must appear in a specific slot (brand, USP, CTA).

## 3. Canonical negative keyword list (v1)

Install these on every new Search campaign:

```
free
cheap
cheapest
wholesale
job
jobs
career
careers
intern
review
reviews
recall
lawsuit
complaint
diy
how to
tutorial
youtube
wikipedia
craigslist
gumtree
facebook marketplace
```

## 4. Ad group naming convention

`{Brand} - Search - {Category} - {Intent}`

Examples:
- `Koala - Search - Throws - Generic`
- `Koala - Search - Throws - Branded`
- `Koala - Search - Cushions - Generic`

## 5. Quality Score factors

Quality Score is Google Ads' internal scoring of each keyword. It has three components:

| Component | Driver |
|---|---|
| Expected CTR | Historic CTR of keyword + RSA combo |
| Ad relevance | How well RSA headlines / descriptions match the keyword |
| Landing page experience | Page load speed, mobile-friendliness, content relevance to keyword |

Low Quality Score → higher CPCs. High Quality Score → lower CPCs, better positions.

## 6. Budget guidance

| Daily budget | Campaign expected to produce |
|---|---|
| < $20 | Too little for most Search campaigns; consider pausing |
| $20–$50 | OK for narrow verticals (local services), too thin for e-commerce |
| $50–$200 | Normal for SMB e-commerce |
| $200+ | Mid-market; can support multiple concurrent campaigns |

## 7. Typical campaign structure for an AU homewares retailer

```
Campaign: Koala - Search - Generic
├── Ad group: Throws - Wool
│   ├── Keywords: 18 ("wool throw", "merino throw", "wool blanket throw", ...)
│   └── RSA: 15 headlines + 4 descriptions, pinned brand + USP + CTA
├── Ad group: Throws - Linen
│   ├── Keywords: 14
│   └── RSA: 15 / 4
├── Ad group: Cushions - Linen
│   ├── Keywords: 22
│   └── RSA: 15 / 4
├── Ad group: Rugs - Wool
│   ├── Keywords: 19
│   └── RSA: 15 / 4
└── Ad group: Home fragrance
    ├── Keywords: 16
    └── RSA: 15 / 4

Campaign: Koala - Search - Branded
└── Ad group: Koala Brand
    ├── Keywords: 8 (exact match on brand variants)
    └── RSA: 15 / 4 (defends brand queries)
```

## 8. Sitelink ideas by vertical

| Vertical | Sitelinks |
|---|---|
| E-commerce | Shop, New arrivals, Sale, Gift cards |
| Lead-gen services | Services, Pricing, About, Contact |
| SaaS | Features, Pricing, Customer stories, Free trial |
| Local services | Book now, Service areas, Reviews, Emergency call-out |
