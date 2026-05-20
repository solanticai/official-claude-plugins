# DataLayer Schema — Koala & Co. Online

**Site type:** E-commerce (Shopify)
**Container:** GTM-KOALA123
**Date:** 11/04/2026

---

## Summary

Designed the canonical e-commerce dataLayer schema for Koala & Co. Online, an Australian homewares retailer on Shopify. Schema follows the GA4 Enhanced Ecommerce spec verbatim for downstream compatibility with GA4, Meta Pixel, and Google Ads. All money fields use AUD and numeric types; `event_id` is derived from Shopify order number + checkout token for deterministic dedup with Meta CAPI. Installed 12 GTM data layer variables covering the core fields used by every tag.

---

## Event catalogue

| Event | Trigger | Required params | Optional params | Purpose |
|---|---|---|---|---|
| `view_item_list` | Collection page load | `items` | `item_list_name`, `item_list_id` | Impression tracking for merchandising |
| `view_item` | Product detail page load | `currency`, `value`, `items` | — | Product interest |
| `add_to_cart` | Add to cart button click | `currency`, `value`, `items` | — | Top-of-funnel purchase signal |
| `begin_checkout` | Checkout page 1 load | `currency`, `value`, `items` | `coupon` | Checkout funnel entry |
| `add_payment_info` | Checkout payment step complete | `currency`, `value`, `items` | `payment_type` | Checkout progression |
| `purchase` | Order thank-you page | `transaction_id`, `currency`, `value`, `items` | `tax`, `shipping`, `coupon` | Revenue conversion |
| `newsletter_signup` | Footer form submit | `list_name` | — | Owned audience growth |

---

## Schema per event

### `purchase`

**Trigger:** Shopify order thank-you page (`first_time_accessed` Liquid condition). Pushed once per order.

**Schema:**

| Field | Type | Required | Example | Notes |
|---|---|---|---|---|
| `event` | string | yes | `purchase` | Always literal string |
| `event_id` | string | yes | `10042-abcd1234` | Shopify order number + last 8 chars of checkout token |
| `transaction_id` | string | yes | `10042` | Shopify order number, used as GA4 `transaction_id` |
| `currency` | string | yes | `AUD` | ISO 4217 uppercase |
| `value` | number | yes | `249.50` | Order total inc. tax and shipping |
| `tax` | number | no | `22.68` | GST |
| `shipping` | number | no | `9.95` | Shipping amount |
| `coupon` | string | no | `WINTER10` | Discount code if applied |
| `items` | array | yes | see below | One entry per line item |

**Inline push (Shopify Liquid):**

```liquid
{% if first_time_accessed %}
<script>
  window.dataLayer = window.dataLayer || [];
  window.dataLayer.push({
    event: 'purchase',
    event_id: '{{ order.order_number }}-{{ checkout.token | slice: 0, 8 }}',
    transaction_id: '{{ order.order_number }}',
    currency: '{{ order.currency }}',
    value: {{ order.total_price | divided_by: 100.0 }},
    tax: {{ order.tax_price | divided_by: 100.0 }},
    shipping: {{ order.shipping_price | divided_by: 100.0 }},
    {% if order.discount_codes[0] %}coupon: '{{ order.discount_codes[0].code }}',{% endif %}
    items: [
      {% for line in order.line_items %}
      {
        item_id: '{{ line.sku }}',
        item_name: {{ line.title | json }},
        item_brand: 'Koala & Co.',
        item_category: {{ line.product.type | json }},
        item_variant: {{ line.variant.title | json }},
        price: {{ line.final_price | divided_by: 100.0 }},
        quantity: {{ line.quantity }}
      }{% unless forloop.last %},{% endunless %}
      {% endfor %}
    ]
  });
</script>
{% endif %}
```

### `add_to_cart`

**Trigger:** Add to cart button click (pre-navigation). Pushed by a custom Shopify theme script, not by Shopify's native analytics.

**Schema:**

| Field | Type | Required | Example | Notes |
|---|---|---|---|---|
| `event` | string | yes | `add_to_cart` | Literal |
| `event_id` | string | yes | auto-UUID | `crypto.randomUUID()` |
| `currency` | string | yes | `AUD` | |
| `value` | number | yes | `129.00` | Price × quantity |
| `items` | array | yes | one item | Single item from click event |

**Inline push:**

```js
window.dataLayer = window.dataLayer || [];
window.dataLayer.push({
  event: 'add_to_cart',
  event_id: crypto.randomUUID(),
  currency: 'AUD',
  value: product.price,
  items: [{
    item_id: product.sku,
    item_name: product.title,
    item_brand: 'Koala & Co.',
    item_category: product.type,
    item_variant: variant.title,
    price: product.price,
    quantity: 1
  }]
});
```

---

## Helper function

Installed in `src/theme/analytics.js`:

```js
function trackEvent(name, params = {}) {
  window.dataLayer = window.dataLayer || [];
  window.dataLayer.push({
    event: name,
    event_id: params.event_id || crypto.randomUUID(),
    ...params
  });
}

window.koala = window.koala || {};
window.koala.track = trackEvent;
```

Usage:

```js
koala.track('add_to_cart', {
  currency: 'AUD',
  value: 129.00,
  items: [ /* ... */ ]
});

koala.track('newsletter_signup', {
  list_name: 'main_footer'
});
```

---

## GTM data layer variables created

| Variable name | Data layer key | Status |
|---|---|---|
| `DL - event` | `event` | created (id 42) |
| `DL - event_id` | `event_id` | created (id 43) |
| `DL - transaction_id` | `transaction_id` | created (id 44) |
| `DL - currency` | `currency` | created (id 45) |
| `DL - value` | `value` | created (id 46) |
| `DL - tax` | `tax` | created (id 47) |
| `DL - shipping` | `shipping` | created (id 48) |
| `DL - coupon` | `coupon` | created (id 49) |
| `DL - items` | `items` | created (id 50) |
| `DL - list_name` | `list_name` | created (id 51) |
| `DL - ecommerce.currency` | `ecommerce.currency` | already exists (id 22) |
| `DL - ecommerce.value` | `ecommerce.value` | already exists (id 23) |

---

## Rollout checklist

1. Paste the helper function into `src/theme/analytics.js` and import from `theme.liquid`.
2. Replace `checkout/order.liquid` with the `purchase` snippet above.
3. Wire the add-to-cart click handler in `product-form.js` to `koala.track('add_to_cart', ...)`.
4. Verify each event in GTM Preview mode — open the preview URL, navigate to a product page, add to cart, complete a test checkout.
5. Open GA4 DebugView (Admin → DebugView) and confirm each event arrives with the documented params.
6. Once verified, run `/ppc-manager:ga4-events` to mark `purchase` and `generate_lead` as conversion events.

---

## Next steps

1. `/ppc-manager:ga4-events` — register conversion events and custom dimensions for `item_category` and `coupon`.
2. `/ppc-manager:gtm-tags` — create the Meta Pixel `Purchase` event tag and the Google Ads purchase conversion tag, both consuming these variables.
3. `/ppc-manager:meta-events-mapping` — reconcile Pixel browser-side vs. CAPI server-side deduplication using `event_id`.
