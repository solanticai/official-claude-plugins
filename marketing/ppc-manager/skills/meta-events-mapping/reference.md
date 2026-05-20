# Meta Events Mapping — Reference

## 1. Canonical event dictionary (2026)

| Business event | GA4 | Meta Pixel | Meta CAPI | GTM DL | TikTok Pixel | LinkedIn Insight |
|---|---|---|---|---|---|---|
| Page load | page_view | PageView | PageView | page_view | Pageview | (auto) |
| Product view | view_item | ViewContent | ViewContent | view_item | ViewContent | ViewProduct |
| Category view | view_item_list | (ViewContent) | (ViewContent) | view_item_list | (ViewContent) | — |
| Search | view_search_results | Search | Search | search | Search | — |
| Add to cart | add_to_cart | AddToCart | AddToCart | add_to_cart | AddToCart | AddToCart |
| Begin checkout | begin_checkout | InitiateCheckout | InitiateCheckout | begin_checkout | InitiateCheckout | Purchase |
| Add payment | add_payment_info | AddPaymentInfo | AddPaymentInfo | add_payment_info | — | — |
| Purchase | purchase | Purchase | Purchase | purchase | CompletePayment | Purchase |
| Lead | generate_lead | Lead | Lead | generate_lead | SubmitForm | Lead |
| Signup | sign_up | CompleteRegistration | CompleteRegistration | sign_up | CompleteRegistration | Signup |
| Newsletter | newsletter_signup | Subscribe | Subscribe | newsletter_signup | Subscribe | — |
| Phone click | click_phone | Contact | Contact | click_phone | Contact | — |
| Email click | click_email | Contact | Contact | click_email | Contact | — |
| File download | file_download (auto) | — | — | file_download | — | — |
| Schedule | schedule | Schedule | Schedule | schedule | Schedule | — |
| Contact form | contact | Contact | Contact | contact | Contact | Lead |

## 2. Param mapping

| Param name | GA4 | Meta Pixel | Meta CAPI (custom_data) | GTM key |
|---|---|---|---|---|
| Currency | `currency` | `currency` | `currency` | `DL - currency` |
| Value | `value` | `value` | `value` | `DL - value` |
| Item IDs | `items[].item_id` | `content_ids` | `content_ids` | derived via JS helper |
| Item names | `items[].item_name` | `content_name` | `content_name` | derived |
| Content type | `items[].item_category` | `content_type` | `content_type` | usually `'product'` |
| Transaction ID | `transaction_id` | — | `event_id` | `DL - transaction_id` |
| Num items | — | `num_items` | `num_items` | derived from items length |
| Search term | `search_term` | `search_string` | `search_string` | `DL - search_term` |
| Status | — | `status` | `status` | — |

## 3. Common mismatch patterns

- Meta reports `Purchase` once, GA4 reports `purchase` multiple times: typically because the thank-you page refreshed and no dedup is in place. Fix: use `transaction_id` as the GA4 dedup key and `event_id` for Meta dedup.
- GA4 shows 200 purchases, Meta shows 95: browser pixel is being blocked. Fix: add CAPI (`meta-capi-setup`).
- GA4 shows AUD 25,000, Meta shows USD 16,000: Meta auto-converts if currency is set. Fine but note the difference.
- GA4 fires `add_to_cart`, Meta fires `AddToCart`, but currencies don't match: verify `DL - currency` is the same string everywhere.

## 4. Output dictionary format

Every event row in the output dictionary should include:
- Business name
- Trigger (when it fires)
- Owner (who is responsible for maintaining it)
- GA4 event name + GA4 param schema
- Meta Pixel event name + Meta Pixel param schema
- Meta CAPI event name + CAPI user_data / custom_data keys
- GTM dataLayer event name + variables consumed
- Notes (custom rationale, exceptions)
