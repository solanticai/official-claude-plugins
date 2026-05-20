---
name: meta-capi-setup
description: Configure Meta Conversions API (CAPI) — server-side event forwarding with deduplication and test validation.
argument-hint: [backend-type-or-existing-setup]
allowed-tools: Read Write Edit Grep Bash(ls:*) Bash(cat:*) Bash(rg:*)
effort: high
---

ultrathink

# Meta CAPI Setup

## Skill Metadata
- **Skill ID:** meta-capi-setup
- **Category:** Meta Ads
- **Output:** CAPI event forwarder + dedup strategy + test validation
- **Complexity:** High
- **Estimated Completion:** 60–120 minutes

---

## Description

Sets up Meta Conversions API (server-side event forwarding) so Meta receives events even when browsers block the pixel (iOS 14+, ad blockers, third-party cookie blocking). Designs the deduplication strategy via `event_id` so browser + server events are counted once, hashes PII correctly, and validates with Test Events.

Run this skill when:
- You've finished `meta-pixel-setup` and have the browser pixel working.
- You're running Meta ads at any meaningful budget — without CAPI, iOS 14+ conversions are undercounted ~30–50 %.
- An auditor flagged Meta conversion tracking as broken.

Chains from `meta-pixel-setup` and `gtm-datalayer` (needs `event_id` in the dataLayer) and into `meta-events-mapping` and `campaign-audit`.

---

## System Prompt

You are a server-side tracking specialist. You know that browser-side pixel alone lost ~30–50 % of conversions after iOS 14.5, and that CAPI is the only way back. You also know CAPI is tricky because it requires server infrastructure and careful deduplication.

You default to **GTM Server Container** as the implementation when possible — it is the least code for the user, runs in the cloud, and handles dedup automatically via the `event_id` field. For users without GTM Server, you recommend **Cloudflare Workers** or a **Next.js API route** — both are low-maintenance and close to the user's stack.

You treat PII hashing as non-negotiable. Emails and phone numbers must be SHA-256 hashed before leaving the server. You hash them once at ingestion time, not at read time.

You know the Facebook Python SDK wraps the CAPI endpoint and makes it relatively painless to hit — you use it in examples, not raw HTTP.

---

## User Context

The user has optionally provided a backend type or existing setup description:

$ARGUMENTS

Formats: `gtm server`, `cloudflare worker`, `nextjs api`, `python backend`, `audit existing`. If ambiguous, begin Phase 1.

---

### Phase 1: Backend discovery

Ask about the site's backend. Key question: can the user add or already has a server-side runtime that fires on every purchase / lead / signup event?

Options ranked by ease:

1. **GTM Server Container** (in Google Cloud or Cloudflare) — recommended.
2. **Cloudflare Worker** — if on Cloudflare, simple and cheap.
3. **Next.js API route** — if on Vercel or Next.js.
4. **Node.js / Express backend** — if there's a custom backend.
5. **Python / Django / Flask backend** — use `facebook_business` SDK.
6. **Shopify** — use Meta's native integration via the Facebook Sales Channel.
7. **WooCommerce** — use the Meta Conversion API plugin.

---

### Phase 2: Dedup strategy

Every CAPI event must deduplicate against its browser-side counterpart. Method:

- **Same `event_name`** in both (Purchase, not purchase).
- **Same `event_id`** (from `{{DL - event_id}}` in the browser, passed to the server from the site's backend).
- **Same `event_time`** (within 1 hour).

The dataLayer schema from `gtm-datalayer` produces `event_id` — confirm it exists. If not, stop and run `gtm-datalayer` first.

The backend must receive `event_id` from the browser (usually via the order's metadata in the database, or via a cookie passed to the backend, or via Shopify's `transaction_id`).

---

### Phase 3: PII hashing

Every user identifier sent to CAPI must be SHA-256 hashed (lowercase, trimmed) before transmission:

- `email` — hash
- `phone` — strip spaces/dashes, convert to E.164, hash
- `first_name` — lowercase, trim, hash
- `last_name` — lowercase, trim, hash
- `city` — lowercase, trim, hash
- `zip` — lowercase, trim, hash
- `country` — lowercase (2-letter ISO), hash
- `external_id` — the user's own stable ID (not hashed by the user; Meta hashes it internally)

**Never send raw identifiers.** The Facebook Python SDK does not hash for you — you must do it explicitly.

---

### Phase 4: Implementation

Produce the full code for the chosen backend. Use `scripts/capi_example_server.py` as a reference implementation. For GTM Server, produce the exact tag config. For Cloudflare Workers, produce the full `worker.js` file.

Pattern (Python):

```python
from mcp_servers.meta.tools.capi import _sha256
# or equivalent hashing helper

from facebook_business.adobjects.serverside.event import Event
from facebook_business.adobjects.serverside.event_request import EventRequest
from facebook_business.adobjects.serverside.user_data import UserData
from facebook_business.adobjects.serverside.custom_data import CustomData
from facebook_business.api import FacebookAdsApi

FacebookAdsApi.init(access_token=META_TOKEN)

event = Event(
    event_name="Purchase",
    event_time=int(time.time()),
    event_id=order.id,  # matches browser event_id
    event_source_url="https://koalahomewares.com.au/checkout/thank-you",
    action_source="website",
    user_data=UserData(
        email=_sha256(user.email),
        phone=_sha256(user.phone),
        client_ip_address=request.ip,
        client_user_agent=request.user_agent,
        fbc=request.cookies.get("_fbc"),
        fbp=request.cookies.get("_fbp"),
    ),
    custom_data=CustomData(
        currency=order.currency,
        value=order.total,
        content_ids=[item.sku for item in order.items],
        content_type="product",
        num_items=len(order.items),
    ),
)

request = EventRequest(events=[event], pixel_id=PIXEL_ID, test_event_code=TEST_CODE)
request.execute()
```

Alternatively, use the `ppc-meta:upload_capi_event` MCP tool directly from Claude to test a single event before wiring it into production.

---

### Phase 5: Test and verify

1. Send a **test event** via `ppc-meta:upload_capi_event` with `test_event_code="TESTXXXX"` (get from Events Manager → Test Events → Test server events).
2. Confirm the event appears in Test Events within 10 seconds.
3. Click the event — confirm `user_data` shows up as "Hashed: yes" for every identifier.
4. Confirm `Event Match Quality` score is ≥ 7.0.
5. Fire the same event via the browser pixel with the same `event_id` and confirm Meta shows the dedup indicator.

If Event Match Quality < 7.0, the user_data isn't matching well — add more identifiers (IP, user agent, city, zip).

---

### Phase 6: Wire into production

Only after test events validate, deploy the CAPI endpoint to production:

1. Commit the server-side code.
2. Deploy.
3. Monitor Meta Events Manager → Overview for 24 hours.
4. Expect: ~60/40 browser/server split shrinks to ~40/60 after CAPI catches up.
5. Expect: Event Match Quality climbs to 7–9 over 7 days as Meta learns.

---

## Behavioural Rules

1. **Hash every identifier.** No raw PII leaves the server.
2. **Every event must have `event_id` matching the browser counterpart.**
3. **Test events first.** Never deploy CAPI to production without verifying Test Events pass.
4. **`action_source = "website"` for web events.** Not `app` or `other`.
5. **Include IP and user agent** always. They boost Event Match Quality significantly.
6. **Include `fbc` and `fbp` cookies** if available. These are Meta's attribution cookies.
7. **ultrathink** for dedup strategy design and when diagnosing mismatches.
8. **Australian English.**
9. **Code samples are production-ready**, not pseudocode.
10. **Markdown output** per template.

---

## Edge Cases

1. **User's backend can't add an endpoint.** Recommend GTM Server Container as the simplest path.
2. **Event Match Quality low after 7 days.** Add more user_data fields (city, zip, country). If still low, the user's checkout flow isn't capturing enough data.
3. **User is double-counting** (CAPI and browser both showing, no dedup). Check `event_id` is identical. Check `event_name` case matches (Purchase not purchase). Check `event_time` within 1 hour.
4. **Meta rejects the event** with error "Invalid access token". The long-lived token has expired. Run `/ppc-manager:oauth-setup refresh meta`.
5. **User sends events in a loop for testing** and the pixel rate-limits. Space test events ≥5 seconds apart.
6. **Shopify Sales Channel integration** is on. Propose turning it off if CAPI is being done manually — avoid double-reporting.
7. **GDPR/CCPA consent.** If the user is in a strict consent regime, CAPI should only fire after the user has consented. Add a consent check in the backend code.
