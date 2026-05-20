# Google Ads Account Setup — Reference

---

## 1. Account baseline checklist

| Area | Setting | Desired |
|---|---|---|
| Account | Currency | Matches business (AUD for AU) |
| Account | Time zone | Australia/Sydney (AU) |
| Account | Auto-tagging | ON |
| Billing | Status | ACTIVE |
| Links | GA4 | Linked, ads_personalization_enabled |
| Links | Merchant Center | Linked if selling products |
| Links | YouTube channel | Linked if running video |
| Conversions | At least one Primary action | Yes |
| Conversions | Attribution model | Data-driven preferred |
| Recommendations | Auto-apply | OFF (default) |
| Account | Test account | Clearly labelled if true |

## 2. Conversion action categories

| Category | Use for |
|---|---|
| Purchase | Revenue events (GA4 `purchase`) |
| Add to cart | Add-to-cart (Secondary, not Primary) |
| Begin checkout | Checkout entry (Secondary) |
| Submit lead form | Lead submissions |
| Sign-up | Free account creation |
| Phone call lead | Click-to-call on mobile |
| Book appointment | Booking events |
| Request quote | Quote requests |
| Page view | Never (too vague) |

## 3. Attribution models (2026)

| Model | When to use |
|---|---|
| Data-driven | Default for accounts with >300 conversions/month. Google's ML picks credit per touchpoint. |
| Last click | Fallback for low-volume accounts. Conservative, simple. |
| First click | Almost never — overvalues top-of-funnel touches. |
| Linear | Deprecated — do not use. |
| Time decay | Deprecated — do not use. |
| Position-based | Deprecated — do not use. |

**Default for new accounts:** Data-driven (Google now uses it even for low-volume accounts, with reduced precision).

## 4. Bidding strategy decision tree

```
Do you have >30 conversions in last 30 days?
├── No → Manual CPC + Enhanced CPC
└── Yes
    ├── Goal = max revenue? → Maximize conversion value (with tROAS if ≥50 conversions)
    ├── Goal = max conversions? → Maximize conversions (with tCPA if ≥30 conversions)
    ├── Goal = max clicks (awareness)? → Maximize clicks
    └── Goal = specific ad position? → Manual CPC with bid adjustments
```

**Rule:** never set a tROAS target lower than the account's 30-day average ROAS. Gradual tightening works better than moonshots.

## 5. Merchant Center & YouTube linking

- **Merchant Center:** Tools → Linked accounts → Google Merchant Center → Link. Required for Shopping / PMax Retail.
- **YouTube channel:** Tools → Linked accounts → YouTube → Link. Required for YouTube action / view-through conversions.

## 6. Audit findings reference

| Finding | Severity | Fix |
|---|---|---|
| Auto-tagging OFF | critical | Admin → Account settings → Auto-tagging ON |
| No GA4 link (but GA4 exists) | high | Tools → Linked accounts → Google Analytics (GA4) → Link |
| Duplicate conversions (manual + GA4 import) | high | Remove manual, keep GA4 import |
| No Primary conversion | high | Mark at least one conversion as Primary |
| Attribution = Last click (on a high-volume account) | medium | Change to Data-driven |
| Auto-apply recommendations ON | medium | Recommendations → Settings → Turn off |
| Billing not set | critical | Billing → Summary → Complete billing |
| Currency mismatch | critical | Create new account in correct currency |
