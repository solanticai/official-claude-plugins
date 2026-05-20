# GA4 Setup — Koala & Co. Online

**Property:** properties/789012345
**Account:** Koala & Co. (accounts/987654321)
**Date:** 11/04/2026

---

## Snapshot

- **Currency:** AUD
- **Time zone:** Australia/Sydney
- **Industry:** SHOPPING
- **Created:** 2024-06-15T03:12:45+00:00
- **Data streams:** 1 (WEB)
- **Google Ads links:** 0

---

## Audit findings

### Already correct

| Area | Setting |
|---|---|
| Property currency | AUD |
| Property time zone | Australia/Sydney |
| Industry category | SHOPPING |
| Web data stream exists | `Koala Homewares Web` (G-KOALAHOMES1) |
| Enhanced Measurement — page_view | ON |
| Enhanced Measurement — outbound clicks | ON |

### Needs fixing

| Area | Current | Desired | Severity | How to fix |
|---|---|---|---|---|
| Data retention | 2 months | 14 months | **high** | Manual — Admin → Data retention → 14 months |
| Unwanted referrals | empty | `checkout.stripe.com`, `www.paypal.com`, `zip.co` | **high** | Manual — Admin → Data streams → Web → Configure tag settings → Show all → List unwanted referrals |
| Google Ads link | none | linked to customer 123-456-7890 | **high** | MCP write (supported in v1.1; v1.0 = manual Admin → Product links → Google Ads) |
| Enhanced Measurement — site search | OFF | ON, query param `q` | medium | Manual — Admin → Data streams → Web → Enhanced Measurement → Configure |
| `PROPERTY_TYPE_ORDINARY` | ok | ok | — | No action |

### Manual steps (not automatable in v1.0)

1. Admin → Data collection and modification → Data retention → Event data retention = 14 months → Save.
2. Admin → Data streams → `Koala Homewares Web` → Tag settings → Show all → List unwanted referrals → add `checkout.stripe.com`, `www.paypal.com`, `zip.co`, `checkout.afterpay.com`, `buy.humm.com.au`.
3. Admin → Data streams → `Koala Homewares Web` → Enhanced Measurement → Configure → Turn ON Site search → Query parameter `q` → Save.
4. Admin → Product links → Google Ads links → Link → pick the `Koala & Co. AU` customer → enable Personalized advertising → Save.

---

## Changes applied via MCP

- **list_google_ads_links** (read) — confirmed zero links exist.
- **get_property_details** (read) — confirmed baseline metadata.
- **list_data_streams** (read) — confirmed single web stream.

No write operations performed in v1.0; all fixes are in the manual steps list above.

---

## Smoke report (last 30 days)

| Event name | Event count |
|---|---|
| `page_view` | 142,311 |
| `session_start` | 38,904 |
| `first_visit` | 22,711 |
| `scroll` | 31,552 |
| `click` | 8,433 |
| `view_item` | 6,120 |
| `add_to_cart` | 1,089 |
| `begin_checkout` | 487 |
| `purchase` | 203 |
| `form_submit` | 128 |
| `user_engagement` | 41,220 |

**Top 5 observations:**

1. Funnel is healthy: `view_item` (6,120) → `add_to_cart` (1,089) → `begin_checkout` (487) → `purchase` (203). That's a 3.3% end-to-end conversion, decent for homewares.
2. `purchase` is not yet marked as a conversion event — fix via `/ppc-manager:ga4-events`.
3. `user_engagement` is only 29% of `session_start`, suggesting high bounce. Worth exploring in `/ppc-manager:campaign-audit`.
4. `view_cart` is missing — Shopify native analytics doesn't push it. Add to the dataLayer via `/ppc-manager:gtm-datalayer` if needed for cart abandonment flows.
5. Meta-related events (e.g. `fb_ad_click_impression`) are missing — expected, because the Meta Pixel events go to Meta Ads Manager, not GA4.

---

## Next steps

1. Complete the 4 manual steps in the Admin UI. Timebox ~10 minutes.
2. Run `/ppc-manager:ga4-events` to mark `purchase` as a conversion event and create custom dimensions for `item_category`, `coupon`, and `payment_type`.
3. Run `/ppc-manager:google-ads-account-setup` to mirror the GA4 conversions into Google Ads.
4. In 7 days, re-run `/ppc-manager:ga4-setup` (audit only) to confirm the manual fixes stuck.
