# GA4 Setup — Reference

---

## 1. GA4 property baseline checklist

Use this as the canonical "what good looks like" for any property audit.

| Area | Setting | Desired value |
|---|---|---|
| Property | Industry category | Matches the business (RETAIL, FINANCE, TECHNOLOGY, etc.) |
| Property | Currency | User's primary currency (AUD for AU) |
| Property | Time zone | User's primary timezone (Australia/Sydney) |
| Property | Data retention | 14 months (standard) or 50 months (GA4 360) |
| Property | Reset user data on new activity | ON (default) |
| Property | Google signals | User choice — default OFF for new AU properties (privacy) |
| Data stream (Web) | Exists | Yes |
| Data stream (Web) | Enhanced Measurement → Page views | ON |
| Data stream (Web) | Enhanced Measurement → Scrolls | ON |
| Data stream (Web) | Enhanced Measurement → Outbound clicks | ON |
| Data stream (Web) | Enhanced Measurement → Site search | ON (configure query param) |
| Data stream (Web) | Enhanced Measurement → Video engagement | ON if YouTube embeds |
| Data stream (Web) | Enhanced Measurement → File downloads | ON |
| Data stream (Web) | Enhanced Measurement → Form interactions | ON |
| Data stream (Web) | Unwanted referrals | At minimum: user's own checkout domains, Stripe, PayPal, Apple Pay |
| Data stream (Web) | Cross-domain measurement | ON if >1 domain |
| Links | Google Ads link | Present + ads personalization ON (if running Google Ads) |
| Links | BigQuery link | Recommended but not required |
| Links | Search Console link | Optional |

---

## 2. Enhanced Measurement reference

Enhanced Measurement gives you eight auto-tracked events without any GTM work:

| Event | Fires when | Params |
|---|---|---|
| `page_view` | Page loads (if GA4 Config `sendPageView=true`) | `page_location`, `page_title`, `page_referrer` |
| `scroll` | User scrolls to 90% of the page | `percent_scrolled` |
| `click` | User clicks a link pointing outside the current domain | `link_classes`, `link_domain`, `link_url`, `outbound` |
| `view_search_results` | URL contains a query param that matches `search`, `q`, `query`, `keyword`, `term` | `search_term` |
| `video_start` / `video_progress` / `video_complete` | Embedded YouTube video events | `video_current_time`, `video_duration`, `video_percent`, `video_provider`, `video_title`, `video_url` |
| `file_download` | User clicks a link ending in `.pdf`, `.docx`, `.xlsx`, `.zip`, etc. | `file_extension`, `file_name`, `link_classes`, `link_domain`, `link_url` |
| `form_start` | User first interacts with any form field | `form_id`, `form_name`, `form_destination` |
| `form_submit` | Native form submit | `form_id`, `form_name`, `form_destination` |

**Rule:** don't duplicate these in the dataLayer unless you need to add custom params.

---

## 3. Unwanted referrals (recommended defaults)

Every GA4 property running a checkout flow should exclude at least these from Unwanted Referrals:

- `checkout.stripe.com`
- `pay.google.com`
- `www.paypal.com`
- `www.paypalobjects.com`
- `apple.com`
- `checkoutshopper-live.adyen.com`
- `www.afterpay.com`
- `zip.co` / `www.zip.co`
- `www.humm.com.au`
- User's own staging / preview domains (e.g. `staging.mysite.com.au`)

Without these, GA4 will attribute any purchase that passed through Stripe/PayPal Redirect flow to the payment gateway as the source, destroying attribution.

---

## 4. Data retention

GA4 defaults to 2 months of event-level retention, which means you lose user-level detail after 2 months. Always max out:

- **GA4 standard:** 14 months
- **GA4 360:** 50 months

UI path: Admin → Data collection and modification → Data retention → `Event data retention` → change to 14/50 months → Save.

Note: Data retention is NOT yet writable via the Admin API in v1beta. `ga4-setup` produces a manual instruction for this in its change log.

---

## 5. GA4 industry categories (enum values)

Pass to `create_property` or use as a reference when diagnosing wrong categories. Selected subset:

- `AUTOMOTIVE`
- `BUSINESS_INDUSTRIAL_MARKETS`
- `FINANCE`
- `HEALTHCARE`
- `TECHNOLOGY`
- `TRAVEL`
- `OTHER`
- `ARTS_ENTERTAINMENT`
- `HOME_GARDEN`
- `INTERNET_TELECOM`
- `LAW_GOVERNMENT`
- `NEWS`
- `ONLINE_COMMUNITIES`
- `PEOPLE_SOCIETY`
- `PETS_ANIMALS`
- `REAL_ESTATE`
- `REFERENCE`
- `SCIENCE`
- `SPORTS`
- `JOBS_EDUCATION`
- `SHOPPING`
- `BEAUTY_FITNESS`
- `FOOD_DRINK`
- `GAMES`
- `HOBBIES_LEISURE`
- `BOOKS_LITERATURE`

`SHOPPING` + `HOME_GARDEN` are typical for AU homewares. `FINANCE` for fintech. `ONLINE_COMMUNITIES` for forum/community sites.

---

## 6. Google Ads linking (when to create)

Create a Google Ads link when all of:

1. The user runs paid Google Ads campaigns.
2. The GA4 account has Editor permission on the property.
3. The Google account running `oauth-setup` has Admin on the Google Ads customer account.

Benefits:

- GA4 becomes a source of audiences in Google Ads.
- Google Ads spend + performance appears in GA4 acquisition reports.
- GA4 conversions (marked in `ga4-events`) can be imported to Google Ads as conversion actions.
- Enables cross-device attribution via Google signals (if enabled).

---

## 7. Common audit findings

| Finding | Severity | Fix |
|---|---|---|
| Data retention = 2 months | high | Change to 14 months |
| Enhanced Measurement off | medium | Turn on |
| No unwanted referrals | high (if e-commerce) | Add payment gateway domains |
| No Google Ads link (but running Google Ads) | high | Create via MCP or admin UI |
| Timezone mismatch between site and property | low | Change to site's timezone |
| Multiple conflicting web streams | medium | Consolidate or ask user which is canonical |
| `currency_code` mismatch | medium | Change to correct currency; any historical data stays in the old currency |
| No conversion events marked | medium | Run `/ppc-manager:ga4-events` |
| `industry_category` = `OTHER` | low | Set to correct category |
