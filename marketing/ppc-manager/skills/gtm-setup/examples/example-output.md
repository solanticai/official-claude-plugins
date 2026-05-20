# GTM Setup — Change Log — Koala & Co. Online

**Container:** GTM-KOALA123 (container_id `1234567890`)
**Account:** Koala & Co. (account_id `4444333322`)
**Workspace:** Default Workspace
**Version:** GTM baseline setup - 2026-04-11 (version_id `42`) — **Published**
**Date:** 11/04/2026

---

## Summary

Koala & Co. Online is an Australian homewares retailer whose GTM container had accumulated two years of ad-hoc tagging. We audited the container, deleted four legacy Universal Analytics tags, renamed twelve tags to the standard convention, and installed the GA4 baseline (one Config tag on All Pages + Consent Mode v2 default-deny stub). The container now has a clean foundation for the upcoming `gtm-datalayer` and `ga4-events` work.

---

## Baseline status

| Item | Before | After |
|---|---|---|
| GA4 Configuration tag | 0 (was UA) | 1 (Con - GA4 - Config) |
| All Pages trigger | Built-in, unused | Built-in, attached to GA4 Config |
| Consent Mode v2 stub | None | `Util - HTML - Consent Mode Init` (priority 100) |
| Legacy UA tags | 4 | 0 |
| Naming convention compliance | 42% | 100% |

---

## Changes applied

### Variables created

| Name | Type | Parameter |
|---|---|---|
| CONST - GA4 Measurement ID | Constant | `G-KOALAHOMES1` |
| DL - event | Data Layer Variable | `event` |
| DL - ecommerce.value | Data Layer Variable | `ecommerce.value` |
| DL - ecommerce.currency | Data Layer Variable | `ecommerce.currency` |

### Triggers created

| Name | Type | Filter |
|---|---|---|
| All Pages - Page View | pageview | (built-in, no filter) |
| Custom Event - purchase | customEvent | `event` equals `purchase` |

### Tags created

| Name | Type | Firing trigger |
|---|---|---|
| Con - GA4 - Config | gaawc (GA4 Configuration) | All Pages - Page View |
| Util - HTML - Consent Mode Init | html (Custom HTML) | All Pages - Page View (priority 100) |

### Tags renamed

| Old name | New name |
|---|---|
| GA Tag | Con - GA4 - Config (also re-typed from `ua` to `gaawc`) |
| Purchase Tracking | Con - GA4 - Event - purchase |
| FB Pixel | Con - Meta - Pixel Base |
| Google Ads Conv | Con - Google Ads - Purchase |
| (+8 more renames) | |

### Tags deleted

| Name | Reason |
|---|---|
| UA - All Pages | Legacy Universal Analytics (sunsetted 2023) |
| UA - Event Tracking | Legacy Universal Analytics |
| UA - Ecommerce | Legacy Universal Analytics |
| UA - Goals | Legacy Universal Analytics |

---

## Preview & verification

- **Tag Assistant preview URL:** `https://tagassistant.google.com/?container_id=GTM-KOALA123&version_id=42`
- **Verification steps:**
  1. Open the preview URL in Chrome.
  2. Visit `https://koalahomewares.com.au/` in the preview session.
  3. Confirm `Con - GA4 - Config` fires on Page View.
  4. Open GA4 DebugView (under Admin → DebugView) and confirm one `page_view` event appears from `debug_mode = true`.
  5. Confirm `Util - HTML - Consent Mode Init` fires before the GA4 Config (priority 100 vs default 0).

---

## Recommended next steps

1. Run `/ppc-manager:gtm-datalayer` to design the e-commerce dataLayer schema (Koala pushes `add_to_cart`, `begin_checkout`, `purchase` from a Shopify storefront — the existing snippets need rationalising).
2. Run `/ppc-manager:ga4-events` to create the `purchase` conversion event and custom dimensions for `item_category` and `promo_code`.
3. Run `/ppc-manager:meta-pixel-setup` to wire the Meta pixel with the same events (CAPI is already in place via a Shopify plugin — the skill will audit dedup).
