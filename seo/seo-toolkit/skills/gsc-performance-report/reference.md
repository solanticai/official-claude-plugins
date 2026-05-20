# GSC Performance Report — Reference Framework

## GSC API Query Patterns

### Dimensions

| Dimension | Use Case |
|---|---|
| `query` | Which search terms are driving traffic |
| `page` | Which pages are ranking and earning clicks |
| `country` | Geographic performance distribution |
| `device` | Mobile vs desktop vs tablet split |
| `searchAppearance` | Rich results, AMP, featured snippets |

Dimensions can be combined (e.g. `query + page` to see which query drives traffic to which page).

### Date Comparison Patterns

| Pattern | Best For |
|---|---|
| 28d vs prior 28d | General performance monitoring; trending |
| 28d vs same 28d last year (YoY) | Seasonal businesses; longer-term view |
| Post-change vs pre-change | Measuring impact of a specific SEO action |
| Post-algorithm vs pre-algorithm | Understanding algorithm update impact |

**GSC data lag:** GSC data is typically complete after 2–4 days. Always exclude the 3 most recent days from analysis to avoid incomplete day data.

---

## Z-Test for Delta Significance

### Why Use Statistical Significance

GSC metrics (especially clicks) have high variance for low-volume queries. A query going from 3 to 6 clicks is not necessarily a meaningful change — it could be normal variance. Applying a significance test separates true signals from noise.

### Simplified Proportions Z-Test

For clicks delta between two periods:

```
z = (p1 - p2) / sqrt(p_pool * (1 - p_pool) * (1/n1 + 1/n2))

where:
  p1 = clicks_current / impressions_current
  p2 = clicks_comparison / impressions_comparison
  p_pool = (clicks_current + clicks_comparison) / (impressions_current + impressions_comparison)
  n1 = impressions_current
  n2 = impressions_comparison
```

**Significance thresholds (two-tailed):**
- |z| < 1.65 → not significant (noise)
- 1.65 ≤ |z| < 1.96 → moderate significance (watch)
- |z| ≥ 1.96 → statistically significant (95% confidence)

**Practical rule for low-volume rows:** If total impressions in both periods combined < minimum threshold (default 100), label `[low-data]` regardless of delta size.

---

## CTR-by-Position Benchmark Curve

These are approximate industry averages for organic CTR by position. Actual values vary significantly by query type (branded vs non-branded, featured snippets, local pack, etc.).

| Position | Avg CTR (informational) | Avg CTR (commercial) |
|---|---|---|
| 1 | 28–35% | 18–25% |
| 2 | 15–20% | 10–14% |
| 3 | 10–13% | 7–10% |
| 4 | 7–9% | 5–7% |
| 5 | 5–7% | 3–5% |
| 6–10 | 2–5% | 1–3% |
| 11–20 | 0.5–1.5% | 0.3–1% |
| > 20 | < 0.5% | < 0.3% |

**CTR below benchmark for position:** Likely cause — title/meta description doesn't match search intent, a SERP feature (featured snippet, local pack) is capturing clicks above organic results, or brand is not well-known.

**CTR above benchmark for position:** Rich result (FAQ, review stars, sitelinks) is enhancing the organic listing; strong brand recognition.

---

## Query Class Taxonomy

| Class | Signals | Typical CTR | SEO Implication |
|---|---|---|---|
| Branded | Contains brand name or product name | Very high | Reflects brand strength; not raw SEO performance |
| Informational | "how", "what", "why", "guide", "tips" | Medium | Top of funnel; content investment |
| Commercial Investigation | "best", "vs", "review", "top 10" | Medium-high | Middle of funnel; high buyer intent |
| Transactional | "buy", "price", "cheap", "near me" | High (but lower volume) | Bottom of funnel; conversion-critical |
| Navigational | Domain name, "login", "contact" | Very high | Not targetable via SEO strategy |

### Query Class Shifts to Flag

- **Branded share increasing** → Site authority is growing OR non-branded visibility is declining
- **Informational share increasing, transactional declining** → Content over-index on top-of-funnel; may need more commercial content
- **Sudden loss of a specific query class** → Algorithm update may have targeted a content type

---

## Common GSC Anomaly Patterns and Hypotheses

| Anomaly Pattern | Likely Cause | Recommended Action |
|---|---|---|
| Impressions ↑, CTR ↓ | Ranking for broader/irrelevant queries | Audit title/meta; ensure content matches new query intent |
| Position ↑ (improved), Clicks ↓ | SERP feature (featured snippet, image pack, news) capturing clicks above your result | Check if a featured snippet exists; optimise for it or accept the trade-off |
| Sudden 100% impression loss | Page de-indexed, manual action, or URL moved | Check GSC Coverage report for index errors; check for manual actions |
| Impressions stable, Clicks ↓ | CTR drop — title/meta no longer competitive | A/B test new title; check if SERP layout changed |
| All metrics ↓ across the board | Broad algorithm update or crawl issue | Cross-reference with Google update history; run technical audit |
| New queries appearing in bulk | Successful new content published, or featured on a high-authority site | Track and double down on winning query clusters |

---

## GSC Data Limitations

1. **Query data is sampled** — GSC shows the top 1,000 rows by default (API max: 25,000 rows per request with pagination)
2. **Branded vs non-branded not labelled** — requires manual classification in post-processing
3. **Position is a weighted average** — "average position 4" could mean some users see you at 1, others at 8
4. **CTR is aggregate across all user contexts** — mobile vs desktop, signed-in vs signed-out, location all affect CTR
5. **Not provided queries** — some branded queries may be hidden in `(not provided)` aggregation
6. **Data freshness** — typically 2–4 day lag; exclude last 3 days

---

## Key References

- Google Search Console API documentation
- Google Search Central: Understand how GSC reports queries
- Sistrix CTR study (European organic CTR benchmarks)
- Advanced Web Ranking: CTR research (ongoing study)
