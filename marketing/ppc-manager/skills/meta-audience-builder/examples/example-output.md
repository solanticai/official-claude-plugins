# Meta Audiences — Koala & Co. AU

**Ad account:** act_1234567890
**Pixel:** 123456789012345
**Date:** 11/04/2026

---

## Retargeting audiences

| Name | Source event | Retention | Approx size | Status |
|---|---|---|---|---|
| Retarget - Page Viewers - 180d | PageView | 180 days | ~14,000 | created |
| Retarget - Product Viewers - 60d | ViewContent | 60 days | ~4,200 | created |
| Retarget - Cart Abandoners - 14d | AddToCart (exclude Purchase 14d) | 14 days | ~180 | created, populating |
| Retarget - Checkout Abandoners - 7d | InitiateCheckout (exclude Purchase 7d) | 7 days | ~60 | created, populating |

---

## Lookalike audiences

| Name | Source audience | Country | Ratio | Approx size | Status |
|---|---|---|---|---|---|
| Lookalike - AU Purchasers 1% | Custom - AU Purchasers 180d | AU | 1% | ~200,000 | created |
| Lookalike - AU Purchasers 3% | Custom - AU Purchasers 180d | AU | 3% | ~600,000 | created |
| Lookalike - AU Subscribers 1% | Custom - Newsletter Subscribers | AU | 1% | ~200,000 | created |

---

## Exclusion audiences

| Name | Source | Retention | Status |
|---|---|---|---|
| Exclusion - Recent Purchasers 30d | Purchase event | 30 days | created |
| Exclusion - Existing Customers | Customer list (8,300 users uploaded, hashed) | — | created |

---

## Campaign use matrix

| Campaign type | Include | Exclude |
|---|---|---|
| Retargeting (conversion) | `Retarget - Cart Abandoners - 14d`, `Retarget - Checkout Abandoners - 7d` | `Exclusion - Recent Purchasers 30d` |
| Retargeting (re-engagement) | `Retarget - Page Viewers - 180d`, `Retarget - Product Viewers - 60d` | `Exclusion - Recent Purchasers 30d`, `Retarget - Cart Abandoners - 14d` |
| Prospecting (1% LAL) | `Lookalike - AU Purchasers 1%`, `Lookalike - AU Subscribers 1%` | `Exclusion - Recent Purchasers 30d`, `Exclusion - Existing Customers`, `Retarget - Page Viewers - 180d` |
| Prospecting (broader) | `Lookalike - AU Purchasers 3%` | Same as above |
| Brand awareness | Broad interest + Lookalike 3% | `Exclusion - Recent Purchasers 30d` |

---

## Next steps

1. Wait 24 hours for Cart Abandoners / Checkout Abandoners audiences to populate (currently 180 and 60 — they'll grow over time).
2. Run `/ppc-manager:meta-creative-brief` to design creative for the Lookalike 1% prospecting campaign.
3. Launch a Retargeting conversion campaign using Cart Abandoners 14d + Purchase exclusion next week.
4. Launch a Prospecting campaign using Lookalike 1% + all exclusions after creative is ready.
