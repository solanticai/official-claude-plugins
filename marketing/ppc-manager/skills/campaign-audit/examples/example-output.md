# Campaign Audit — Koala & Co. AU

**Account:** 1234567890 (Google Ads) + act_1234567890 (Meta)
**Period:** 12/03/2026 to 11/04/2026 (30 days)
**Total spend:** $11,280 AUD ($6,820 Google Ads + $4,460 Meta)
**Conversions:** 224 purchases (Google Ads 132, Meta 92)
**Overall health score:** 68/100
**Date:** 11/04/2026

---

## Executive summary

Koala & Co. is running a healthy Google Ads account with strong branded search performance but has three significant tuning opportunities: $1,240/month in wasted spend on non-converting generic queries, under-utilised Responsive Search Ad headline slots, and a missing negative keyword list. Meta Ads is tracking-constrained — the pixel fires cleanly but CAPI is not yet installed, causing conversion undercount of ~35% based on GA4 reconciliation. Fixing these three blockers would unlock an estimated $2,800/month of efficiency.

---

## Blockers (fix immediately)

| # | Finding | Data point | $ impact / month | Effort | Remediation |
|---|---|---|---|---|---|
| 1 | Meta CAPI not installed; pixel only | GA4 Meta Purchase = 141, Meta Ads Purchase = 92, 35% undercount | $1,100 | medium | Run `/ppc-manager:meta-capi-setup` with Cloudflare Worker backend |
| 2 | Google Ads wasting spend on 12 non-converting keywords | 12 kw with >200 clicks each, $0 conversions, $1,240 total spend | $1,240 | low | Add to negatives via shared list |
| 3 | Google Ads Search campaign missing sitelink/callout extensions | Campaign `Koala - Search - Homewares` has 0 sitelinks | $420 | low | Install 4 sitelinks + 4 callouts via Google Ads UI |

---

## Tuning (next optimisation cycle)

| # | Finding | Data point | $ impact / month | Effort | Remediation |
|---|---|---|---|---|---|
| 4 | RSA `Throws - Wool` only uses 3 headlines of 15 | 3/15 headlines, CTR 2.1% | $280 | low | Run `/ppc-manager:google-ads-copy` to get 12 more headlines |
| 5 | No Meta retargeting exclusion for recent buyers | Cart Abandoners 14d audience includes users who purchased | $140 | low | Run `/ppc-manager:meta-audience-builder` to rebuild with Exclusion - Recent Purchasers 30d |
| 6 | Meta creative frequency = 4.8 on the main prospecting ad set | Frequency trending up from 3.2 to 4.8 over 7 days | $320 | medium | Run `/ppc-manager:meta-creative-brief` for 2 new variants |
| 7 | Google Ads Ad group `Rugs - Wool` bids set to manual $0.80 in a market with $1.50 avg | Lost impression share (budget) = 42% | $180 | low | Raise bids to $1.40-$1.50 manually |

---

## Experiments (to test next)

| # | Hypothesis | Rationale | Test design |
|---|---|---|---|
| 1 | Performance Max campaign will outperform Search for prospecting | PMax typically 15–25% cheaper CPA than Search for retail with strong feed | Run `/ppc-manager:google-pmax-campaign` with $100/day budget alongside existing Search for 30 days, compare CPA |
| 2 | Lookalike 1% LAL for Meta will outperform broad interest targeting | Current broad targeting CPA = $48, Lookalike should be ~$35 based on benchmark | Pause one broad ad set, launch lookalike ad set with same budget for 14 days |

---

## Cross-platform reconciliation

| Source | Purchases | Value (AUD) | Variance |
|---|---|---|---|
| GA4 | 273 | $34,820 | baseline |
| Google Ads | 132 | $18,600 | -5% (expected) |
| Meta | 92 | $12,450 | -35% (**BLOCKER** — install CAPI) |

---

## Health scores by area

| Area | Score | Severity |
|---|---|---|
| Account setup (billing, linking, conversion actions) | 88/100 | ok |
| Structure (naming, grouping, match types) | 72/100 | ok |
| Tracking (pixel, CAPI, dedup) | 54/100 | warning |
| Creative (CTR, frequency, age) | 68/100 | warning |
| Audience (retargeting, lookalikes, exclusions) | 60/100 | warning |
| Landing page (alignment, speed) | 78/100 | ok |
| **Overall** | **68/100** | warning |

---

## Remediation playbook

### Immediate (this week)

1. Install Meta CAPI via Cloudflare Worker — `/ppc-manager:meta-capi-setup`. Target: EMQ ≥7.0 on Purchase. ETA: 2 days including deployment.
2. Add the 12 wasted-spend keywords to the shared negative list. Also add 6 new negatives from the search-terms report.
3. Install sitelinks + callouts on `Koala - Search - Homewares` manually in Google Ads UI. ETA: 20 minutes.

### Next (next 2 weeks)

1. Run `/ppc-manager:google-ads-copy` to generate 12 new RSA headlines for `Throws - Wool` ad group.
2. Run `/ppc-manager:meta-audience-builder` to rebuild retargeting audiences with proper purchaser exclusion.
3. Run `/ppc-manager:meta-creative-brief` for 2 new ad variants to rotate into the main prospecting ad set.

### Backlog

1. Test Performance Max campaign (see Experiment 1).
2. Test Meta Lookalike 1% ad set (see Experiment 2).
3. Re-audit in 14 days to verify fixes landed.

---

## Next steps

1. Start with blocker #1 (Meta CAPI) — highest dollar impact with medium effort.
2. Re-run `/ppc-manager:campaign-audit` on 25/04/2026 to measure progress.
3. If health score rises to ≥80, move to monthly audit cadence.
