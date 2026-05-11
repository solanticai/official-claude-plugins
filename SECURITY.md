# Security Policy

## Scanning

Every plugin in this marketplace is packaged as a gzipped tarball and submitted to [VirusTotal](https://www.virustotal.com) for multi-engine antivirus scanning. Scans run automatically on:

- **Push to `main`** that touches anything under `plugins/` (changed plugins only via path-scoped triggers)
- **Weekly cron** — Monday at 14:00 UTC (full marketplace rescan)
- **Manual dispatch** via the Actions tab

### Strategy

- **One tarball per plugin** — each `plugins/<name>/` directory is packaged and scanned as a single artefact.
- **Hash-first dedup** — we compute the SHA-256 locally and query VirusTotal by hash. Only previously-unseen tarballs are uploaded, which keeps us well within the public API's 4 req/min and 500 req/day limits.
- **Rate-limit headroom** — 20 seconds between API calls (4 req/min allowed; we use ~3 req/min worst-case).

### Reports

| Artefact | Location | Audience |
|---|---|---|
| Per-plugin markdown summary | `plugins/<name>/VIRUSTOTAL.md` | Humans |
| Raw normalised JSON | `.virustotal/<name>.json` | Tooling, CI consumers, shields.io endpoints |
| Marketplace-wide summary table | below this section | Humans |

### Privacy note

Files uploaded via the VirusTotal public API are shared with VT's AV-vendor partners and VT Intelligence subscribers per their [public API terms](https://developers.virustotal.com/reference/privacy-policy). This marketplace is fully public on GitHub, so the effective exposure is identical to what is already published in the repository. Do **not** add anything private, secret, or customer-identifying to any plugin — uploaded content is not recoverable from VT.

## Reporting a Vulnerability

If you discover a security issue in any plugin or in the marketplace tooling, please email **john@anthril.com** rather than opening a public issue. We will acknowledge receipt within 72 hours.

For dependency vulnerabilities surfaced by VirusTotal scans (non-zero detections in the table below), review the linked VT report first — false positives are common for gzipped shell-heavy archives. Confirmed true positives are treated as P0 and the affected plugin is delisted from `marketplace.json` pending remediation.

<!-- vt-summary:start -->
## Latest scan — 2026-05-11

| Plugin | Detections | Last scan | Report |
|---|---:|---|---|
| business-economics | 0 / 75 | 2026-05-11 | [detail](plugins/business-economics/VIRUSTOTAL.md) |
| data-analysis | 0 / 75 | 2026-05-11 | [detail](plugins/data-analysis/VIRUSTOTAL.md) |
| database-design | 0 / 75 | 2026-05-11 | [detail](plugins/database-design/VIRUSTOTAL.md) |
| devops | 0 / 75 | 2026-05-11 | [detail](plugins/devops/VIRUSTOTAL.md) |
| knowledge-engineering | 0 / 75 | 2026-05-11 | [detail](plugins/knowledge-engineering/VIRUSTOTAL.md) |
| package-manager | 0 / 75 | 2026-05-11 | [detail](plugins/package-manager/VIRUSTOTAL.md) |
| plan-completion-audit | 0 / 75 | 2026-05-11 | [detail](plugins/plan-completion-audit/VIRUSTOTAL.md) |
| ppc-manager | 0 / 75 | 2026-05-11 | [detail](plugins/ppc-manager/VIRUSTOTAL.md) |
| resource-manager | 0 / 75 | 2026-05-11 | [detail](plugins/resource-manager/VIRUSTOTAL.md) |
| software-development | 0 / 75 | 2026-05-11 | [detail](plugins/software-development/VIRUSTOTAL.md) |
<!-- vt-summary:end -->
