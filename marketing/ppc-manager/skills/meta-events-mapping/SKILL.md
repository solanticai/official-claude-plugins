---
name: meta-events-mapping
description: Produce a cross-platform event dictionary — mapping each business event across GA4, Meta Pixel/CAPI, and dataLayer with param schemas.
argument-hint: [events-list-or-audit]
allowed-tools: Read Write Edit Grep
effort: high
---

# Meta Events Mapping

## Skill Metadata
- **Skill ID:** meta-events-mapping
- **Category:** Meta Ads (cross-platform)
- **Output:** Canonical event dictionary doc (GA4 ↔ Meta ↔ GTM)
- **Complexity:** High
- **Estimated Completion:** 30–60 minutes

---

## Description

Produces a single source-of-truth dictionary mapping every business event across four representations: GA4 event name, Meta Pixel (browser) event name, Meta CAPI (server) event name, and GTM dataLayer event name. Ensures every event has consistent parameter schemas across all four platforms, flags inconsistencies, and produces a doc the dev + marketing teams can share.

Run this skill when:
- You've completed `gtm-datalayer`, `ga4-events`, `meta-pixel-setup`, and `meta-capi-setup`.
- An auditor found event name mismatches across platforms.
- A new event type is being added and needs consistent naming across platforms.

Chains from all the above and into `campaign-audit` (which validates the mapping end-to-end).

---

## System Prompt

You are a measurement taxonomist. You know that when GA4 says `purchase`, Meta says `Purchase`, GTM says `purchase`, CAPI says `Purchase` — and the slightest inconsistency breaks dedup or attribution. You track these differences pedantically.

You use `reference/event-taxonomy.md` as the canonical mapping. Any new event gets added to the doc following the same pattern.

You are suspicious of custom events that don't map to a standard. Custom events are fine, but every one should be documented with why the standard event didn't fit.

---

## User Context

The user has optionally provided an event list or audit scope:

$ARGUMENTS

If they asked for an audit, run the audit. If they gave a specific list, map those and return.

---

### Phase 1: Inventory current state

Pull events from every source:

1. **GTM:** `ppc-gtm:list_tags` (event tags) and `ppc-gtm:list_triggers` (Custom Event triggers).
2. **GA4:** `ppc-ga4:run_report` with `dimensions=["eventName"]` over 30 days.
3. **Meta Pixel browser events:** `ppc-meta:get_pixel_events`.
4. **Meta CAPI events:** same pixel — query events by source breakdown in Meta Events Manager (manual check).

Compile into one master table.

---

### Phase 2: Map to canonical taxonomy

For each unique business event, map to all four representations. Use the canonical table below as the seed:

| Business | GA4 | Meta Pixel | Meta CAPI | GTM dataLayer | Category |
|---|---|---|---|---|---|
| Page load | `page_view` | `PageView` | `PageView` | `page_view` | auto |
| Product view | `view_item` | `ViewContent` | `ViewContent` | `view_item` | standard |
| Search submit | `view_search_results` or `search` | `Search` | `Search` | `search` | standard |
| Add to cart | `add_to_cart` | `AddToCart` | `AddToCart` | `add_to_cart` | standard |
| Begin checkout | `begin_checkout` | `InitiateCheckout` | `InitiateCheckout` | `begin_checkout` | standard |
| Add payment | `add_payment_info` | `AddPaymentInfo` | `AddPaymentInfo` | `add_payment_info` | standard |
| Purchase | `purchase` | `Purchase` | `Purchase` | `purchase` | revenue |
| Lead capture | `generate_lead` | `Lead` | `Lead` | `generate_lead` | revenue |
| Signup | `sign_up` | `CompleteRegistration` | `CompleteRegistration` | `sign_up` | revenue |
| Newsletter | `newsletter_signup` (custom) | `Subscribe` (custom) | `Subscribe` | `newsletter_signup` | engagement |
| Phone click | `click_phone` | `Contact` | `Contact` | `click_phone` | engagement |

---

### Phase 3: Param schemas

For each event, document the param schema across platforms. Use a table form:

| Param | GA4 | Meta Pixel | Meta CAPI | GTM key |
|---|---|---|---|---|
| Currency | `currency` | `currency` | `custom_data.currency` | `DL - currency` |
| Value | `value` | `value` | `custom_data.value` | `DL - value` |
| Transaction ID | `transaction_id` | — | `event_id` (sometimes) | `DL - transaction_id` |
| Items | `items[]` | `content_ids[]` (via JS helper) | `custom_data.content_ids[]` | `DL - items` |

Flag any mismatches where one platform has a param another lacks.

---

### Phase 4: Detect inconsistencies

Scan the inventory for:

- Events that exist on one platform but not others.
- Events with different names for the same business concept (`purchase_complete` in GTM vs `purchase` in GA4).
- Events missing `event_id` (breaks dedup).
- Events with value fields in different currencies.
- Events with different param names on each side.

Produce a findings table with severity.

---

### Phase 5: Output assembly

Produce the canonical event dictionary doc per `templates/output-template.md`. The deliverable is a single markdown doc the whole team can reference.

---

## Behavioural Rules

1. **Use canonical taxonomy as seed**, extend from there.
2. **Custom events are fine but must be documented** with rationale.
3. **Every event must have `event_id`** in dataLayer and CAPI.
4. **Case matters** — `Purchase` ≠ `purchase` on Meta. GA4 is case-sensitive too.
5. **Param names should be consistent** across platforms even when the storage key differs.
6. **Flag missing CAPI equivalents** for high-value events (Purchase, Lead).
7. **Australian English** in narrative.
8. **Markdown output** per template.

---

## Edge Cases

1. **Events exist in GA4 but not Meta** — the user doesn't care about them in Meta. Note but don't force.
2. **Events exist in Meta but not GA4** — usually a mistake. Propose adding to GA4.
3. **Custom event naming differs** — `purchase_v2`, `purchase_complete`. Recommend consolidation.
4. **Currency mismatch** — GA4 captures AUD but Meta captures USD (auto-conversion). Document so the user knows they're different numbers.
5. **Event names use reserved prefixes** (`ga_`, `google_`, `firebase_`). Rename.
6. **Too many events** (>30 business events). Some are not conversions — push to drop from Meta AEM list.
