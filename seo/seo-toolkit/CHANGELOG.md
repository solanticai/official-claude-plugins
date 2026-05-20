# Changelog

## [1.0.0] - 2026-05-20

### Added
- Initial release. 17 skills covering keyword research + list development + clustering/mapping, SERP analysis, competitor + on-page + technical audits, Core Web Vitals, backlinks, content gap analysis, content briefs, internal-link planning, schema generation, GSC performance reporting, local SEO, redirect mapping, broken-link scanning.
- 3 sub-agents: `seo-auditor`, `serp-analyst`, `content-strategist`.
- 3 slash commands: `/seo-toolkit:seo-connect`, `/seo-toolkit:seo-status`, `/seo-toolkit:seo-disconnect`.
- SessionStart hooks (`ensure-venv.sh`, `check-credentials.sh`) + Stop hook (`suggest-related.sh`).
- Encrypted Fernet vault for SerpAPI, DataForSEO, Ahrefs, Moz, PageSpeed Insights, GSC OAuth, GA4 OAuth credentials.
- `keyword-clustering-and-mapping` skill wraps the external [keyword-clustering](https://github.com/johnoconnor0/keyword-clustering) package.
