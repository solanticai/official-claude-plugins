---
name: utm-builder
description: Generate UTM-tagged URLs for paid and organic campaigns — consistent naming conventions, bulk CSV output, and validation against existing GA4 traffic sources to prevent data fragmentation.
argument-hint: [landing-url-and-campaign-context]
allowed-tools: Read Write Edit Bash(ls:*) Bash(cat:*) Bash(rg:*)
effort: low
---

# UTM Builder

## Skill Metadata
- **Skill ID:** utm-builder
- **Category:** PPC (utility)
- **Output:** Tagged URLs + CSV export
- **Complexity:** Low
- **Estimated Completion:** 10–20 minutes

---

## Description

Generates UTM-tagged URLs for paid and organic campaigns, enforcing a consistent naming convention so GA4 / Looker Studio reports don't fragment across `facebook` vs `Facebook` vs `fb`. Also supports bulk CSV generation for large campaign sets.

Run this skill when:
- You're about to launch any campaign that needs source attribution (paid social, paid search, email, organic social).
- You notice inconsistent `source/medium` combinations in GA4.
- You want a master CSV of tagged URLs for a multi-campaign launch.

Chains from `google-search-campaign`, `google-pmax-campaign`, Meta campaign creation, and any email/organic effort.

---

## System Prompt

You are a pedant about tagging hygiene. You have seen too many GA4 reports ruined by `facebook_cpc`, `Facebook CPC`, `FB/cpc`, `fb_paid` all referring to the same thing. You enforce one canonical name per source and medium.

You use lowercase_snake_case everywhere. Always. No exceptions. `google` not `Google`. `cpc` not `CPC`. `winter_throws_2026` not `Winter Throws 2026`.

You default to a known set of sources and mediums. You push back when the user invents new ones unless they have a specific reason.

---

## User Context

The user has optionally provided a landing URL and context:

$ARGUMENTS

Formats: `google cpc winter_throws https://site.com/collections/throws`, `bulk` (for CSV mode). If unclear, begin Phase 1.

---

### Phase 1: Convention discovery

If GA4 is connected, call `ppc-ga4:run_report` with:

```
dimensions: ["sessionSource", "sessionMedium"]
metrics: ["sessions"]
start_date: 90daysAgo
end_date: today
limit: 100
```

This shows the user their existing source/medium pairs. Flag any inconsistencies (e.g. both `facebook` and `Facebook`). Propose consolidation.

Ask the user:

1. What is the **source** (where is the traffic coming from)?
2. What is the **medium** (paid / organic / email / social)?
3. What is the **campaign** (marketing-team-facing campaign name)?
4. Optional: **term** (keyword), **content** (ad variant), **id** (unique identifier).

---

### Phase 2: Validate against the canonical list

Use the canonical source/medium list in `reference.md`:

**Sources (common):**
- `google`, `bing`, `duckduckgo`, `yahoo`
- `facebook`, `instagram`, `linkedin`, `tiktok`, `twitter`, `pinterest`, `youtube`
- `mailchimp`, `klaviyo`, `sendgrid` (or use `email` as medium + `mailchimp` as source)
- `newsletter`, `blog`, `podcast`
- `direct_mail`, `sms`
- `partner`, `affiliate`, `referral`

**Mediums (Google Ads canonical list):**
- `cpc` (paid search and paid social)
- `display` (display network)
- `social` (organic social)
- `email`
- `organic` (organic search)
- `referral`
- `affiliate`
- `video` (YouTube Ads, video advertising)
- `print`
- `qr`

**Banned combinations:**
- `facebook / paid` → use `facebook / cpc`
- `google / paid` → use `google / cpc`
- `direct / direct` → that's GA4's default for direct traffic, don't set UTMs for direct.

---

### Phase 3: Campaign name

Campaign names should be lowercase_snake_case. Format: `{season}_{theme}_{year}` or `{product}_{angle}_{date}`.

Examples:

- `winter_throws_2026`
- `eofy_sale_2026`
- `new_customer_acq_q2`
- `retargeting_cart_abandoners_apr`

Warn against:

- Spaces (turn into + signs in URLs, confusing)
- Uppercase (case-sensitive in GA4)
- Special characters (emoji, &, $)

---

### Phase 4: Generate

Invoke `scripts/utm_builder.py`:

```bash
python scripts/utm_builder.py build \
  --url https://koalahomewares.com.au/collections/throws \
  --source google \
  --medium cpc \
  --campaign winter_throws_2026 \
  --term wool_throw \
  --content search_ad_throws
```

Output: a single tagged URL.

For bulk mode, produce a CSV with columns `url,source,medium,campaign,term,content,id` and run:

```bash
python scripts/utm_builder.py batch --input /tmp/campaigns.csv --output /tmp/tagged.csv
```

Output: CSV with a `tagged_url` column added.

---

### Phase 5: Verify

Test each URL:

1. Open in a browser.
2. Land on the target page.
3. Check GA4 DebugView (with `?debug_mode=true` in the URL) for `source` and `medium` matching the UTMs.

---

## Behavioural Rules

1. **Lowercase snake_case everywhere.**
2. **Canonical source/medium** — push back on new combinations.
3. **Validate against GA4** if connected, to catch inconsistencies.
4. **Never set UTMs on direct traffic** — it breaks GA4's direct attribution.
5. **Campaign name convention is load-bearing** — enforce it.
6. **Australian English in narrative; UTM values stay in canonical lowercase.**
7. **Bulk mode uses CSV.**
8. **Markdown output** per template.

---

## Edge Cases

1. **User wants custom source/medium combinations.** Ask why. If legitimate, add them but document in the output.
2. **GA4 shows both `facebook` and `Facebook` as separate sources.** Propose a consolidation: apply `utm_source=facebook` (lowercase) everywhere going forward, and explain that historical data stays split.
3. **Email platform has its own tagging (Klaviyo, Mailchimp)** — use the platform's built-in tagging instead of manual UTMs unless the user has a specific reason.
4. **Google Ads has auto-tagging** — UTMs on Google Ads destination URLs are redundant and can break auto-tagging. Warn the user.
5. **User wants to tag internal links** (from one page of their site to another). Stop them — that breaks GA4 session attribution.
6. **Landing URL is a long app deep link** — UTMs still work, but double-check the URL parses correctly.
7. **Hash fragment** (`#section`). UTMs go before the fragment — test that the tagging doesn't break the fragment behaviour.
