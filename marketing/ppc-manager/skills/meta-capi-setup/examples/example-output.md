# Meta CAPI Setup — Koala & Co. Online

**Pixel ID:** 123456789012345
**Backend:** Cloudflare Worker (Koala hosts on Cloudflare)
**Date:** 11/04/2026

---

## Dedup strategy

- `event_id` source: `{{ order.order_number }}-{{ checkout.token | slice: 0, 8 }}` (from `gtm-datalayer`)
- Browser events: fired from GTM via `meta-pixel-setup`
- Server events: fired from `api.koalahomewares.com.au/capi` on every Shopify order
- Dedup method: matching `event_name` (Purchase) + `event_id`

---

## Events forwarded server-side

| Event | Params | `user_data` fields | EMQ target |
|---|---|---|---|
| Purchase | currency, value, content_ids, content_type, num_items | email, phone, fn, ln, city, zip, country, client_ip_address, client_user_agent, fbc, fbp | ≥8.0 |
| Lead | — | email, client_ip_address, client_user_agent, fbc, fbp | ≥6.0 |
| InitiateCheckout | value, currency | email, client_ip_address, client_user_agent, fbc, fbp | ≥6.0 |

Only Purchase, Lead, and InitiateCheckout are CAPI-forwarded — lower-funnel events (ViewContent, AddToCart) stay browser-only to reduce noise.

---

## Implementation

- **Backend:** Cloudflare Worker
- **File path:** `workers/meta-capi/src/index.ts`
- **Deploy target:** `api.koalahomewares.com.au/capi`
- **Code:** adapted from `reference.md` Section 4 (Cloudflare Worker sample). Reads pixel ID, access token, and test event code from Cloudflare Worker environment variables.

### Deployment

```bash
wrangler deploy
```

### Env vars (Cloudflare secrets)

```
META_PIXEL_ID = 123456789012345
META_ACCESS_TOKEN = <long-lived token from ppc-manager vault>
META_TEST_EVENT_CODE = TESTAKOALA (for staging only, remove in production)
```

---

## Test Events validation

- Test code used: `TESTAKOALA`
- Events sent: 12 (1 Purchase, 3 Lead, 8 InitiateCheckout over 10 minutes)
- Events received in Test Events: 12/12
- Current EMQ: 7.8 (Purchase), 5.9 (Lead), 6.1 (InitiateCheckout)
- Target EMQ: 7.0+ — Purchase exceeds, Lead needs more user_data (add city/zip if available)

---

## Production checklist

- [x] PII hashed (SHA-256, lowercased, trimmed) — worker uses `crypto.subtle.digest('SHA-256', ...)`
- [x] `event_id` matches browser counterpart — verified via Shopify order metadata passed through
- [x] `action_source = "website"`
- [x] IP and user_agent included — from `cf-connecting-ip` and `user-agent` headers
- [x] `fbc` and `fbp` cookies forwarded — passed from browser in the POST body
- [ ] Test event code removed from production — **not yet**, staging still uses `TESTAKOALA`
- [x] Access token stored in env vars, not source — Cloudflare Worker secret

---

## Next steps

1. Deploy to Cloudflare production env (remove `META_TEST_EVENT_CODE` secret).
2. Monitor Events Manager → Overview for 48 hours. Expect total events to increase 30–50 % as CAPI catches what the browser pixel loses to ad blockers.
3. Run `/ppc-manager:meta-events-mapping` to produce the cross-platform event dictionary.
4. If `Lead` EMQ stays below 7.0 after a week, add `city` and `zip` from the form to the CAPI payload.
