# Meta Audience Builder — Reference

## 1. Custom audience source types

| Source | Use for | Min source size |
|---|---|---|
| Website (pixel event) | Auto-updating site behaviour | any |
| Customer list (upload) | First-party email/phone data | 100 |
| Engagement — Page | Users who interacted with a Page | 100 |
| Engagement — Video | Users who watched video | 100 |
| Engagement — Lead form | Users who opened/submitted a lead form | 100 |
| App activity | Mobile app events | 100 |
| Offline events | CRM purchase events uploaded to Meta | 100 |

## 2. Retention recommendations

| Event | Retention | Rationale |
|---|---|---|
| PageView | 180 days | Very broad — maximum window is useful for brand remarketing |
| ViewContent | 60 days | Product-level interest cools fast |
| AddToCart | 14 days | Intent cools very fast for cart abandoners |
| InitiateCheckout | 7 days | Checkout intent is even more time-sensitive |
| Purchase | 30 days (exclusion) / 180 (repeat) | 30d for exclusion from prospecting; 180d for repeat purchase campaigns |
| AddToWishlist | 30 days | Moderate intent |
| Lead | 30 days | For follow-up campaigns |

## 3. Lookalike ratio guide

| Ratio | Size (AU) | When to use |
|---|---|---|
| 1% | ~200,000 | Tightest match, closest to source audience. Best for conversion campaigns. |
| 2–3% | ~400-600k | Slightly broader, more reach. For mid-funnel. |
| 4–5% | ~800k-1M | Broader. Good for awareness / top-of-funnel prospecting. |
| 6-10% | >1M | Very broad. Almost always too broad — only for reach campaigns at scale. |

## 4. Audience name conventions

`{Type} - {Source} - {Window}`

Types:
- `Retarget` — retargeting audiences (warm traffic).
- `Lookalike` — lookalike audiences.
- `Exclusion` — exclusion audiences.
- `Custom` — customer list uploads.
- `Engagement` — page/video/lead engagement.

Examples:
- `Retarget - Page Viewers - 180d`
- `Retarget - Cart Abandoners - 14d`
- `Lookalike - AU Purchasers 1%`
- `Exclusion - Recent Purchasers 30d`
- `Custom - Newsletter Subscribers`
- `Engagement - FB Page - 90d`

## 5. Campaign matrix

| Campaign type | Included | Excluded |
|---|---|---|
| Retargeting - Conversion | `Retarget - Cart Abandoners - 14d`, `Retarget - Checkout Abandoners - 7d` | `Exclusion - Recent Purchasers 30d` |
| Retargeting - Engagement | `Retarget - Page Viewers - 180d` | `Exclusion - Recent Purchasers 30d`, `Retarget - Cart Abandoners - 14d` (to avoid overlap) |
| Prospecting | `Lookalike - AU Purchasers 1%`, `Lookalike - AU Subscribers 1%` | `Retarget - Page Viewers - 180d`, `Exclusion - Recent Purchasers 30d`, `Custom - Existing Customers` |
| Brand awareness | Broad / Interest targeting / Lookalike 5% | `Exclusion - Recent Purchasers 30d` |

## 6. Common mistakes

- Building lookalikes from too small a source (<100 users) — they'll be rubbish.
- Not excluding existing customers from prospecting — expensive.
- Using 180-day retention on cart abandoners — intent is cold at that point.
- Overlapping retargeting and prospecting audiences — wastes budget on overlap.
- Uploading a customer list without hashing — Meta hashes it for you but best practice is to hash first.
