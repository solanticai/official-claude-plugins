# GA4 Events — Koala & Co. Online

**Property:** properties/789012345
**Date:** 11/04/2026

---

## Event inventory (last 30 days)

| Event name | Event count | Source | Conversion? |
|---|---|---|---|
| `page_view` | 142,311 | Enhanced Measurement | no |
| `session_start` | 38,904 | GA4 auto | no |
| `first_visit` | 22,711 | GA4 auto | no |
| `scroll` | 31,552 | Enhanced Measurement | no |
| `click` | 8,433 | Enhanced Measurement | no |
| `view_item` | 6,120 | dataLayer | no |
| `add_to_cart` | 1,089 | dataLayer | no |
| `begin_checkout` | 487 | dataLayer | no |
| `purchase` | 203 | dataLayer | **new** |
| `newsletter_signup` | 188 | dataLayer | **new** |
| `form_submit` | 128 | Enhanced Measurement | no |
| `user_engagement` | 41,220 | GA4 auto | no |

---

## Conversions

### Already marked

(none — this is the first time `ga4-events` has been run on this property)

### Newly marked

| Event name | Rationale | Google Ads import? |
|---|---|---|
| `purchase` | Primary revenue event; imports cleanly into Google Ads as `Purchase` | yes |
| `newsletter_signup` | Secondary owned-audience event; useful for retargeting audiences | no (use as Meta custom audience source instead) |

Skipped (user wanted but we pushed back):
- `add_to_cart` — too top-of-funnel, would pollute Google Ads Smart Bidding data.
- `begin_checkout` — same reason; already available as a Funnel Exploration step.

---

## Custom dimensions

### Already exist

(none)

### Newly created

| Parameter name | Display name | Scope | Rationale |
|---|---|---|---|
| `item_brand` | Item brand | EVENT | Split performance by Koala & Co.-owned brands vs stocked brands |
| `item_category` | Item category | EVENT | Slice by Throws / Cushions / Rugs / Lighting |
| `coupon` | Coupon code | EVENT | Measure promo redemption rates |
| `payment_type` | Payment type | EVENT | Afterpay vs Stripe vs PayPal — important for cohort analysis |
| `shipping_tier` | Shipping tier | EVENT | Standard vs Express — affects margin |

---

## Custom metrics

(none this run — recommended for Phase 2 after 30 days of accumulated `estimated_margin` data)

---

## DebugView verification

For each newly-marked conversion:

### `purchase`

1. Open `https://koalahomewares.com.au/?debug_mode=true`.
2. Add a throwaway item to cart, proceed through checkout with the test Stripe card `4242 4242 4242 4242`.
3. Land on the thank-you page.
4. GA4 → Admin → DebugView — within 10 seconds, `purchase` appears.
5. Click it — confirm `transaction_id`, `currency=AUD`, `value=129.00`, `items[]` with `item_brand`, `item_category`, `coupon`, `payment_type=credit_card`, `shipping_tier=standard` all present.
6. Verified: 11/04/2026 14:48 AEST.

### `newsletter_signup`

1. Open `https://koalahomewares.com.au/?debug_mode=true`.
2. Scroll to the footer newsletter form, enter a test email, submit.
3. GA4 → Admin → DebugView — within 10 seconds, `newsletter_signup` appears.
4. Click it — confirm `list_name=main_footer` is present.
5. Verified: 11/04/2026 14:52 AEST.

---

## Open issues to revisit later

1. `estimated_margin` custom metric — requires the Shopify checkout to push margin data, which is not in the current dataLayer schema. Add to the next `gtm-datalayer` iteration.
2. `user_type` USER-scope dimension — requires a logged-in state push on account creation. Not a priority until account-based campaigns launch.
3. `item_category2` through `item_category5` — Koala & Co. doesn't use taxonomy below category-level today. Skip until they do.

---

## Next steps

1. Wait 24 hours. Then re-run `/ppc-manager:ga4-events` in audit mode to confirm the new conversions are accumulating. Expect 6–8 new `purchase` conversions based on the 30-day baseline rate.
2. Run `/ppc-manager:google-ads-account-setup` — import `purchase` as a Google Ads conversion action under `Category: Purchase`, `Attribution: Data-driven`.
3. Run `/ppc-manager:meta-events-mapping` to reconcile with Meta Pixel (which is already firing `Purchase` but without the custom dimensions).
