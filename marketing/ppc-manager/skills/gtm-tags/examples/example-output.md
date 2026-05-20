# GTM Tags — Add Meta Pixel Purchase Event — Koala & Co. Online

**Container:** GTM-KOALA123
**Workspace:** Default Workspace
**Version:** Meta Pixel purchase event - 2026-04-11 (version_id `43`) — **Published**
**Date:** 11/04/2026

---

## Goal

Wire the Meta Pixel `Purchase` event to the same `purchase` dataLayer event GA4 and Google Ads already consume. Includes Meta Pixel base install (wasn't present before), the Purchase event tag with deduplication via `event_id`, and a Custom JS variable to convert the `items[]` array into Meta's `content_ids` format. This is the browser-side of Meta Pixel — the server-side (CAPI) will be wired separately via `/ppc-manager:meta-capi-setup`.

---

## Changes applied

### Variables created

| Name | Type | Parameter |
|---|---|---|
| `CONST - Meta Pixel ID` | Constant | `123456789012345` |
| `JS - items to content_ids` | Custom JS | `function() { return ({{DL - items}} || []).map(function(i){return i.item_id}); }` |
| `JS - items length` | Custom JS | `function() { return ({{DL - items}} || []).length; }` |

### Triggers created

| Name | Type | Filter |
|---|---|---|
| `Custom Event - purchase` | Custom Event | `event equals purchase` (re-used existing) |

### Tags created

| Name | Type | Firing trigger | Key parameters |
|---|---|---|---|
| `Con - Meta - Pixel Base` | Custom HTML | All Pages - Page View | `fbq('init', '{{CONST - Meta Pixel ID}}')` + `fbq('track', 'PageView')` |
| `Con - Meta - Event - Purchase` | Custom HTML | Custom Event - purchase | `fbq('track', 'Purchase', {...}, { eventID: '{{DL - event_id}}' })` |

### Tags updated

(none)

---

## Preview verification

- **Preview URL:** `https://tagassistant.google.com/?container_id=GTM-KOALA123&version_id=43`
- **Steps performed:**
  1. Opened preview URL, clicked Connect.
  2. Navigated to `https://koalahomewares.com.au/products/wool-throw`.
  3. Clicked Add to Cart.
  4. Proceeded through checkout with a test card.
  5. Landed on the order thank-you page.
- **Tags fired in preview:**
  - `Con - Meta - Pixel Base` — fired on every page view (correct)
  - `Con - Meta - Event - Purchase` — fired once on the thank-you page (correct)
- **Parameter values observed:**
  - `value: 129.00`, `currency: 'AUD'`, `content_ids: ['SKU_WLT_001']`, `content_type: 'product'`, `num_items: 1`
  - `eventID: '10042-abcd1234'` (matches `{{DL - transaction_id}}-{{checkout token}}`)
- **Verification confirmed by user:** yes at 11/04/2026 14:32 AEST

---

## Published version

- **Version ID:** 43
- **Published at:** 11/04/2026 14:35 AEST
- **Published by:** the ppc-gtm MCP (user-authorised)

---

## Next steps

1. Monitor Meta Events Manager → Test Events for 1 hour to confirm the event arrives. Navigate to [business.facebook.com/events_manager](https://business.facebook.com/events_manager), pick the pixel, and watch Real-time.
2. Run `/ppc-manager:meta-capi-setup` to wire the server-side Conversions API so Meta receives events even when the browser is blocked.
3. After CAPI is installed, run `/ppc-manager:meta-events-mapping` to reconcile browser vs. server dedup.
4. In 48 hours, run `/ppc-manager:campaign-audit` scoped to Meta to verify ROAS attribution is calculating correctly.
