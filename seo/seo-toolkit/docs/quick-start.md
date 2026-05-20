# SEO Toolkit — Quick Start

Get from zero to your first SEO analysis in under five minutes.

---

## Prerequisites

- Claude Code with this plugin installed
- Python 3.11+ on your PATH
- At least one SEO data provider account (free options: SerpAPI trial, PSI API key, GSC OAuth)

---

## Step 1 — Install Python dependencies

When you start a new Claude Code session with this plugin loaded, the `ensure-venv.sh` hook automatically creates a virtual environment at `${CLAUDE_PLUGIN_ROOT}/.venv` and installs all dependencies from `requirements.txt`.

You can verify this worked by checking:

```bash
cat "${CLAUDE_PLUGIN_DATA}/python_path.txt"
# Should print something like: /Users/you/.claude/plugins/data/seo-toolkit/.venv/bin/python
```

If the venv was not created, check `${CLAUDE_PLUGIN_DATA}/install.log` for errors. The most common cause is Python < 3.11 on your PATH.

---

## Step 2 — Connect your first provider

Run the interactive setup wizard:

```
/seo-toolkit:seo-connect
```

You will be prompted to choose a provider. For a quick start, pick one of:

- **SerpAPI** — free 100 searches/mo, great for SERP analysis. Get your key at https://serpapi.com/dashboard.
- **PSI** — completely free, no sign-up beyond a Google API key. Enable at https://console.cloud.google.com → APIs & Services → PageSpeed Insights API.
- **GSC** — free OAuth, requires a verified Google Search Console property.

The wizard stores your credentials in an encrypted vault. You will be prompted for a vault passphrase — store this somewhere safe (it will also be saved in your OS keychain via Claude Code's userConfig).

---

## Step 3 — Validate your connection

```
/seo-toolkit:seo-status
```

This runs `scripts/token_validator.py` and renders a table showing which providers are connected and healthy. A ✓ means the credential is present and verified.

---

## Step 4 — Run your first analysis

### If you connected SerpAPI

```
/seo-toolkit:keyword-research [seed keyword or topic]
```

For example:

```
/seo-toolkit:keyword-research accounting software for small business Australia
```

This will pull SERP data, classify intent, and return a structured keyword report.

### If you connected GSC

```
/seo-toolkit:gsc-performance-report
```

This will pull your top queries and pages from the last 90 days and surface quick wins (high impressions, low CTR) and content gap opportunities.

### If you connected PSI

```
/seo-toolkit:core-web-vitals-report [your-domain.com.au]
```

This will measure LCP, INP, CLS, and TTFB for your homepage and top landing pages.

---

## Optional — Install Lighthouse CLI

The `core-web-vitals-report` skill can use either the PSI API (cloud, no install needed) or the local Lighthouse CLI (more detailed, works on staging/local environments). To install Lighthouse:

```bash
npm install -g lighthouse
```

Verify it is available:

```bash
npx lighthouse --version
```

Once installed, the `scripts/lighthouse_runner.sh` helper will automatically use it for local URL audits. The PSI API remains the default for production URLs.

---

## Next steps

- Connect additional providers with `/seo-toolkit:seo-connect <provider>` — see `docs/data-sources.md` for guidance on which providers to prioritise.
- Run a full technical audit: `/seo-toolkit:technical-seo-audit [your-domain.com.au]`
- Analyse your competitors: `/seo-toolkit:competitor-seo-audit [competitor-domain.com.au]`
- Build a keyword cluster map: `/seo-toolkit:keyword-clustering-and-mapping [topic]`

For a full list of available skills, run:

```
/seo-toolkit:
```

(typing the prefix will show available completions in Claude Code)
