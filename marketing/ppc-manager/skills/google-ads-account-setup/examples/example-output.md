# Google Ads Account Setup — Koala & Co. AU

**Customer ID:** 1234567890
**Currency:** AUD
**Time zone:** Australia/Sydney
**Test account:** false
**Date:** 11/04/2026

---

## Audit findings

| Area | Current | Desired | Severity |
|---|---|---|---|
| Auto-tagging | ON | ON | ok |
| Currency | AUD | AUD | ok |
| Time zone | Australia/Sydney | Australia/Sydney | ok |
| GA4 link | none | linked to 789012345 | **high** |
| Merchant Center link | none | linked (has Shopify feed) | **high** |
| Conversion actions | 2 manual (Purchase, AddToCart) | GA4-imported Purchase | **high** (duplicate) |
| Auto-apply recommendations | ON | OFF | medium |
| Negative keyword lists | 0 | 1 (Shared brand negatives) | low |

---

## Conversion actions

| Name | Category | Primary? | Attribution | Source | Status |
|---|---|---|---|---|---|
| Purchase (manual tag) | Purchase | yes | Last click | Google Ads tag | **flagged for removal** |
| AddToCart (manual tag) | Add to cart | no | Last click | Google Ads tag | **flagged for removal** |
| GA4 - purchase | Purchase | yes | Data-driven | GA4 import | **NEW, recommended** |

---

## Linked accounts

| Link type | Target | Status |
|---|---|---|
| GA4 | properties/789012345 | to be linked |
| Merchant Center | (Shopify feed) | to be linked |
| YouTube channel | — | N/A (no video) |

---

## Fix plan

### Automatable fixes applied via MCP

- None in v1.0 — account linking + conversion deletion are manual-only.

### Manual fixes

1. **Link GA4:** Tools → Linked accounts → Google Analytics (GA4) → Link `properties/789012345` → enable Personalized advertising.
2. **Import GA4 conversions:** Tools → Measurement → Conversions → New conversion action → Import → GA4 properties → Web → pick `purchase` → Create.
3. **Disable old manual conversions:** Conversions → pick `Purchase (manual tag)` → Edit → Status = Removed. Repeat for `AddToCart (manual tag)`.
4. **Link Merchant Center:** Tools → Linked accounts → Google Merchant Center → Link (opens a Shopify-connected MC account).
5. **Disable auto-apply recommendations:** Recommendations → Auto-apply → Untick every category → Save.
6. **Create a shared negative keyword list:** Tools → Shared library → Negative keyword lists → Create "Brand negatives" with `competitor name`, `cheap`, `free`.

### Wait for data

- Attribution model change to Data-driven — already set by the GA4 import, will activate once 300+ conversions accumulate (~30 days at current rate).
- Smart Bidding migration — current conversion volume is ~200/month, not enough for tCPA/tROAS yet. Revisit in 60 days.

---

## Next steps

1. Complete the 6 manual fixes above. Timebox ~25 minutes.
2. Run `/ppc-manager:keyword-research` to build the keyword list for the first Search campaign.
3. Run `/ppc-manager:google-search-campaign` to launch the campaign in PAUSED state.
4. Review and enable once the Search campaign structure is approved.
5. In 7 days, run `/ppc-manager:campaign-audit` to verify conversions are attributing correctly.
