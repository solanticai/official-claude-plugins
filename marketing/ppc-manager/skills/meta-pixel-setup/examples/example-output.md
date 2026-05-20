# Meta Pixel Setup — Koala & Co. Online

**Pixel ID:** 123456789012345
**Container:** GTM-KOALA123
**Date:** 11/04/2026

---

## Events installed

| Event | Trigger | Params | eventID used |
|---|---|---|---|
| PageView | All Pages - Page View | — | — (page views don't need dedup) |
| ViewContent | Custom Event `view_item` | `content_ids`, `content_type`, `value`, `currency` | `{{DL - event_id}}` |
| AddToCart | Custom Event `add_to_cart` | `content_ids`, `content_type`, `value`, `currency`, `num_items` | `{{DL - event_id}}` |
| InitiateCheckout | Custom Event `begin_checkout` | `value`, `currency`, `num_items`, `content_ids` | `{{DL - event_id}}` |
| AddPaymentInfo | Custom Event `add_payment_info` | `value`, `currency` | `{{DL - event_id}}` |
| Purchase | Custom Event `purchase` | `value`, `currency`, `content_ids`, `content_type`, `num_items` | `{{DL - event_id}}` |
| Lead | Custom Event `newsletter_signup` | — | `{{DL - event_id}}` |

Total: 7 event tags + 1 base pixel tag.

---

## AEM priority ranking (top 8)

1. Purchase
2. InitiateCheckout
3. AddToCart
4. AddPaymentInfo
5. ViewContent
6. Lead
7. (nothing — only 6 configured)
8. (nothing)

---

## Verification

- [x] Base pixel fires on All Pages
- [x] All 6 event tags fire in GTM preview
- [x] Every event has `eventID` populated (verified in Test Events detail)
- [x] Events appear in Meta Events Manager Test Events within 10 seconds

---

## Next steps

1. Run `/ppc-manager:meta-capi-setup` — server-side CAPI using the GTM Server container Koala has on Cloudflare Workers.
2. Run `/ppc-manager:meta-events-mapping` to produce the cross-platform event dictionary (GA4 ↔ Meta ↔ GTM).
3. Rank the 6 events in Events Manager → Aggregated Event Measurement per the priority order above.
4. Wait 48 hours, then check attribution in Meta Ads Manager.
