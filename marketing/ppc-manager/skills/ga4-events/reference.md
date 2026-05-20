# GA4 Events — Reference

---

## 1. GA4 recommended conversion events by vertical

| Vertical | Primary conversion | Secondary | Micro |
|---|---|---|---|
| E-commerce | `purchase` | `begin_checkout`, `add_to_cart` | `view_item`, `view_item_list` |
| Lead-gen (service) | `generate_lead` | `form_submit`, `click_phone` | `click_email`, `file_download` |
| SaaS freemium | `sign_up` | `start_trial`, `purchase` | `activate_plan` |
| SaaS paid | `purchase` | `start_trial` | `sign_up` |
| Publisher / content | `newsletter_signup` | `view_article`, `share` | `scroll_depth_90` |
| App (hybrid web + mobile) | `first_open`, `purchase` | `in_app_purchase` | `tutorial_complete` |

**Rule:** pick one primary (what the business exists to make happen), one to three secondaries (steps preceding the primary), and treat "micro" events as informative but non-conversion.

---

## 2. GA4 reserved event and parameter names (do not override)

These are reserved by GA4 itself and cannot be used for custom events or custom parameters:

**Events:**
- `ad_activeview`, `ad_click`, `ad_exposure`, `ad_impression`, `ad_query`, `adunit_exposure`
- `app_clear_data`, `app_exception`, `app_install`, `app_remove`, `app_update`
- `error`, `first_open`, `first_visit`, `in_app_purchase`
- `notification_*`, `os_update`, `screen_view`, `session_start`, `user_engagement`

**Parameter names:**
- `first_open_time`, `first_visit_time`, `last_deep_link_referrer`
- `user_id`, `user_pseudo_id` (GA4 assigns these; you can set but not rename)
- `ga_session_id`, `ga_session_number`, `engagement_time_msec`
- Anything starting with `_`

---

## 3. Custom dimension scope decision

| Question | USER scope | EVENT scope |
|---|---|---|
| Does the value persist across sessions? | yes | no |
| Does the same value apply to every event from this user? | yes | no |
| Example: user's subscription plan | ✓ | |
| Example: item category on a purchase | | ✓ |
| Example: coupon used at checkout | | ✓ |
| Example: logged-in status | ✓ | |
| Example: traffic source | | ✓ |

---

## 4. Custom dimension limits (GA4 standard)

- **50 custom dimensions per property** (shared across EVENT and USER scopes).
- **50 custom metrics per property.**
- **500 unique values per custom dimension per day** — beyond this, "(other)" takes over.
- **40 characters per parameter name.**
- **100 characters per parameter value.**

Plan accordingly. Don't burn a custom dimension on `timestamp_ms`.

---

## 5. Custom dimension / metric worked examples

### Example 1 — E-commerce custom dimensions

| Parameter name | Display name | Scope | Rationale |
|---|---|---|---|
| `item_brand` | Item brand | EVENT | Already in Enhanced Ecommerce; register for reports |
| `item_category` | Item category | EVENT | Already in Enhanced Ecommerce; register |
| `coupon` | Coupon code | EVENT | Track promo effectiveness |
| `payment_type` | Payment type | EVENT | Split purchase by Stripe / PayPal / Afterpay |
| `shipping_tier` | Shipping tier | EVENT | Standard / Express / Same-day |

### Example 2 — SaaS custom dimensions

| Parameter name | Display name | Scope | Rationale |
|---|---|---|---|
| `plan_name` | Plan name | USER | Track by current plan |
| `plan_id` | Plan ID | USER | Stable identifier for joins |
| `signup_source` | Signup source | USER | Attribution for the user's entire lifetime |
| `team_size_bucket` | Team size bucket | USER | Segmenting by 1-5 / 6-20 / 20+ |

### Example 3 — E-commerce custom metrics

| Parameter name | Display name | Measurement unit | Scope | Rationale |
|---|---|---|---|---|
| `estimated_margin` | Estimated margin | CURRENCY | EVENT | Gross margin per order — populate from `purchase` event |
| `time_to_purchase` | Time to purchase | SECONDS | EVENT | First session → purchase duration |

---

## 6. DebugView setup

1. Enable Debug Mode on the current session by adding `?debug_mode=true` to the site URL, OR by installing the Chrome extension "Google Analytics Debugger".
2. Admin → DebugView.
3. All events from debug-mode sessions appear within seconds.
4. Events show the full parameter payload; custom dimensions you've registered show under the event detail.
5. Click any parameter to see the hashed user identifier, the page context, and the timeline.

**Common mistake:** the user thinks DebugView is broken because they don't see events. The cause is almost always (a) forgetting `?debug_mode=true`, or (b) their GTM container isn't published with the latest changes.

---

## 7. Google Ads conversion import (after marking GA4 conversions)

Once you've marked a GA4 event as a conversion, it can be imported into Google Ads:

1. Google Ads → Tools → Measurement → Conversions.
2. New conversion action → Import → Google Analytics 4 properties → Web.
3. Pick the GA4 account + property.
4. A list of conversions appears — tick the ones you want to import.
5. Each becomes a Google Ads conversion action. It inherits the GA4 event name and value configuration.
6. In Google Ads, you can set the conversion category (Purchase, Lead, Sign up, etc.) and attribution model.

Do not import `add_to_cart` or `view_item` as Google Ads conversions unless you have a specific reason — they're too top-of-funnel for most bidding strategies.
