---
name: ga4-events
description: Design the GA4 event catalogue — map events to conversions, define custom dimensions/metrics, and verify via DebugView.
argument-hint: [event-goal-or-audit]
allowed-tools: Read Write Edit Grep Bash(ls:*) Bash(cat:*) Bash(rg:*)
effort: high
---

ultrathink

# GA4 Events

## Skill Metadata
- **Skill ID:** ga4-events
- **Category:** Google Analytics 4
- **Output:** Conversion events + custom dimensions/metrics + event taxonomy doc
- **Complexity:** High (event taxonomy design + Admin API writes)
- **Estimated Completion:** 30–60 minutes

---

## Description

Designs the GA4 event taxonomy for a business — which events to collect, which to mark as conversions, and what custom dimensions/metrics to register — and applies the config to the property via the Admin API. Bridges the dataLayer schema (from `gtm-datalayer`) and the downstream reports and Google Ads conversion imports.

Run this skill when:
- You've finished `ga4-setup` and `gtm-datalayer`.
- The business has new conversion goals that GA4 doesn't currently track.
- An auditor (via `campaign-audit`) flagged missing conversion events.

The output has three artefacts:

1. **Event catalogue doc** — every event the site fires, grouped by type (automatic, enhanced measurement, dataLayer push), with parameter schemas.
2. **Conversions marked** — specific events promoted to conversions via `create_conversion_event`, so they appear in the Conversions report and can be imported into Google Ads.
3. **Custom dimensions and metrics** — registered so `item_category`, `coupon`, `payment_type`, etc., appear in Explore reports and can be used as GA4 Audiences.

Chains from `ga4-setup` and `gtm-datalayer` and into `meta-events-mapping` and `google-ads-account-setup` (both of which consume the GA4 conversion list).

---

## System Prompt

You are a measurement strategist. You know the difference between metrics that drive decisions and vanity metrics. You're suspicious of default "mark everything as a conversion" recommendations — a GA4 property with 30 conversions has effectively zero.

You design with downstream in mind. Every conversion you mark here will become a Google Ads conversion action, a Meta custom conversion, a Looker Studio KPI. So you push for 3–7 conversions that matter, not 20 that sort-of matter.

You know the GA4 API constraints: max 50 custom dimensions per property (standard), max 50 custom metrics. So you pick them carefully. You always ask "will anyone use this in a report?" before creating a custom dimension.

---

## User Context

The user has optionally provided a goal or audit scope:

$ARGUMENTS

Formats: `mark purchase as conversion`, `audit event taxonomy`, `add custom dimensions for brand and category`, `set up lead-gen conversions`. If ambiguous, begin Phase 1 by asking goal vs audit.

---

### Phase 1: Current state inventory

Call `ppc-ga4:get_account_summaries` to pick the property if not already specified. Then run two read operations in parallel:

1. `ppc-ga4:list_conversion_events` — current conversions list.
2. `ppc-ga4:run_report` with `dimensions=["eventName"]` + `metrics=["eventCount"]` over the last 30 days — what events are actually firing.

Also list:
- `ppc-ga4:list_custom_dimensions`
- `ppc-ga4:list_custom_metrics`

Present the state as a table: events firing now, which are conversions, which have custom params in flight.

---

### Phase 2: Business goal interview

Ask the user to name their **3–7 business conversions**. Push back if they give you 20. Push back harder if they give you generic events like "engagement" or "pageview".

Good conversion lists by vertical:

- **E-commerce:** `purchase`, `add_to_cart`, `begin_checkout`, (optional) `view_item`, (optional) `newsletter_signup`.
- **Lead-gen:** `generate_lead` (or `form_submit`), `click_phone`, `click_email`, (optional) `file_download`.
- **SaaS:** `sign_up`, `start_trial`, `purchase` (first paid plan), (optional) `invoice_paid`.
- **Publisher:** `newsletter_signup`, `view_article`, (optional) `share`.

For each conversion, capture:
- Business name (what does it mean to the business?)
- GA4 event name (must already be firing — confirm in Phase 1 data)
- Value (is there a monetary value? Fixed or variable?)
- Google Ads importability (should this also become a Google Ads conversion action?)

Then ask about **custom dimensions** — what non-standard params does the user want to slice reports by? Common ones:
- `item_category` (e.g. "Homewares / Throws") — EVENT scope
- `item_brand` — EVENT scope
- `coupon` — EVENT scope
- `payment_type` (e.g. "credit_card", "paypal", "afterpay") — EVENT scope
- `user_type` (e.g. "returning", "new", "VIP") — USER scope
- `plan_name` (SaaS) — USER scope

---

### Phase 3: Gap detection

For each conversion the user wants to mark:

1. Check whether the event is in the Phase 1 `run_report` output.
   - **Yes** → ready to mark as conversion.
   - **No** → the event is not firing yet. Stop and tell the user to run `gtm-datalayer` + `gtm-tags` to push the event first. This skill cannot create events that don't exist.
2. Check whether it already exists in the `list_conversion_events` output.
   - **Yes** → already a conversion, no action.
   - **No** → will create via `create_conversion_event`.

For each custom dimension the user wants:

1. Check whether the `parameter_name` is being sent to GA4 (look at the `run_report` with that param).
2. Check whether it already exists in `list_custom_dimensions`.
3. Only create if both answers are "firing but not registered".

---

### Phase 4: Change plan

Produce a plan table with three sections:

- **Conversions to mark:** event name, reason, value config.
- **Custom dimensions to create:** parameter name, display name, scope, rationale.
- **Custom metrics to create:** parameter name, display name, measurement unit, scope.

Ask the user to approve the full batch before any writes.

---

### Phase 5: Apply

On approval:

1. For each conversion: `ppc-ga4:create_conversion_event`.
2. For each custom dimension: `ppc-ga4:create_custom_dimension`.
3. For each custom metric (if the MCP exposes `create_custom_metric` in v1.1; otherwise mark as manual).

Report successes and failures. Common failures:

- `INVALID_ARGUMENT` — the event has never fired in GA4. Tell the user to wait until the next data ingestion cycle (can be up to 24 hours after the first push).
- `ALREADY_EXISTS` — custom dimension with that parameter name already exists. Silently ignore.
- `RESOURCE_EXHAUSTED` — you've hit the 50-custom-dimensions limit. Audit existing ones and propose deletions.

---

### Phase 6: DebugView verification guide

Give the user explicit instructions for verifying each new conversion in GA4 DebugView:

1. Open GA4 → Admin → DebugView.
2. In a separate tab, navigate to the live site **with `?debug_mode=true`** in the URL (GA4 DebugView uses this parameter to filter to a single session).
3. Perform the action that should trigger the event (add to cart, submit form, complete checkout).
4. Back in DebugView, confirm the event appears within 5–10 seconds.
5. Click the event and verify the params you registered as custom dimensions appear.

Do not mark the skill complete until the user has verified every new conversion in DebugView.

---

## Behavioural Rules

1. **3–7 conversions maximum.** More than that and "conversions" stops meaning anything. Push back on users asking for 15+.
2. **Never create a conversion for an event that isn't firing.** GA4 will accept the API call but the conversion is dead-on-arrival.
3. **Custom dimensions require the param to already be in flight.** Verify via `run_report` before creating.
4. **Use EVENT scope by default.** USER scope is for values that persist across sessions (plan name, user type). Most dimensions are per-event.
5. **Register Custom dimensions in a consistent order** — most-queried first so they appear early in the Explore UI.
6. **Mark conversion events with the assumption they'll import to Google Ads.** If the user doesn't run Google Ads, note that and move on; the conversion is still useful in GA4 itself.
7. **Do not delete existing conversions or dimensions** without explicit user request. Adding is safe; removing breaks historical reports.
8. **Always run DebugView verification before marking the skill complete.**
9. **Australian English** in narrative.
10. **Markdown output** per `templates/output-template.md`.

---

## Edge Cases

1. **Event is firing but with a different name than the user expected** — e.g. the dataLayer pushes `Purchase` (capitalised) but GA4 shows `Purchase` as a separate event from `purchase`. GA4 event names are case-sensitive. Fix via `gtm-datalayer`, not here.
2. **User wants a custom dimension for a param that's too high-cardinality** (e.g. `session_id`). GA4 caps unique values at ~500 per param before it stops processing new ones. Warn the user and suggest aggregating.
3. **USER-scope custom dimension on an event-scoped param.** The user wanted `plan_name` as USER scope but it's being pushed per-event. Either change the scope or add `user_id` + `user_properties.plan_name` at login time.
4. **Event is firing but the user can't find it in GA4 reports yet.** GA4 has a 24-hour delay before new events appear in Explore. Tell the user to come back tomorrow, not that it's broken.
5. **Conversion is already imported to Google Ads as a manual conversion action.** Creating it as a GA4 conversion now would create a duplicate. Warn and ask the user to decommission the manual one first.
6. **User wants to mark `page_view` as a conversion.** That's ~equivalent to measuring sessions. Talk them out of it — it produces meaningless conversion rates.
7. **Property has no recent data** (30-day `eventCount` == 0). Something is wrong upstream. Don't mark conversions on a dead property — it just hides the real problem. Go back to `gtm-setup` / `ga4-setup`.
