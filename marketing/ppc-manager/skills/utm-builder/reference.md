# UTM Builder — Reference

## 1. UTM parameter reference

| Parameter | Purpose | Example |
|---|---|---|
| `utm_source` | Where the traffic came from | `google`, `facebook`, `newsletter` |
| `utm_medium` | Marketing medium | `cpc`, `social`, `email`, `referral` |
| `utm_campaign` | Campaign name | `winter_throws_2026` |
| `utm_term` | Paid search keyword (optional) | `wool_throw` |
| `utm_content` | Ad variant / link position (optional) | `search_ad_a`, `footer_link` |
| `utm_id` | Unique identifier (optional) | `ad_98765` |

## 2. Canonical source names

### Search engines
- `google`
- `bing`
- `duckduckgo`
- `yahoo`

### Social platforms
- `facebook`
- `instagram`
- `linkedin`
- `tiktok`
- `twitter`
- `pinterest`
- `youtube`
- `reddit`
- `snapchat`

### Email platforms
- `mailchimp`
- `klaviyo`
- `sendgrid`
- `campaign_monitor`
- `hubspot_email`

### Other
- `newsletter`
- `blog`
- `podcast`
- `partner`
- `affiliate`
- `direct_mail`
- `sms`
- `print`

## 3. Canonical medium names

| Medium | Use for |
|---|---|
| `cpc` | Paid search + paid social (default for any `?click` context) |
| `display` | Display ads only |
| `social` | Organic social posts |
| `email` | Any email traffic |
| `organic` | Organic search (don't set this manually — GA4 does) |
| `referral` | Partner / referring site traffic |
| `affiliate` | Affiliate links |
| `video` | Video ads (YouTube Ads, etc.) |
| `print` | Print media QR codes |
| `qr` | General QR code |

## 4. Banned combinations

| Source | Medium | Reason |
|---|---|---|
| `(direct)` | `(none)` | GA4's default for direct traffic — don't override |
| `facebook` | `paid` | Use `cpc` not `paid` |
| `google` | `paid` | Use `cpc` |
| `social` | `social` | Redundant, confusing |
| `email` | `newsletter` | Redundant — `email` is the medium, `newsletter` is the source |
| ALL CAPS | anything | Case-sensitive in GA4 — always lowercase |

## 5. Campaign name convention

Format: `{topic}_{year}` or `{topic}_{month_year}` or `{season}_{topic}_{year}`

### Examples
- `winter_throws_2026`
- `may_sale_2026`
- `q2_new_customer_2026`
- `eofy_clearance_2026`
- `black_friday_2026`
- `retargeting_cart_abandoners_apr`

### Anti-patterns
- `Winter Throws 2026` (spaces, uppercase)
- `winter-throws-2026` (hyphens — allowed but inconsistent with the snake_case convention)
- `q2-2026` (no topic, too generic)
- `2026` (too generic)

## 6. Auto-tagging vs manual UTMs

| Platform | Recommendation |
|---|---|
| Google Ads | Auto-tagging (GCLID). Do NOT add UTMs to destination URLs. |
| Microsoft Ads | Auto-tagging (UCID). Same. |
| Meta Ads | Auto-tagging exists but limited. Add UTMs manually for safety. |
| LinkedIn Ads | Auto-tagging via LinkedIn Insight. Supplement with UTMs. |
| TikTok Ads | Manual UTMs required. |
| Email (Klaviyo/Mailchimp) | Built-in UTMs; configure once at the platform level. |
| SMS | Manual UTMs. |
| QR codes | Manual UTMs (they're just links). |

## 7. GA4 source/medium behaviour

GA4 builds `sessionDefaultChannelGrouping` (the "channel" dimension in reports) automatically from your `utm_source` + `utm_medium` combinations. Examples:

- `source=google, medium=cpc` → Channel: `Paid Search`
- `source=facebook, medium=cpc` → Channel: `Paid Social`
- `source=google, medium=organic` → Channel: `Organic Search`
- `source=facebook, medium=social` → Channel: `Organic Social`
- `source=mailchimp, medium=email` → Channel: `Email`
- `source=newsletter, medium=referral` → Channel: `Referral`

If your UTMs don't map, GA4 assigns `Unassigned` — a red flag.
