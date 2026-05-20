# Anthril Official Claude Plugins

A curated library of Claude Code plugins organised into eight customer-facing categories — **Lifestyle**, **SMB**, **Marketing**, **Engineering**, **Data Science**, **Economics**, **Utilities**, and **SEO** — packaged as a Claude Code marketplace with standalone plugins.

**14 plugins · 89 production-ready skills · Australian English throughout · evidence-backed markdown outputs.**

Maintained by [@Anthril](https://github.com/anthril).

## Quick Start

### Install as Plugin

```bash
# Add the marketplace
/plugin marketplace add anthril/official-claude-plugins

# Install one or more plugins
/plugin install brand-manager@anthril-claude-plugins
/plugin install business-operations@anthril-claude-plugins
/plugin install ppc-manager@anthril-claude-plugins
/plugin install software-development@anthril-claude-plugins
/plugin install devops@anthril-claude-plugins
/plugin install database-design@anthril-claude-plugins
/plugin install package-manager@anthril-claude-plugins
/plugin install data-analysis@anthril-claude-plugins
/plugin install knowledge-engineering@anthril-claude-plugins
/plugin install business-economics@anthril-claude-plugins
/plugin install skillops@anthril-claude-plugins
/plugin install resource-manager@anthril-claude-plugins
/plugin install plan-completion-audit@anthril-claude-plugins
/plugin install seo-toolkit@anthril-claude-plugins
```

### Install a Single Skill

```bash
# Copy one skill to your personal skills directory
cp -r data-science/data-analysis/skills/knowledge-graph-builder ~/.claude/skills/
```

### Test Locally

```bash
# Load the full marketplace for development
claude --plugin-dir .

# Load a single plugin
claude --plugin-dir ./data-science/data-analysis

# List available skills
/skills

# Run a skill
/knowledge-graph-builder Build a knowledge graph for a consulting firm
```

## Updating

Claude Code does **not** auto-refresh marketplaces — it reads from a local cache (`~/.claude/plugins/marketplaces/<name>/`) that is only re-fetched on demand. If a `/plugin` view shows you on the latest version when a newer release exists, the cache is stale.

To pick up a new release:

```bash
# 1. Re-fetch the marketplace clone (pulls the latest commit)
/plugin marketplace update anthril-claude-plugins

# 2. Update one or more installed plugins
/plugin update software-development@anthril-claude-plugins
```

The first command advances the cached marketplace's git HEAD; the second installs the new version into `~/.claude/plugins/cache/anthril-claude-plugins/<plugin>/<version>/` and rewrites the entry in `installed_plugins.json`.

See [`CHANGELOG.md`](CHANGELOG.md) for what is in each release before updating.

---

## Plugins by Category

### Lifestyle

*Reserved placeholder for forthcoming personal-productivity, health, finance, and household plugins.*

### SMB

#### Brand Manager (`smb/brand-manager` — 9 skills)

| Skill | Description |
|-------|-------------|
| [`brand-identity`](smb/brand-manager/skills/brand-identity/) | Define brand purpose, values, personality, voice, and positioning statement |
| [`brand-guidelines`](smb/brand-manager/skills/brand-guidelines/) | Create comprehensive brand guidelines covering typography, colour, imagery, and tone of voice |
| [`target-audience`](smb/brand-manager/skills/target-audience/) | Build detailed audience personas with demographics, psychographics, and journey maps |
| [`competitor-analysis`](smb/brand-manager/skills/competitor-analysis/) | Analyse competitors across positioning, messaging, visual identity, and market gaps |
| [`logo-brief`](smb/brand-manager/skills/logo-brief/) | Write a logo design brief with concept direction, usage rules, and file format specs |
| [`color-palette`](smb/brand-manager/skills/color-palette/) | Design a brand colour palette with primary, secondary, accent, and semantic colours |
| [`design-tokens`](smb/brand-manager/skills/design-tokens/) | Generate design tokens for typography, colour, spacing, and elevation in JSON/CSS format |
| [`legal-disclaimers`](smb/brand-manager/skills/legal-disclaimers/) | Draft legal disclaimers, terms, and compliance notices for Australian businesses |
| [`website-copy`](smb/brand-manager/skills/website-copy/) | Write website copy for landing pages, about sections, and CTAs aligned to brand voice |

#### Business Operations (`smb/business-operations` — 5 skills)

| Skill | Description |
|-------|-------------|
| [`kpi-framework-generator`](smb/business-operations/skills/kpi-framework-generator/) | Layered KPI framework — North-Star metric → input metrics → functional KPIs per team — tied to OKRs |
| [`operational-bottleneck-detector`](smb/business-operations/skills/operational-bottleneck-detector/) | Identify bottlenecks across people, process, systems, and supply; quantify throughput loss; prioritise fixes |
| [`pricing-strategy-analyser`](smb/business-operations/skills/pricing-strategy-analyser/) | Recommend pricing model, price points, packaging, and elasticity guard-rails grounded in Van Westendorp |
| [`revenue-channel-mapper`](smb/business-operations/skills/revenue-channel-mapper/) | Map every revenue channel — contribution %, CAC, LTV, friction score — and prioritise with RICE |
| [`stakeholder-brief-builder`](smb/business-operations/skills/stakeholder-brief-builder/) | One-page stakeholder briefs tailored by audience (board, investors, staff, customers, suppliers) |

### Marketing

#### PPC Manager (`marketing/ppc-manager` — 22 skills)

23 skills for end-to-end PPC across Google Ads, Meta Ads, GA4, and GTM — with OAuth-authenticated read/write via bundled Python MCP servers.

| Skill | Description |
|-------|-------------|
| [`oauth-setup`](marketing/ppc-manager/skills/oauth-setup/) | Walk through OAuth setup for Google and Meta platforms with encrypted vault storage |
| [`gtm-setup`](marketing/ppc-manager/skills/gtm-setup/) | Set up Google Tag Manager containers, workspaces, and base configuration |
| [`gtm-datalayer`](marketing/ppc-manager/skills/gtm-datalayer/) | Design and implement GTM data layer specifications |
| [`gtm-tags`](marketing/ppc-manager/skills/gtm-tags/) | Create and configure GTM tags, triggers, and variables |
| [`ga4-setup`](marketing/ppc-manager/skills/ga4-setup/) | Set up GA4 properties, data streams, and base configuration |
| [`ga4-events`](marketing/ppc-manager/skills/ga4-events/) | Design and implement GA4 custom events and conversions |
| [`google-ads-account-setup`](marketing/ppc-manager/skills/google-ads-account-setup/) | Set up Google Ads account structure, billing, and conversion tracking |
| [`google-search-campaign`](marketing/ppc-manager/skills/google-search-campaign/) | Build Google Search campaigns with ad groups, keywords, and ads |
| [`google-pmax-campaign`](marketing/ppc-manager/skills/google-pmax-campaign/) | Build Google Performance Max campaigns with asset groups and signals |
| [`google-ads-copy`](marketing/ppc-manager/skills/google-ads-copy/) | Write Google Ads copy — headlines, descriptions, and extensions |
| [`display-ad-specs`](marketing/ppc-manager/skills/display-ad-specs/) | Generate display ad specifications and creative briefs |
| [`meta-pixel-setup`](marketing/ppc-manager/skills/meta-pixel-setup/) | Set up Meta Pixel with base code and standard events |
| [`meta-capi-setup`](marketing/ppc-manager/skills/meta-capi-setup/) | Configure Meta Conversions API for server-side tracking |
| [`meta-events-mapping`](marketing/ppc-manager/skills/meta-events-mapping/) | Map business events to Meta standard and custom events |
| [`meta-audience-builder`](marketing/ppc-manager/skills/meta-audience-builder/) | Build Meta custom and lookalike audiences |
| [`meta-creative-brief`](marketing/ppc-manager/skills/meta-creative-brief/) | Write creative briefs for Meta ad campaigns |
| [`meta-ads-copy`](marketing/ppc-manager/skills/meta-ads-copy/) | Write Meta ad copy — primary text, headlines, and descriptions |
| [`keyword-research`](marketing/ppc-manager/skills/keyword-research/) | Conduct keyword research for PPC campaigns across Google and Meta |
| [`campaign-audit`](marketing/ppc-manager/skills/campaign-audit/) | Cross-platform campaign audit using all four MCP servers |
| [`utm-builder`](marketing/ppc-manager/skills/utm-builder/) | Build UTM parameter conventions and tracking URLs |
| [`landing-page-copy`](marketing/ppc-manager/skills/landing-page-copy/) | Write landing page copy optimised for PPC traffic |
| [`youtube-campaign`](marketing/ppc-manager/skills/youtube-campaign/) | Plan and configure YouTube ad campaigns |

### Engineering

#### Software Development (`engineering/software-development` — 4 skills)

| Skill | Description |
|-------|-------------|
| [`application-audit`](engineering/software-development/skills/application-audit/) | Multi-agent audit for Next.js + React + Supabase apps — ten parallel specialist auditors with validated findings and an action plan |
| [`plan-orchestrator`](engineering/software-development/skills/plan-orchestrator/) | Turn a bullet list of tasks into one ordered plan with full coverage verification — fans out specialist sub-agents in Plan Mode |
| [`dead-code-audit`](engineering/software-development/skills/dead-code-audit/) | Detect dead code across 9 languages — JS/TS, Python, Go, Rust, Java, PHP, Ruby, C# — with an actionable removal plan |
| [`write-path-mapping`](engineering/software-development/skills/write-path-mapping/) | Map end-to-end write paths from UI to database with framework and database introspection |

#### DevOps (`engineering/devops` — 9 skills)

Every DevOps skill supports three operating modes: static (default), `--live` (uses `gh`, `kubectl`, `terraform`, cloud CLIs, scanners), and `--apply` (opt-in remediation with per-change confirmation). Runtime testing (`--runtime`) is available where applicable with production-name guards.

| Skill | Description |
|-------|-------------|
| [`devops-needs-assessment`](engineering/devops/skills/devops-needs-assessment/) | Plain-language DevOps triage for non-experts — scores nine dimensions and names the top three fixes |
| [`cicd-pipeline-audit`](engineering/devops/skills/cicd-pipeline-audit/) | Audit CI/CD pipelines (GitHub Actions, GitLab CI, CircleCI, Azure Pipelines, Jenkins, Bitbucket) — one sub-agent per workflow |
| [`iac-terraform-audit`](engineering/devops/skills/iac-terraform-audit/) | Audit Terraform, OpenTofu, Terragrunt, and Pulumi modules — one sub-agent per module |
| [`container-audit`](engineering/devops/skills/container-audit/) | Audit Dockerfiles and docker-compose files — one sub-agent per Dockerfile |
| [`kubernetes-manifest-audit`](engineering/devops/skills/kubernetes-manifest-audit/) | Audit Kubernetes manifests and Helm charts against CIS and NSA/CISA hardening guides |
| [`observability-audit`](engineering/devops/skills/observability-audit/) | Score observability across the four pillars — logs, metrics, traces, alerts/dashboards |
| [`release-readiness-audit`](engineering/devops/skills/release-readiness-audit/) | Pre-production go/no-go gate — migration safety, rollback, monitoring, deploy strategy |
| [`devsecops-supply-chain-audit`](engineering/devops/skills/devsecops-supply-chain-audit/) | Audit supply chain across every ecosystem detected — pinning, vulnerabilities, secrets, SBOM, signing, branch protection |
| [`sre-reliability-audit`](engineering/devops/skills/sre-reliability-audit/) | Assess Site Reliability maturity — SLOs, runbooks, on-call, postmortems, game days |

#### Database Design (`engineering/database-design` — 1 skill)

| Skill | Description |
|-------|-------------|
| [`postgres-schema-audit`](engineering/database-design/skills/postgres-schema-audit/) | Audit any Postgres 13+ schema (Supabase via MCP, or RDS/Cloud SQL/Neon/Railway/self-hosted via a read-only connection) — parallel per-schema sub-agents across ten audit categories, producing evidence-backed findings, an ER diagram, and draft migration SQL |

#### Package Manager (`engineering/package-manager` — 2 skills)

| Skill | Description |
|-------|-------------|
| [`npm-package-audit`](engineering/package-manager/skills/npm-package-audit/) | Audit npm packages for publishing quality, cross-OS compatibility, type declarations, build config, security, and CI/CD — produces a scored report with actionable fixes |
| [`cli-ux-audit`](engineering/package-manager/skills/cli-ux-audit/) | Audit any CLI tool for terminal UX — help text, command structure, error messages, output formatting, discoverability, and accessibility |

### Data Science

#### Data Analysis (`data-science/data-analysis` — 5 skills)

| Skill | Description |
|-------|-------------|
| [`anomaly-detection-rule-builder`](data-science/data-analysis/skills/anomaly-detection-rule-builder/) | Build rule-based and statistical anomaly detection systems for business metrics — revenue drops, traffic spikes, churn increases, cost overruns |
| [`cohort-analysis-builder`](data-science/data-analysis/skills/cohort-analysis-builder/) | Design cohort analysis frameworks with SQL queries, visualisation specs, and interpretation guides for retention, revenue, and churn |
| [`data-pipeline-architecture`](data-science/data-analysis/skills/data-pipeline-architecture/) | Design ETL/ELT pipeline architectures with data flow diagrams, transformation specs, orchestration, and error handling for Supabase and BigQuery |
| [`data-dictionary-generator`](data-science/data-analysis/skills/data-dictionary-generator/) | Auto-generate comprehensive data dictionaries from database schemas, CSV files, or API responses with column definitions and Mermaid ERD |
| [`dataset-profiling-quality-audit`](data-science/data-analysis/skills/dataset-profiling-quality-audit/) | Profile datasets and audit data quality — completeness, validity, consistency, uniqueness, timeliness, accuracy |

#### Knowledge Engineering (`data-science/knowledge-engineering` — 4 skills)

| Skill | Description |
|-------|-------------|
| [`business-data-model-designer`](data-science/knowledge-engineering/skills/business-data-model-designer/) | Design complete Supabase/PostgreSQL data models with ERD, SQL migrations, RLS policies, indexes, and triggers |
| [`entity-disambiguation`](data-science/knowledge-engineering/skills/entity-disambiguation/) | Resolve entity ambiguity across data sources — canonical records, merge decisions, and sameAs link mappings |
| [`entity-relationship-mapper`](data-science/knowledge-engineering/skills/entity-relationship-mapper/) | Map business domains to entity-relationship models with Schema.org types, JSON-LD `@graph` output, and sameAs connections |
| [`knowledge-graph-builder`](data-science/knowledge-engineering/skills/knowledge-graph-builder/) | Construct knowledge graph specifications for Neo4j, JSON-LD, or Supabase/PostgreSQL JSONB implementation |

### Economics

#### Business Economics (`economics/business-economics` — 2 skills)

| Skill | Description |
|-------|-------------|
| [`unit-economics-calculator`](economics/business-economics/skills/unit-economics-calculator/) | Calculate CAC, LTV, payback period, contribution margin with scenario analysis for service, SaaS, and hybrid businesses |
| [`market-sizing-tam-estimator`](economics/business-economics/skills/market-sizing-tam-estimator/) | Estimate TAM, SAM, and SOM using top-down and bottom-up methods with sensitivity analysis, calibrated for Australian markets |

### Utilities

#### SkillOps (`utilities/skillops` — 4 skills)

| Skill | Description |
|-------|-------------|
| [`skill-creator`](utilities/skillops/skills/skill-creator/) | Create new Claude Code skills with proper frontmatter, directory structure, templates, examples, and supporting files |
| [`skill-evaluator`](utilities/skillops/skills/skill-evaluator/) | Audit an existing skill across **ten** quality dimensions — discovery, scope, conciseness, IA, content, tooling, testing, standards, activation/behaviour, anti-patterns — with a scored markdown report and JSON sidecar |
| [`skill-eval-harness`](utilities/skillops/skills/skill-eval-harness/) | Run an `evals/suite.yaml` against a skill — activation tests, functional tests, edge cases, and a regression diff vs the previous run |
| [`skill-eval-bootstrap`](utilities/skillops/skills/skill-eval-bootstrap/) | Scaffold a starter `evals/suite.yaml` from a skill's description, examples, and emitted error codes |

#### Resource Manager (`utilities/resource-manager` — 4 skills)

| Skill | Description |
|-------|-------------|
| [`resource-dashboard`](utilities/resource-manager/skills/resource-dashboard/) | Launch a localhost browser dashboard showing live Claude process tree, memory use, MCP servers, and orphan count |
| [`resource-dashboard-stop`](utilities/resource-manager/skills/resource-dashboard-stop/) | Shut down the Resource Manager localhost dashboard server |
| [`resource-snapshot`](utilities/resource-manager/skills/resource-snapshot/) | One-shot markdown report of the Claude process tree, MCP servers, orphans, and total memory |
| [`mcp-server-audit`](utilities/resource-manager/skills/mcp-server-audit/) | Audit MCP server registrations across user, project, and plugin configs — report always-on servers, duplicates, and drift |

#### Plan Completion Audit (`utilities/plan-completion-audit` — 1 skill)

| Skill | Description |
|-------|-------------|
| [`plan-completion-audit`](utilities/plan-completion-audit/skills/plan-completion-audit/) | Full-stack audit of a project plan versus actual implementation — verifies plan vs code, types, bugs, security, Supabase schema, RLS, and frontend-backend alignment |

### SEO

#### SEO Toolkit (`seo/seo-toolkit` — 17 skills)

End-to-end SEO across technical, content, local, and analytics workflows.

| Skill | Description |
|-------|-------------|
| [`technical-seo-audit`](seo/seo-toolkit/skills/technical-seo-audit/) | Full Crawl/Render/Index/Rank pillars audit — robots.txt, sitemaps, canonicalisation, hreflang, JS rendering, mobile usability, Core Web Vitals |
| [`on-page-audit`](seo/seo-toolkit/skills/on-page-audit/) | Single-URL or sitemap on-page SEO — title, meta, headings, internal links, schema, alt text, word count |
| [`backlink-audit`](seo/seo-toolkit/skills/backlink-audit/) | Audit a domain's backlink profile via Ahrefs, Moz, or a free-tier fallback — referring-domain register, anchor history, toxic-link triage |
| [`competitor-seo-audit`](seo/seo-toolkit/skills/competitor-seo-audit/) | Audit one or more competitor domains across indexed footprint, content topics, top keywords, backlinks, on-page patterns, and tech |
| [`local-seo-audit`](seo/seo-toolkit/skills/local-seo-audit/) | NAP consistency, Google Business Profile completeness, citation coverage, review velocity, and Local Pack positioning |
| [`broken-link-scanner`](seo/seo-toolkit/skills/broken-link-scanner/) | Crawl a domain or sitemap to find broken links (4xx/5xx), orphan pages, and soft-404s with a remediation register |
| [`core-web-vitals-report`](seo/seo-toolkit/skills/core-web-vitals-report/) | Core Web Vitals (LCP, INP, CLS) for a URL list or sitemap via PageSpeed Insights and CrUX — per-URL scorecard |
| [`gsc-performance-report`](seo/seo-toolkit/skills/gsc-performance-report/) | Google Search Console performance — clicks, impressions, CTR, position deltas with statistical-significance bands |
| [`serp-analysis`](seo/seo-toolkit/skills/serp-analysis/) | Analyse a single query's SERP — features present, top-10 organic results, content-format mix, intent, and ranking opportunities |
| [`keyword-research`](seo/seo-toolkit/skills/keyword-research/) | Expand seed terms into a prioritised keyword set with intent classification, volume, difficulty, and parent-topic grouping |
| [`keyword-list-developer`](seo/seo-toolkit/skills/keyword-list-developer/) | Deduplicated, intent-classified, volume/difficulty-annotated master keyword list from seed terms — CSV output |
| [`keyword-clustering-and-mapping`](seo/seo-toolkit/skills/keyword-clustering-and-mapping/) | Cluster a master keyword list, map clusters to existing pages, detect content gaps + cannibalisation, 30/60/90-day plan |
| [`content-brief-generator`](seo/seo-toolkit/skills/content-brief-generator/) | Single-keyword or cluster-grounded editorial brief — H-structure, SERP intent, internal links, schema, E-E-A-T signals |
| [`content-gap-analysis`](seo/seo-toolkit/skills/content-gap-analysis/) | Find keywords competitors rank for that your domain doesn't — gap clustering, opportunity scoring, prioritised content plan |
| [`internal-linking-planner`](seo/seo-toolkit/skills/internal-linking-planner/) | Internal link plan from a sitemap or URL list — hub-and-spoke topology, authority scoring, prioritised link recommendations |
| [`schema-markup-generator`](seo/seo-toolkit/skills/schema-markup-generator/) | Copy-paste JSON-LD schema for any page type — Article, Product, FAQPage, LocalBusiness, HowTo, and more |
| [`redirect-map-builder`](seo/seo-toolkit/skills/redirect-map-builder/) | 301 redirect map between old and new sitemaps for site migrations — pattern matching, slug similarity scoring, confidence bands |

---

## Skill Features

Every skill in this library includes:

- **YAML frontmatter** — `name`, `description` (≤ 250 chars), `argument-hint`, `allowed-tools`, `effort`
- **`$ARGUMENTS`** — accept user input directly (e.g. `/skill-name my business description`)
- **`ultrathink`** — extended thinking enabled for complex analytical skills
- **Output templates** under `templates/` — structured output format with section headers
- **Example outputs** under `examples/` — realistic completed examples with Australian business context
- **Utility scripts** under `scripts/` — Python/Bash helpers for common operations
- **Eval suite** under `evals/suite.yaml` — declarative test cases (≥ 3 activation-positive, ≥ 2 activation-negative, ≥ 2 edge) plus an iteration log

Select skills also include:

- **`context: fork`** — research-heavy skills run in isolated subagent context
- **`paths`** — auto-activation when working with matching file patterns
- **`reference.md`** — dense reference material (SQL templates, scoring rubrics, lookup tables) extracted to keep SKILL.md under 500 lines
- **Dynamic context injection** — shell commands that inject project state before the skill runs
- **Parallel sub-agents** — independent audit targets (schemas, workflows, modules, Dockerfiles, charts, ecosystems) audited in parallel for large-repo throughput

## Quality + Evaluation

Every skill is audited against a 10-dimension rubric and exercised by a fleet-wide LLM-as-judge harness:

- **Audit** — `/skill-evaluator <path>` produces a scored markdown report + JSON sidecar across 10 dimensions (45 deterministic checks plus a qualitative review). See [`utilities/skillops/skills/skill-evaluator/`](utilities/skillops/skills/skill-evaluator/).
- **Eval suites** — every skill has an `evals/suite.yaml` containing activation, functional, edge-case, and regression tests. Generated and tuned by `/skill-eval-bootstrap` and `tune-criteria.mjs`.
- **Harness** — `/skill-eval-harness <skill> [--mode=fast]` runs the suite, dispatches the LLM-as-judge in a fresh subagent context, and emits a markdown run report plus an iteration-log row.
- **Latest fleet run** — see [`audits/2026-05-20/judge/fleet-judge.md`](audits/2026-05-20/judge/fleet-judge.md) for the most recent fleet-wide judge verdicts.

## Repository Structure

```
official-claude-plugins/
├── .claude/
│   ├── CLAUDE.md                  # Project instructions for contributors
│   └── hooks/                     # Changelog + plugin-manifest reminders
├── .claude-plugin/
│   └── marketplace.json           # Marketplace catalogue (14 plugins)
├── .github/
│   └── workflows/                 # validate-marketplace, virustotal-audit, sponsors
├── lifestyle/                     # (placeholder — no plugins yet)
├── smb/
│   ├── brand-manager/             # 9 skills
│   └── business-operations/       # 5 skills
├── marketing/
│   └── ppc-manager/               # 22 skills + 4 Python MCP servers
├── engineering/
│   ├── software-development/      # 4 skills
│   ├── devops/                    # 9 skills
│   ├── database-design/           # 1 skill
│   └── package-manager/           # 2 skills
├── data-science/
│   ├── data-analysis/             # 5 skills
│   └── knowledge-engineering/     # 4 skills
├── economics/
│   └── business-economics/        # 2 skills
├── utilities/
│   ├── skillops/                  # 4 skills (skill-creator/evaluator/eval-harness/eval-bootstrap)
│   ├── resource-manager/          # 4 skills + localhost dashboard
│   └── plan-completion-audit/     # 1 skill
├── seo/
│   └── seo-toolkit/               # 17 skills
├── audits/                        # Time-stamped audit + judge reports
│   └── 2026-05-20/
│       ├── summary.md
│       ├── plan-completion-audit.md
│       └── judge/
│           ├── fleet-judge.md     # Aggregate LLM-as-judge report
│           ├── prompts/<skill>.txt
│           └── results/<skill>.json
├── scripts/
│   ├── check-versions.mjs         # Verify marketplace ↔ plugin.json version sync
│   └── virustotal-audit.mjs       # Weekly VT scan of every plugin tarball
├── .virustotal/                   # Per-plugin VT scan sidecars
├── CHANGELOG.md
├── SECURITY.md                    # VirusTotal policy + scan results
├── SPONSORS.md
├── LICENSE                        # MIT
└── README.md
```

### Plugin layout

Each plugin follows a consistent layout under its category directory:

```
<category>/<plugin>/
├── .claude-plugin/
│   └── plugin.json                # Plugin manifest
├── skills/
│   └── <skill-name>/
│       ├── SKILL.md               # Main skill instructions (≤ 500 lines)
│       ├── reference.md           # Dense reference material (where needed)
│       ├── LICENSE.txt
│       ├── templates/
│       │   └── output-template.md
│       ├── examples/
│       │   └── example-output.md
│       ├── scripts/               # Utility scripts (where relevant)
│       └── evals/
│           ├── suite.yaml         # Declarative test cases
│           └── iteration-log.md   # Append-only run log
├── hooks/                         # Plugin lifecycle hooks (optional)
│   ├── hooks.json
│   └── scripts/
├── settings.json                  # Plugin settings (usually empty {})
├── README.md
└── VIRUSTOTAL.md                  # Latest VirusTotal scan summary
```

## Creating New Skills

Use the built-in skill creator:

```bash
/skill-creator customer-churn-predictor — predict churn risk from behavioural signals
```

Or follow the conventions in [`.claude/CLAUDE.md`](.claude/CLAUDE.md) to create skills manually.

### Skill Development Checklist

- [ ] SKILL.md has valid YAML frontmatter with `name`, `description`, `argument-hint`, `allowed-tools`, `effort`
- [ ] SKILL.md is under 500 lines
- [ ] Uses `$ARGUMENTS` for user input
- [ ] Description is under 250 characters, front-loaded with key use case
- [ ] `effort` field set appropriately (`low`, `medium`, `high`, `max`)
- [ ] `paths` field set if skill should auto-activate on file patterns
- [ ] `templates/` directory has at least one output template
- [ ] `examples/` directory has at least one example output
- [ ] Dense reference material is in `reference.md`, not SKILL.md
- [ ] `evals/suite.yaml` generated via `/skill-eval-bootstrap`
- [ ] Australian English throughout (colour, optimise, behaviour, organise)
- [ ] Plugin version in `plugin.json` matches marketplace entry (run `node scripts/check-versions.mjs`)
- [ ] Tested locally with `claude --plugin-dir .`

## Contributing

1. Fork the repository
2. Create a new skill using `/skill-creator`
3. Place it under the appropriate `<category>/<plugin>/skills/` directory
4. Generate a baseline eval suite with `/skill-eval-bootstrap <skill>`
5. Test locally with `claude --plugin-dir .`
6. Submit a pull request

See [`.claude/CLAUDE.md`](.claude/CLAUDE.md) for detailed development standards.

## Sponsors

This project is maintained by [Anthril](https://github.com/anthril) and funded by our sponsors.

[Become a sponsor →](https://github.com/sponsors/anthril)

<!-- sponsors --><!-- sponsors -->

## License

MIT
