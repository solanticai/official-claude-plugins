# SEO Toolkit — Data Sources Guide

When to use each data provider, what each is best for, and their cost and rate-limit characteristics.

---

## Provider comparison

| Provider | Best for | Cost band | Data freshness | Rate limits | Free tier? |
|---|---|---|---|---|---|
| **SerpAPI** | SERP scraping, SERP features, PAA questions | ~USD 50/mo (100 searches) | Real-time | 100 searches/mo free; paid plans from $50/mo | Yes — 100 searches |
| **DataForSEO** | Keyword volume, keyword suggestions, bulk processing | Pay-per-use (low) | 24–48h | Very generous; bulk API designed for scale | Pay-per-use from USD $0.0006/keyword |
| **Ahrefs** | Backlink data, referring domains, domain rating | USD 99–999/mo | Near real-time (updated daily) | API plan required (USD 999+/mo); expensive | No |
| **Moz** | Domain Authority, link metrics, spam score | USD 99–599/mo | Updated weekly | 25 000 rows/mo on standard; 10 req/s | No (limited free API) |
| **PSI (Google)** | Core Web Vitals, Lighthouse scores, field data | Free | Real-time (lab) + 28d rolling (field) | 400 requests/day per key; no charge | Yes — free API |
| **GSC (Google)** | Organic impressions, clicks, average position, query data | Free | ~3 day lag | 200 req/100s per property; no charge | Yes — free OAuth |
| **GA4 (Google)** | Organic traffic, conversion data, user behaviour | Free | ~24h lag (standard) | 10 concurrent requests; no charge | Yes — free OAuth |

---

## When to use each provider

### SerpAPI

Use SerpAPI when you need to know **what Google is currently showing** for a query. It scrapes live SERPs and returns structured data including organic results, Featured Snippets, People Also Ask, Local Pack, Shopping results, and more.

Best skills: `keyword-research`, `serp-analysis`, `competitor-seo-audit`

Avoid for: keyword volume at scale (expensive per query), historical data.

### DataForSEO

Use DataForSEO when you need **keyword volume and suggestions in bulk**. Its Keyword Data API covers search volume, CPC, competition, and trends. The keyword suggestion API returns semantically related terms and long-tail variants.

Best skills: `keyword-list-developer`, `keyword-clustering-and-mapping`, `keyword-research`

Avoid for: real-time SERP snapshots (use SerpAPI instead).

### Ahrefs

Use Ahrefs for **backlink intelligence** — referring domains, anchor text distribution, new/lost links, and competitor link profiles. Its link index is large and updated frequently.

Best skills: `backlink-audit`, `competitor-seo-audit`

Avoid for: keyword volume (DataForSEO is cheaper); Core Web Vitals (use PSI).

Note: Ahrefs API access requires their highest-tier plan. Many teams use the Ahrefs UI and export CSVs manually for infrequent backlink audits.

### Moz

Use Moz for **domain authority benchmarking** and comparing the relative strength of domains. Domain Authority (DA) is widely understood by clients and useful for quick competitive comparisons.

Best skills: `competitor-seo-audit`, `backlink-audit`

Avoid for: real-time data (Moz index updates weekly). Do not treat DA as a ranking factor — it is a proxy metric.

### PageSpeed Insights (PSI)

Use PSI for **Core Web Vitals** measurement. It provides both Lighthouse lab data (synthetic, reproducible) and Chrome User Experience Report (CrUX) field data (real user measurements).

Best skills: `core-web-vitals-report`, `technical-seo-audit`

The API is free with a Google API key. Rate limit is 400 requests/day per key — sufficient for most audits.

### Google Search Console (GSC)

Use GSC for **owned-site organic performance data** — what queries are driving impressions and clicks, which pages rank, average position, and click-through rate. This is first-party data from Google.

Best skills: `gsc-performance-report`, `content-gap-analysis`, `keyword-research`

Limitations: data is only available for properties the user has verified in GSC. Queries with very low impressions are anonymised.

### Google Analytics 4 (GA4)

Use GA4 for **post-click behaviour** — sessions, bounce rate, goal completions, and conversion attribution for organic traffic. Combine with GSC data for a full funnel view (impressions → clicks → conversions).

Best skills: `content-gap-analysis`, `gsc-performance-report`

---

## Recommended provider combinations by use case

| Use case | Primary | Secondary |
|---|---|---|
| Keyword research | DataForSEO (volume) | SerpAPI (SERP snapshot) |
| Competitor analysis | SerpAPI (SERP) | Ahrefs (backlinks) |
| Content gap analysis | GSC (owned performance) | DataForSEO (opportunity volume) |
| Technical audit | PSI (CWV) | GSC (indexation signals) |
| Backlink audit | Ahrefs | Moz (DA benchmarking) |
| Local SEO | SerpAPI (Local Pack) | GSC (local query data) |

---

## Cost-conscious setup

If you want maximum coverage with minimal cost:

1. **Free tier only**: PSI + GSC + GA4 — covers Core Web Vitals, owned query data, and traffic analysis at no cost.
2. **Add keyword data**: DataForSEO pay-per-use — extremely low cost for volume lookups.
3. **Add SERP snapshots**: SerpAPI free tier (100 searches/mo) — enough for targeted competitive analysis.
4. **Skip Ahrefs/Moz** unless backlink analysis is a core requirement — both require paid plans.
