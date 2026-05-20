# Campaign Audit — Reference

## 1. Finding categories

| Category | Definition | Action |
|---|---|---|
| Blocker | Actively broken, silently burning budget | Fix immediately |
| Tuning | Works but could be significantly better | Fix in next optimisation cycle |
| Experiment | Works fine; could unlock upside with a test | Plan and run as an A/B test |

## 2. Typical blocker checklist (Google Ads)

- [ ] Conversion tracking firing (≥30 conversions / 30 days at account level)
- [ ] Conversion values present (not zero)
- [ ] Primary conversions set (not "all conversions" optimisation)
- [ ] Auto-tagging ON
- [ ] GA4 linked
- [ ] Merchant Center linked (if retail)
- [ ] Billing active
- [ ] No Universal Analytics conversion imports (legacy)
- [ ] Search Terms report not 80%+ `(not set)` / `(other)`
- [ ] Shared negative keyword list applied to every Search campaign

## 3. Typical blocker checklist (Meta)

- [ ] Pixel fires on every page load (PageView)
- [ ] Purchase event fires with `eventID` for CAPI dedup
- [ ] CAPI events arrive (check Events Manager Overview "server" tab)
- [ ] Event Match Quality ≥ 7.0 for Purchase
- [ ] Aggregated Event Measurement priority ranked
- [ ] Custom audience for "Purchase 30d" exists for exclusion
- [ ] No stuck ad sets (delivery = "No Delivery" but status = Active)
- [ ] No creative with frequency > 5 (fatigue threshold)

## 4. Typical tuning findings

- **High CPC on non-converting keywords.** Pause or negative.
- **Ad group with 100+ keywords.** Split by theme.
- **Responsive Search Ad with only 3 headlines.** Add 12 more to max out.
- **Bidding strategy is Maximise Clicks.** Switch to Max Conversions once ≥30 conv/month.
- **Campaign daily budget caps spend at 50% of available impressions.** Increase budget or lower bids.
- **Meta ad set with overlap > 30% with another ad set.** Merge or exclude.

## 5. Creative fatigue indicators (Meta)

| Metric | Healthy | Fatigued |
|---|---|---|
| Frequency | < 3.0 | ≥ 5.0 |
| CTR trend | flat or rising | steady decline over 7 days |
| CPM trend | flat | rising despite stable audience |
| Delivery | Active | Limited |

If fatigued: rotate to new creative (from `meta-creative-brief`).

## 6. Wasted spend calculation

```
wasted_spend = sum(cost of keywords with 0 conversions AND >200 clicks)
```

In GAQL:

```sql
SELECT
  ad_group_criterion.keyword.text,
  metrics.cost_micros,
  metrics.clicks,
  metrics.conversions
FROM ad_group_criterion
WHERE segments.date DURING LAST_30_DAYS
  AND metrics.clicks > 200
  AND metrics.conversions = 0
ORDER BY metrics.cost_micros DESC
```

Any row that appears is a candidate for negative keyword or pause.

## 7. GA4 vs platform reconciliation

Expected difference:

- **Google Ads ↔ GA4:** within 5% for Purchase (they're tightly integrated via the import).
- **Meta ↔ GA4:** Meta typically 10–20% higher for Purchase (view-through attribution). If Meta > GA4 by >40%, overcounting. If Meta < GA4 by >20%, undercounting (pixel broken or ad blocker impact).

## 8. Remediation skill chain

| Finding | Remediation skill |
|---|---|
| Pixel not firing | `/ppc-manager:meta-pixel-setup` |
| CAPI missing | `/ppc-manager:meta-capi-setup` |
| Event mismatch GA4/Meta | `/ppc-manager:meta-events-mapping` |
| GTM tags broken | `/ppc-manager:gtm-tags` |
| Conversion tracking broken | `/ppc-manager:ga4-events` |
| No negatives | `/ppc-manager:keyword-research` (negative candidates section) |
| Creative fatigue | `/ppc-manager:meta-creative-brief` + `/ppc-manager:meta-ads-copy` |
| Audience overlap | `/ppc-manager:meta-audience-builder` |
| Missing GA4 link | `/ppc-manager:google-ads-account-setup` |
| Landing page misaligned | `/ppc-manager:landing-page-copy` |
