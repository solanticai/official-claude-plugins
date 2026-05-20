# Doc Link Validator Report

**Date:** {{date_dd_mm_yyyy}}
**Root scanned:** {{path}}
**Total links checked:** {{n}}

---

## Summary

| Status | Count |
|--------|-------|
| Healthy (200) | {{n}} |
| Broken internal (404) | {{n}} |
| Broken external (404 / 410) | {{n}} |
| Suspect external (403 / 405) — verify manually | {{n}} |
| Server error (5xx) — recheck later | {{n}} |
| Network error | {{n}} |

---

## Broken Internal Links

| File:Line | Link | Suggested replacement |
|-----------|------|----------------------|
| {{file:line}} | {{url}} | {{suggestion}} |

---

## Broken External Links

| File:Line | Link | Status | Suggested replacement |
|-----------|------|--------|----------------------|
| {{file:line}} | {{url}} | {{code}} | {{archive_or_alternative}} |

---

## Verify Manually (403 / 405 / 5xx)

Some servers refuse HEAD requests; these may be fine in a browser.

| File:Line | Link | Status |
|-----------|------|--------|
| {{file:line}} | {{url}} | {{code}} |

---

## Recheck Later (transient errors)

| File:Line | Link | Reason |
|-----------|------|--------|
| {{file:line}} | {{url}} | {{reason}} |
