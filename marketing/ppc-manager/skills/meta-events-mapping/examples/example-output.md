# Event Dictionary — Koala & Co. Online

**Date:** 11/04/2026
**Owner:** Data & Analytics team (Koala & Co.)

---

## Canonical events

| Business event | GA4 | Meta Pixel | Meta CAPI | GTM DL | Notes |
|---|---|---|---|---|---|
| Page load | `page_view` | `PageView` | `PageView` | `page_view` | Enhanced Measurement on GA4 |
| Product view | `view_item` | `ViewContent` | `ViewContent` | `view_item` | Requires currency/value |
| Add to cart | `add_to_cart` | `AddToCart` | (not forwarded) | `add_to_cart` | Browser-only to reduce noise |
| Begin checkout | `begin_checkout` | `InitiateCheckout` | `InitiateCheckout` | `begin_checkout` | |
| Add payment | `add_payment_info` | `AddPaymentInfo` | `AddPaymentInfo` | `add_payment_info` | |
| Purchase | `purchase` | `Purchase` | `Purchase` | `purchase` | Revenue event, CAPI dedup via `event_id` |
| Newsletter | `newsletter_signup` | `Subscribe` | `Subscribe` | `newsletter_signup` | Custom Meta event |

---

## Param schemas per event

### Purchase (`purchase`)

**GA4 params:**
- `transaction_id` (string): Shopify order number, also used as GA4 dedup key
- `currency` (string): `AUD`
- `value` (number): Total order value inc. tax and shipping
- `tax` (number): GST
- `shipping` (number): Shipping cost
- `coupon` (string): Discount code if applied
- `items[]` (array): Enhanced Ecommerce items shape — `item_id`, `item_name`, `item_brand`, `item_category`, `item_variant`, `price`, `quantity`

**Meta Pixel params:**
- `currency`: Same as GA4
- `value`: Same as GA4
- `content_ids`: Array of SKUs (derived from `items[].item_id` via JS helper)
- `content_type`: Literal `'product'`
- `num_items`: Derived from `items.length`
- `eventID` (top-level, for dedup): `{{DL - event_id}}`

**Meta CAPI `custom_data`:**
- `currency`: Same
- `value`: Same
- `content_ids`: Same
- `content_type`: `'product'`
- `num_items`: Same
- `event_id` (top-level): Same as browser pixel's `eventID`

### Newsletter (`newsletter_signup`)

**GA4 params:**
- `list_name` (string): Which list (`main_footer`, `popup`, `checkout`)

**Meta Pixel params:**
- Using `Subscribe` as the custom event (closest standard is `CompleteRegistration` but `Subscribe` matches the subscription semantic better)
- No params beyond `eventID`

**Meta CAPI `custom_data`:**
- `status`: `'subscribed'`

---

## Inconsistencies found

| Finding | Severity | Fix |
|---|---|---|
| `add_to_cart` fires in GA4 and Meta browser but not CAPI | medium | Intentional — noisy event, not worth server-side cost |
| `view_item` fires ~3x per page load on Shopify for variant changes | medium | Deduplicate by `event_id` on the client — one push per `item_id`/minute |
| Meta Pixel `Purchase` has `eventID`, Meta CAPI doesn't always receive it | **high** | Verify Cloudflare Worker includes `event_id` from POST body in every CAPI event |
| GA4 shows AUD 25,340 last 30 days, Meta shows USD 16,200 | low | Currency conversion expected — not a bug |
| GA4 `transaction_id` is the Shopify order number, CAPI `event_id` appends checkout token | low | Functional but different shapes. Document that `transaction_id` ≠ `event_id` but both are unique |

---

## Next steps

1. Circulate this doc to dev + marketing as canonical reference (store in Notion + this repo).
2. Fix the `high` severity CAPI `event_id` issue — update the Cloudflare Worker to always forward the browser's `event_id`.
3. Run `/ppc-manager:campaign-audit --scope meta` to verify Meta attribution is clean after the fix.
4. Re-run this skill in 30 days to check for drift.
