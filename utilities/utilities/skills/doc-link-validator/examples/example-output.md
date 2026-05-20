# Doc Link Validator Report

**Date:** 20/05/2026
**Root scanned:** `docs/`
**Total links checked:** 247

---

## Summary

| Status | Count |
|--------|-------|
| Healthy (200) | 218 |
| Broken internal (404) | 6 |
| Broken external (404 / 410) | 4 |
| Suspect external (403 / 405) — verify manually | 12 |
| Server error (5xx) — recheck later | 3 |
| Network error | 4 |

---

## Broken Internal Links

| File:Line | Link | Suggested replacement |
|-----------|------|----------------------|
| `docs/getting-started.md:42` | `../guides/install.md` | `../guides/installation.md` (basename match, 1-char diff) |
| `docs/api.md:108` | `./endpoints/users.md` | `./reference/endpoints/users.md` (moved Feb 2026) |
| `docs/troubleshooting.md:14` | `../FAQ.md` | `../faq.md` (case mismatch on Linux filesystems) |
| `docs/changelog.md:200` | `./old-versions.md` | File no longer exists; either restore or remove link |
| `docs/contributing.md:55` | `../CODE_OF_CONDUCT.md` | `../.github/CODE_OF_CONDUCT.md` (moved Mar 2026) |
| `docs/security.md:30` | `./incident-response.md` | `./security/incident-response.md` (newly nested) |

---

## Broken External Links

| File:Line | Link | Status | Suggested replacement |
|-----------|------|--------|----------------------|
| `docs/learn-more.md:8` | https://blog.example.com/old-post | 404 | https://web.archive.org/web/2024/https://blog.example.com/old-post (last cap Jan 2024) |
| `docs/security.md:67` | https://owasp.org/Top10/A03_2017-Sensitive_Data_Exposure/ | 404 | Replaced by 2021 version: https://owasp.org/Top10/A02_2021-Cryptographic_Failures/ |
| `docs/api.md:142` | https://github.com/external/repo/blob/main/docs/auth | 404 | Project archived; consider removing or noting "archived" |
| `docs/team.md:5` | https://www.linkedin.com/in/old-employee | 410 | Profile deleted; remove from team page |

---

## Verify Manually (403 / 405 / 5xx)

Some servers refuse HEAD requests; these may be fine in a browser.

| File:Line | Link | Status |
|-----------|------|--------|
| `docs/dependencies.md:12` | https://www.npmjs.com/package/some-package | 403 |
| `docs/learn-more.md:34` | https://medium.com/@author/article-name | 405 |
| `docs/api.md:201` | https://api.amazonaws.com/docs | 403 |
| ... (9 more) | | |

---

## Recheck Later (transient errors)

| File:Line | Link | Reason |
|-----------|------|--------|
| `docs/getting-started.md:88` | https://status.example.com | 503 (likely brief outage) |
| `docs/cli.md:14` | https://cli.example.com | timeout (slow DNS) |
| `docs/integrations.md:22` | https://newservice.io | connection refused |
