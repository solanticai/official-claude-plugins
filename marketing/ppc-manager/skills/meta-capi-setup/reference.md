# Meta CAPI Setup — Reference

## 1. user_data fields

| Field | Treatment | Purpose |
|---|---|---|
| `email` | SHA-256 (lowercased, trimmed) | Strongest match signal |
| `phone` | SHA-256 (E.164 format) | Strong match |
| `first_name` | SHA-256 | Medium match |
| `last_name` | SHA-256 | Medium match |
| `city` | SHA-256 | Boosts EMQ |
| `zip` | SHA-256 | Boosts EMQ |
| `country` | SHA-256 (ISO 2-letter, lowercase) | Boosts EMQ |
| `external_id` | Raw (Meta hashes) | User's own stable ID |
| `client_ip_address` | Raw | Boosts EMQ |
| `client_user_agent` | Raw | Boosts EMQ |
| `fbc` | Raw | Attribution cookie from Meta |
| `fbp` | Raw | Pixel cookie |

## 2. Event Match Quality tiers

| EMQ score | Quality |
|---|---|
| 0–2.9 | Poor (few identifiers matching) |
| 3.0–5.9 | Fair |
| 6.0–6.9 | Good |
| 7.0–8.9 | Great (target) |
| 9.0–10.0 | Excellent |

## 3. GTM Server Container setup (high level)

1. Create a GTM Server container in GTM web UI → New Container → Server.
2. Host on Cloudflare Workers (cheapest), Google App Engine, or container on GCP Run.
3. Configure the server container URL in the browser container via the Google Tag config.
4. Install the **Facebook Conversions API** tag template from the Community Template Gallery.
5. Configure with pixel ID + access token + event name mappings.
6. Publish.

## 4. Cloudflare Worker sample (minimal)

```js
// worker.js
import { Event, EventRequest, UserData, CustomData } from '@facebook/business-sdk';

async function sha256(value) {
  const buf = new TextEncoder().encode(value.trim().toLowerCase());
  const hash = await crypto.subtle.digest('SHA-256', buf);
  return Array.from(new Uint8Array(hash))
    .map(b => b.toString(16).padStart(2, '0'))
    .join('');
}

export default {
  async fetch(request, env) {
    if (request.method !== 'POST') return new Response('Method not allowed', { status: 405 });
    const body = await request.json();

    const user_data = new UserData({
      email: body.email ? await sha256(body.email) : undefined,
      phone: body.phone ? await sha256(body.phone.replace(/\D/g, '')) : undefined,
      client_ip_address: request.headers.get('cf-connecting-ip'),
      client_user_agent: request.headers.get('user-agent'),
      fbc: body.fbc,
      fbp: body.fbp,
    });

    const custom_data = new CustomData({
      currency: body.currency,
      value: body.value,
      content_ids: body.content_ids,
      content_type: 'product',
    });

    const event = new Event({
      event_name: body.event_name,
      event_time: Math.floor(Date.now() / 1000),
      event_id: body.event_id,
      event_source_url: body.event_source_url,
      action_source: 'website',
      user_data,
      custom_data,
    });

    const req = new EventRequest({
      events: [event],
      pixel_id: env.META_PIXEL_ID,
      access_token: env.META_ACCESS_TOKEN,
      test_event_code: env.META_TEST_EVENT_CODE, // remove in production
    });

    const result = await req.execute();
    return new Response(JSON.stringify(result), {
      headers: { 'content-type': 'application/json' },
    });
  },
};
```

## 5. Next.js API route sample

```ts
// pages/api/capi.ts
import type { NextApiRequest, NextApiResponse } from 'next';
import { createHash } from 'crypto';
const bizSdk = require('facebook-nodejs-business-sdk');

const { Event, EventRequest, UserData, CustomData, FacebookAdsApi } = bizSdk;

const access_token = process.env.META_ACCESS_TOKEN!;
const pixel_id = process.env.META_PIXEL_ID!;
FacebookAdsApi.init(access_token);

const sha256 = (v: string) =>
  createHash('sha256').update(v.trim().toLowerCase()).digest('hex');

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') return res.status(405).end();
  const { event_name, event_id, email, phone, value, currency, content_ids, event_source_url } = req.body;

  const user_data = (new UserData())
    .setEmail(email ? sha256(email) : undefined)
    .setPhone(phone ? sha256(phone.replace(/\D/g, '')) : undefined)
    .setClientIpAddress(req.headers['x-forwarded-for'] || req.socket.remoteAddress)
    .setClientUserAgent(req.headers['user-agent']);

  const custom_data = (new CustomData())
    .setCurrency(currency)
    .setValue(value)
    .setContentIds(content_ids)
    .setContentType('product');

  const event = (new Event())
    .setEventName(event_name)
    .setEventTime(Math.floor(Date.now() / 1000))
    .setEventId(event_id)
    .setEventSourceUrl(event_source_url)
    .setActionSource('website')
    .setUserData(user_data)
    .setCustomData(custom_data);

  const request = (new EventRequest(access_token, pixel_id))
    .setEvents([event]);

  try {
    const result = await request.execute();
    res.status(200).json({ ok: true, result });
  } catch (err) {
    res.status(500).json({ ok: false, err: err.message });
  }
}
```

## 6. Common CAPI errors

| Error | Meaning | Fix |
|---|---|---|
| `Invalid access token` | Long-lived token expired | `/ppc-manager:oauth-setup refresh meta` |
| `Pixel ID not found` | Pixel ID typo or wrong account | Verify via `ppc-meta:list_pixels` |
| `Missing user_data` | No identifiers | Add at least email or phone |
| `test_event_code` error | Test code not recognised | Get a fresh one from Events Manager |
| `Event too far in the past` | `event_time` > 7 days old | Refuse old events (GDPR compliance issue anyway) |
