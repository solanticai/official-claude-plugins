# Meta Pixel Setup — Reference

## 1. Meta standard events

| Event | When to fire | Required params |
|---|---|---|
| PageView | Every page load | — |
| ViewContent | Product detail page view | content_ids, content_type, value, currency |
| Search | Site search submitted | search_string |
| AddToCart | Add to cart click | content_ids, content_type, value, currency |
| AddToWishlist | Add to wishlist click | content_ids |
| InitiateCheckout | Checkout page load | value, currency |
| AddPaymentInfo | Payment step complete | — |
| Purchase | Order thank-you page | value, currency, content_ids, content_type |
| Lead | Form submit (lead gen) | value (optional) |
| CompleteRegistration | Account created | — |
| Contact | Phone / email click | — |
| Schedule | Appointment booked | — |
| SubmitApplication | Application submitted | — |

## 2. Pixel base code (GTM Custom HTML)

```html
<script>
!function(f,b,e,v,n,t,s){
  if(f.fbq)return;n=f.fbq=function(){n.callMethod?
  n.callMethod.apply(n,arguments):n.queue.push(arguments)};
  if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
  n.queue=[];t=b.createElement(e);t.async=!0;
  t.src=v;s=b.getElementsByTagName(e)[0];
  s.parentNode.insertBefore(t,s)}(window, document,'script',
  'https://connect.facebook.net/en_US/fbevents.js');
fbq('init', '{{CONST - Meta Pixel ID}}');
fbq('track', 'PageView');
</script>
```

Firing trigger: `All Pages - Page View`. Priority 100.

## 3. Event tag body (Custom HTML — example: Purchase)

```html
<script>
fbq('track', 'Purchase', {
  value: {{DL - value}},
  currency: '{{DL - currency}}',
  content_ids: {{JS - items to content_ids}},
  content_type: 'product',
  num_items: {{JS - items length}}
}, { eventID: '{{DL - event_id}}' });
</script>
```

Firing trigger: Custom Event `event equals purchase`.

## 4. GA4 → Meta event mapping

| GA4 | Meta |
|---|---|
| `page_view` | `PageView` |
| `view_item` | `ViewContent` |
| `view_item_list` | (no direct equivalent, sometimes treated as ViewContent) |
| `search` | `Search` |
| `add_to_cart` | `AddToCart` |
| `add_to_wishlist` | `AddToWishlist` |
| `begin_checkout` | `InitiateCheckout` |
| `add_payment_info` | `AddPaymentInfo` |
| `purchase` | `Purchase` |
| `generate_lead` | `Lead` |
| `sign_up` | `CompleteRegistration` |
| `contact` | `Contact` |

## 5. Aggregated Event Measurement (AEM)

Meta caps you at 8 events per verified domain. Rank them by priority in Events Manager. Standard priority for e-commerce:

1. Purchase (most important)
2. InitiateCheckout
3. AddToCart
4. ViewContent
5. Search
6. Lead (if applicable)
7. AddPaymentInfo
8. AddToWishlist (lowest priority)

Any events beyond 8 are dropped for iOS 14+ attribution.

## 6. Test Events flow

1. Meta Events Manager → Data Sources → pick pixel → Test Events tab.
2. Paste the live site URL OR use the Test Event Code (starts with `TEST`).
3. Navigate the site; events appear in Test Events within seconds.
4. Click an event to see full params + eventID.

If an event doesn't appear:
- Check GTM preview — is the tag firing?
- Check browser console for `fbq not defined` errors (base tag missing).
- Check ad blockers — disable uBlock / AdBlock for testing.
- Confirm `fbq('init', ...)` runs before `fbq('track', ...)`.
