# Google Search Campaign — Koala - Search - Homewares

**Customer:** 1234567890 (Koala & Co. AU)
**Campaign:** Koala - Search - Homewares
**Budget:** AUD 75.00 / day
**Status:** PAUSED (awaiting user enable)
**Date:** 11/04/2026

---

## Structure

| Ad group | Keywords | Match mix | RSA |
|---|---|---|---|
| Throws - Wool | 18 | 12 Phrase / 4 Exact / 2 Broad | 15 h / 4 d |
| Throws - Linen | 14 | 10 Phrase / 4 Exact / 0 Broad | 15 h / 4 d |
| Cushions - Linen | 22 | 16 Phrase / 5 Exact / 1 Broad | 15 h / 4 d |
| Rugs - Wool | 19 | 13 Phrase / 5 Exact / 1 Broad | 15 h / 4 d |
| Home fragrance | 16 | 11 Phrase / 4 Exact / 1 Broad | 15 h / 4 d |

Totals: 5 ad groups, 89 keywords, 5 RSAs.

---

## Ad group detail

### Throws - Wool

**Landing page:** `https://koalahomewares.com.au/collections/throws/wool`
**Default CPC bid:** AUD 1.50

**Keywords:**

| Keyword | Match type |
|---|---|
| wool throw blanket | Phrase |
| merino wool throw | Phrase |
| "wool throw" | Phrase |
| [wool throw australia] | Exact |
| [merino throw blanket] | Exact |
| wool throw for couch | Phrase |
| … 12 more | |

**RSA:**

- Headlines: 15 (pinned: 3 — "Koala & Co." @ H1, "Handmade Australian Wool" @ H2, "Shop Wool Throws" @ H3)
- Descriptions: 4
- Path: /throws/wool

### Rugs - Wool

**Landing page:** `https://koalahomewares.com.au/collections/rugs/wool`
**Default CPC bid:** AUD 1.80

... (4 more ad groups with the same structure)

---

## Negative keywords

| Keyword | Match type | Source |
|---|---|---|
| free | Broad | Canonical negatives |
| cheap | Broad | Canonical negatives |
| wholesale | Broad | Canonical negatives |
| diy | Broad | Canonical negatives |
| tutorial | Broad | Canonical negatives |
| adairs | Phrase | Competitor excludes |
| pillow talk | Phrase | Competitor excludes |
| bed bath n table | Phrase | Competitor excludes |
| craigslist | Broad | Canonical negatives |
| gumtree | Broad | Canonical negatives |
| facebook marketplace | Broad | Canonical negatives |
| pet bed | Phrase | Koala does not sell pet beds |
| … 15 more | | |

Installed as **Shared Negative Keyword List: Koala - Core Negatives** so it can be reused on future campaigns.

---

## Readiness checklist

- [x] Conversion tracking imported from GA4 (`GA4 - purchase` is Primary conversion)
- [x] Billing active
- [x] Merchant Center linked (Shopify feed, ID 789012345)
- [ ] Ad extensions installed (**manual**: 4 sitelinks, 4 callouts, 1 structured snippet — see reference.md)
- [x] Landing page live (HTTP 200 for all 5 URLs)
- [x] Daily budget approved ($75 AUD)
- [ ] User confirmed ENABLE (waiting)

---

## Next steps

1. Install ad extensions via UI (Assets → Add → Sitelinks / Callouts / Structured snippets).
2. Tick the remaining two checkboxes.
3. Enable the campaign: `ppc-google-ads:enable_campaign(customer_id=1234567890, campaign_id=987654321)`.
4. Monitor daily for the first week. Expect ~2–3 days before Google settles on a baseline.
5. In 7 days, run `/ppc-manager:campaign-audit --scope google-ads` to review initial performance and apply fixes.
