# GTM DataLayer — Reference

Dense reference material for dataLayer schema design: the GA4 recommended event catalogue, Enhanced Ecommerce spec, param type rules, and the canonical event-ID generation helpers.

## Contents

1. [GA4 automatically-collected events (do not duplicate)](#1-ga4-automatically-collected-events-do-not-duplicate)
2. [GA4 recommended events by vertical](#2-ga4-recommended-events-by-vertical)
3. [Items array shape (Enhanced Ecommerce)](#3-items-array-shape-enhanced-ecommerce)
4. [Event ID generation helpers](#4-event-id-generation-helpers)
5. [PII hashing](#5-pii-hashing)
6. [Push patterns by framework](#6-push-patterns-by-framework)
7. [Anti-patterns — do not produce schemas that look like this](#7-anti-patterns--do-not-produce-schemas-that-look-like-this)

---

## 1. GA4 automatically-collected events (do not duplicate)

GA4 fires these automatically when the GA4 Config tag is installed. Do not re-create them in the dataLayer — just rely on GA4 or supplement them if needed.

| Event | Fires when |
|---|---|
| `first_visit` | First time a user visits |
| `session_start` | Session begins |
| `page_view` | Page loads (if `sendPageView=true` on GA4 Config) |
| `user_engagement` | User has engaged with the page for 10+ seconds |
| `scroll` | User scrolls to 90 % of the page (if Enhanced Measurement is on) |
| `click` | Outbound link click (if Enhanced Measurement is on) |
| `view_search_results` | URL contains a search query parameter (if Enhanced Measurement is on) |
| `video_start`, `video_progress`, `video_complete` | YouTube embeds (if Enhanced Measurement is on) |
| `file_download` | User clicks a link pointing at a file extension (if Enhanced Measurement is on) |

**Rule:** if Enhanced Measurement handles it, don't push it from the dataLayer. Only supplement.

---

## 2. GA4 recommended events by vertical

From [support.google.com/analytics/answer/9267735](https://support.google.com/analytics/answer/9267735). Use these names verbatim for maximum downstream compatibility.

### E-commerce (online sales)

| Event | Required params | Optional params |
|---|---|---|
| `view_item_list` | `items` | `item_list_name`, `item_list_id` |
| `view_item` | `currency`, `value`, `items` | |
| `select_item` | `items` | `item_list_name`, `item_list_id` |
| `add_to_cart` | `currency`, `value`, `items` | |
| `remove_from_cart` | `currency`, `value`, `items` | |
| `view_cart` | `currency`, `value`, `items` | |
| `begin_checkout` | `currency`, `value`, `items` | `coupon` |
| `add_shipping_info` | `currency`, `value`, `items` | `shipping_tier`, `coupon` |
| `add_payment_info` | `currency`, `value`, `items` | `payment_type`, `coupon` |
| `purchase` | `transaction_id`, `currency`, `value`, `items` | `tax`, `shipping`, `coupon`, `affiliation` |
| `refund` | `transaction_id` | `currency`, `value`, `items` |
| `view_promotion` | `items` or `promotion_name`/`promotion_id` | `creative_name`, `creative_slot`, `location_id` |
| `select_promotion` | `items` or `promotion_name`/`promotion_id` | |

### Lead-gen / service business

| Event | Required | Optional |
|---|---|---|
| `generate_lead` | `currency`, `value` | `form_id`, `form_name`, `form_destination` |
| `form_start` | `form_id`, `form_name` | `form_destination` |
| `form_submit` | `form_id`, `form_name` | `form_destination` |
| `contact` | `method` | `form_id` |
| `click_phone` | `phone_number` | |
| `click_email` | `email_domain` (masked) | |

### SaaS

| Event | Required | Optional |
|---|---|---|
| `sign_up` | `method` | `signup_plan` |
| `login` | `method` | |
| `view_pricing` | `pricing_plan` | |
| `start_trial` | `value`, `currency`, `trial_days` | `plan_id`, `plan_name` |
| `purchase` | same as e-commerce | |

### Content / publisher

| Event | Required | Optional |
|---|---|---|
| `view_article` | `article_id`, `article_category` | `author` |
| `scroll` | (auto) | |
| `newsletter_signup` | `list_name` | |
| `share` | `method`, `content_type` | `item_id` |
| `search_site` | `search_term` | |

---

## 3. Items array shape (Enhanced Ecommerce)

All e-commerce events use the same `items[]` shape.

```json
{
  "items": [
    {
      "item_id": "SKU_12345",
      "item_name": "Koala Throw",
      "affiliation": "Koala Direct",
      "coupon": "WINTER10",
      "discount": 13.00,
      "index": 0,
      "item_brand": "Koala",
      "item_category": "Homewares",
      "item_category2": "Throws",
      "item_category3": "Wool",
      "item_category4": "",
      "item_category5": "",
      "item_list_id": "related_products",
      "item_list_name": "Related products",
      "item_variant": "Natural",
      "location_id": "ChIJtest",
      "price": 129.00,
      "quantity": 1
    }
  ]
}
```

**Type rules:**
- `price`, `discount`, `tax`, `shipping`, `value` — always numbers (not strings). Decimals OK. Two decimals max in most cases.
- `quantity` — integer.
- `currency` — ISO 4217 string (`AUD`, `USD`, `EUR`, `GBP`, `NZD`). Always uppercase.
- `item_id` — string. Stable across sessions.
- Arrays of items — max 200, recommended max 50.

---

## 4. Event ID generation helpers

Every event must have a unique `event_id` for Meta CAPI deduplication. Helpers for common backends:

### Browser JS

```js
function generateEventId() {
  if (window.crypto && window.crypto.randomUUID) {
    return window.crypto.randomUUID();
  }
  return 'evt_' + Date.now() + '_' + Math.random().toString(36).slice(2, 10);
}
```

### Node.js

```js
import { randomUUID } from 'node:crypto';
const eventId = randomUUID();
```

### Python

```python
import uuid
event_id = str(uuid.uuid4())
```

### PHP

```php
$eventId = bin2hex(random_bytes(16));
```

---

## 5. PII hashing

Before pushing any identifier to the dataLayer, hash it. Meta and Google both expect SHA-256 over the **lowercased, trimmed** string.

### Browser helper

```js
async function sha256(value) {
  const trimmed = String(value || '').trim().toLowerCase();
  const buf = new TextEncoder().encode(trimmed);
  const hash = await crypto.subtle.digest('SHA-256', buf);
  return Array.from(new Uint8Array(hash))
    .map(b => b.toString(16).padStart(2, '0'))
    .join('');
}

// usage
sha256('john@anthril.com').then(hashed => {
  trackEvent('login', { user_data: { email_hash: hashed, method: 'password' } });
});
```

### Rules

- Never push a raw email, phone number, or full name.
- Emails: lowercase, trim whitespace, then SHA-256.
- Phone numbers: remove spaces/dashes/parentheses, E.164 format (e.g. `+61400123456`), then SHA-256.
- Names: lowercase, trim, then SHA-256. Do not normalise accents — it makes cross-platform matching worse.
- Store the hash in `user_data.*_hash` fields. Downstream skills (`meta-capi-setup`) know to consume these keys.

---

## 6. Push patterns by framework

### Shopify

Shopify exposes `{{ order.line_items | json }}` in the checkout template. Use Shopify's pixel API or a thank-you page script:

```liquid
{% if first_time_accessed %}
<script>
  window.dataLayer = window.dataLayer || [];
  window.dataLayer.push({
    event: 'purchase',
    event_id: '{{ order.order_number }}-{{ checkout.token }}',
    transaction_id: '{{ order.order_number }}',
    currency: '{{ order.currency }}',
    value: {{ order.total_price | money_without_currency }},
    items: {{ order.line_items | map: 'formatted_line_item' | json }}
  });
</script>
{% endif %}
```

### React / Next.js SPA

```jsx
// hooks/useTrackPageView.js
import { useEffect } from 'react';
import { useRouter } from 'next/router';

export function useTrackPageView() {
  const router = useRouter();
  useEffect(() => {
    const handler = (url) => {
      window.dataLayer = window.dataLayer || [];
      window.dataLayer.push({
        event: 'page_view',
        event_id: crypto.randomUUID(),
        page_location: window.location.href,
        page_path: url,
        page_referrer: document.referrer,
        page_title: document.title,
      });
    };
    router.events.on('routeChangeComplete', handler);
    return () => router.events.off('routeChangeComplete', handler);
  }, [router]);
}
```

### WordPress / WooCommerce

Use a functions.php hook or a plugin like GTM4WP that already pushes Enhanced Ecommerce by default.

---

## 7. Anti-patterns — do not produce schemas that look like this

- `event: 'conversion'` — too vague. Use `purchase`, `generate_lead`, `sign_up`.
- `event: 'gtm.click'` — that is a built-in GTM event, don't override.
- `event: 'pageview'` — GA4 wants `page_view` (underscore).
- Overloaded `items[]` — one event per list context, not one push with items from 3 different lists.
- Missing `event_id` — blocks Meta CAPI dedup.
- Raw PII — `user_data.email: 'john@example.com'`. Hash it.
- `value` as a string — `value: '129.00'` breaks GA4 aggregation. Use `value: 129.00`.
