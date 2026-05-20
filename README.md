# Anthril Official Claude Plugins

A curated library of Claude Code plugins for data analysis, entity modelling, business operations, brand management, marketing, developer tooling, database design, and DevOps â€” packaged as a Claude Code marketplace with standalone plugins.

Maintained by [@Anthril](https://github.com/anthril).

## Quick Start

### Install as Plugin

```bash
# Add the marketplace
/plugin marketplace add anthril/official-claude-plugins

# Install individual plugins
/plugin install data-analysis@anthril-claude-plugins
/plugin install knowledge-engineering@anthril-claude-plugins
/plugin install business-economics@anthril-claude-plugins
/plugin install package-manager@anthril-claude-plugins
/plugin install plan-completion-audit@anthril-claude-plugins
/plugin install skillops@anthril-claude-plugins
/plugin install brand-manager@anthril-claude-plugins
/plugin install software-development@anthril-claude-plugins
/plugin install ppc-manager@anthril-claude-plugins
/plugin install database-design@anthril-claude-plugins
/plugin install devops@anthril-claude-plugins
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

Claude Code does **not** auto-refresh marketplaces â€” it reads from a local cache (`~/.claude/plugins/marketplaces/<name>/`) that is only re-fetched on demand. If a `/plugin` view shows you on the latest version when a newer release exists, the cache is stale.

To pick up a new release:

```bash
# 1. Re-fetch the marketplace clone (pulls the latest commit)
/plugin marketplace update anthril-claude-plugins

# 2. Update one or more installed plugins
/plugin update software-development@anthril-claude-plugins
```

The first command advances the cached marketplace's git HEAD; the second installs the new version into `~/.claude/plugins/cache/anthril-claude-plugins/<plugin>/<version>/` and rewrites the entry in `installed_plugins.json`.

See [`CHANGELOG.md`](CHANGELOG.md) for what is in each release before updating.

## Plugins

59 production-ready skills across 11 standalone plugins:

### Data Analysis & Intelligence (`data-analysis`)

| Skill | Description |
|-------|-------------|
| [`anomaly-detection-rule-builder`](data-science/data-analysis/skills/anomaly-detection-rule-builder/) | Build rule-based and statistical anomaly detection systems for business metrics â€” revenue drops, traffic spikes, churn increases, cost overruns |
| [`cohort-analysis-builder`](data-science/data-analysis/skills/cohort-analysis-builder/) | Design cohort analysis frameworks with SQL queries, visualisation specs, and interpretation guides for retention, revenue, and churn analysis |
| [`data-pipeline-architecture`](data-science/data-analysis/skills/data-pipeline-architecture/) | Design ETL/ELT pipeline architectures with data flow diagrams, transformation specs, orchestration, and error handling for Supabase and BigQuery |
| [`data-dictionary-generator`](data-science/data-analysis/skills/data-dictionary-generator/) | Auto-generate comprehensive data dictionaries from database schemas, CSV files, or API responses with column definitions and Mermaid ERD |
| [`dataset-profiling-quality-audit`](data-science/data-analysis/skills/dataset-profiling-quality-audit/) | Profile datasets and audit data quality â€” assess completeness, validity, consistency, uniqueness, timeliness, and accuracy |

### Knowledge Engineering (`knowledge-engineering`)

| Skill | Description |
|-------|-------------|
| [`business-data-model-designer`](data-science/knowledge-engineering/skills/business-data-model-designer/) | Design complete Supabase/PostgreSQL data models with ERD, SQL migrations, RLS policies, indexes, and triggers |
| [`entity-disambiguation`](data-science/knowledge-engineering/skills/entity-disambiguation/) | Resolve entity ambiguity across data sources â€” produce canonical records, merge decisions, and sameAs link mappings |
| [`entity-relationship-mapper`](data-science/knowledge-engineering/skills/entity-relationship-mapper/) | Map business domains to entity-relationship models with Schema.org types, JSON-LD @graph output, and sameAs connections |
| [`knowledge-graph-builder`](data-science/knowledge-engineering/skills/knowledge-graph-builder/) | Construct knowledge graph specifications for Neo4j, JSON-LD, or Supabase/PostgreSQL JSONB implementation |

### Business Economics (`business-economics`)

| Skill | Description |
|-------|-------------|
| [`unit-economics-calculator`](economics/business-economics/skills/unit-economics-calculator/) | Calculate CAC, LTV, payback period, contribution margin with scenario analysis for service, SaaS, and hybrid businesses |
| [`market-sizing-tam-estimator`](economics/business-economics/skills/market-sizing-tam-estimator/) | Estimate TAM, SAM, and SOM using top-down and bottom-up methods with sensitivity analysis, calibrated for Australian markets |

### Package Manager (`package-manager`)

| Skill | Description |
|-------|-------------|
| [`npm-package-audit`](engineering/package-manager/skills/npm-package-audit/) | Audit npm packages for publishing quality, cross-OS compatibility, type declarations, build config, security, and CI/CD â€” produces a scored report with actionable fixes |
| [`cli-ux-audit`](engineering/package-manager/skills/cli-ux-audit/) | Audit any CLI tool for terminal UX â€” help text, command structure, error messages, output formatting, discoverability, and accessibility |

### Plan Completion Audit (`plan-completion-audit`)

| Skill | Description |
|-------|-------------|
| [`plan-completion-audit`](utilities/plan-completion-audit/skills/plan-completion-audit/) | Full-stack audit of a project plan versus actual implementation â€” verifies plan vs code, types, bugs, security, Supabase schema, RLS, and frontend-backend alignment |

### SkillOps (`skillops`)

| Skill | Description |
|-------|-------------|
| [`skill-creator`](utilities/skillops/skills/skill-creator/) | Create new Claude Code skills with proper frontmatter, directory structure, templates, examples, and supporting files |
| [`skill-evaluator`](utilities/skillops/skills/skill-evaluator/) | Audit an existing skill for quality across eight dimensions â€” metadata, scope, conciseness, architecture, content, tooling, testing, standards â€” with a scored markdown report and JSON sidecar |

### Brand Manager (`brand-manager`)

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

### Software Development (`software-development`)

| Skill | Description |
|-------|-------------|
| [`dead-code-audit`](engineering/software-development/skills/dead-code-audit/) | Detect dead code across 9 languages â€” JS/TS, Python, Go, Rust, Java, PHP, Ruby, C# â€” with actionable removal plan |
| [`write-path-mapping`](engineering/software-development/skills/write-path-mapping/) | Map end-to-end write paths from UI to database with framework and database introspection |

### PPC Manager (`ppc-manager`)

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
| [`google-ads-copy`](marketing/ppc-manager/skills/google-ads-copy/) | Write Google Ads copy â€” headlines, descriptions, and extensions |
| [`display-ad-specs`](marketing/ppc-manager/skills/display-ad-specs/) | Generate display ad specifications and creative briefs |
| [`meta-pixel-setup`](marketing/ppc-manager/skills/meta-pixel-setup/) | Set up Meta Pixel with base code and standard events |
| [`meta-capi-setup`](marketing/ppc-manager/skills/meta-capi-setup/) | Configure Meta Conversions API for server-side tracking |
| [`meta-events-mapping`](marketing/ppc-manager/skills/meta-events-mapping/) | Map business events to Meta standard and custom events |
| [`meta-audience-builder`](marketing/ppc-manager/skills/meta-audience-builder/) | Build Meta custom and lookalike audiences |
| [`meta-creative-brief`](marketing/ppc-manager/skills/meta-creative-brief/) | Write creative briefs for Meta ad campaigns |
| [`meta-ads-copy`](marketing/ppc-manager/skills/meta-ads-copy/) | Write Meta ad copy â€” primary text, headlines, and descriptions |
| [`keyword-research`](marketing/ppc-manager/skills/keyword-research/) | Conduct keyword research for PPC campaigns across Google and Meta |
| [`campaign-audit`](marketing/ppc-manager/skills/campaign-audit/) | Cross-platform campaign audit using all four MCP servers |
| [`utm-builder`](marketing/ppc-manager/skills/utm-builder/) | Build UTM parameter conventions and tracking URLs |
| [`landing-page-copy`](marketing/ppc-manager/skills/landing-page-copy/) | Write landing page copy optimised for PPC traffic |
| [`youtube-campaign`](marketing/ppc-manager/skills/youtube-campaign/) | Plan and configure YouTube ad campaigns |

### Database Design (`database-design`)

| Skill | Description |
|-------|-------------|
| [`postgres-schema-audit`](engineering/database-design/skills/postgres-schema-audit/) | Audit any Postgres 13+ schema (Supabase via MCP, or RDS/Cloud SQL/Neon/Railway/self-hosted via a read-only connection) â€” parallel per-schema sub-agents across ten audit categories, producing evidence-backed findings, an ER diagram, and draft migration SQL |

### DevOps (`devops`)

| Skill | Description |
|-------|-------------|
| [`devops-needs-assessment`](engineering/devops/skills/devops-needs-assessment/) | Plain-language DevOps triage for non-experts â€” scores nine dimensions and names the top three fixes |
| [`cicd-pipeline-audit`](engineering/devops/skills/cicd-pipeline-audit/) | Audit CI/CD pipelines (GitHub Actions, GitLab CI, CircleCI, Azure Pipelines, Jenkins, Bitbucket) â€” one sub-agent per workflow |
| [`iac-terraform-audit`](engineering/devops/skills/iac-terraform-audit/) | Audit Terraform, OpenTofu, Terragrunt, and Pulumi modules â€” one sub-agent per module |
| [`container-audit`](engineering/devops/skills/container-audit/) | Audit Dockerfiles and docker-compose files â€” one sub-agent per Dockerfile |
| [`kubernetes-manifest-audit`](engineering/devops/skills/kubernetes-manifest-audit/) | Audit Kubernetes manifests and Helm charts against CIS and NSA/CISA hardening guides |
| [`observability-audit`](engineering/devops/skills/observability-audit/) | Score observability across the four pillars â€” logs, metrics, traces, alerts/dashboards |
| [`release-readiness-audit`](engineering/devops/skills/release-readiness-audit/) | Pre-production go/no-go gate â€” migration safety, rollback, monitoring, deploy strategy |
| [`devsecops-supply-chain-audit`](engineering/devops/skills/devsecops-supply-chain-audit/) | Audit supply chain across every ecosystem detected â€” pinning, vulnerabilities, secrets, SBOM, signing, branch protection |
| [`sre-reliability-audit`](engineering/devops/skills/sre-reliability-audit/) | Assess Site Reliability maturity â€” SLOs, runbooks, on-call, postmortems, game days |

Every DevOps skill supports three operating modes: static (default), `--live` (uses `gh`, `kubectl`, `terraform`, cloud CLIs, scanners), and `--apply` (opt-in remediation with per-change confirmation). Runtime testing (`--runtime`) is available where applicable with production-name guards.

## Skill Features

Every skill in this library includes:

- **YAML frontmatter** â€” `name`, `description` (<250 chars), `argument-hint`, `allowed-tools`, `effort`
- **`$ARGUMENTS`** â€” Accept user input directly (e.g., `/skill-name my business description`)
- **`ultrathink`** â€” Extended thinking enabled for complex analytical skills
- **Output templates** â€” Structured output format with section headers
- **Example outputs** â€” Realistic completed examples with Australian business context
- **Utility scripts** â€” Python/Bash helpers for common operations

Select skills also include:

- **`context: fork`** â€” Research-heavy skills run in isolated subagent context
- **`paths`** â€” Auto-activation when working with matching file patterns
- **`reference.md`** â€” Dense reference material (SQL templates, scoring rubrics, lookup tables) extracted to keep SKILL.md under 500 lines
- **Dynamic context injection** â€” Shell commands that inject project state before the skill runs
- **Parallel sub-agents** â€” Independent audit targets (schemas, workflows, modules, Dockerfiles, charts, ecosystems) are audited in parallel for large-repo throughput

## Plugin Directory Structure

Each plugin follows a consistent layout:

```
plugins/<plugin-name>/
â”œâ”€â”€ .claude-plugin/
â”‚   â””â”€â”€ plugin.json              # Plugin manifest (name, version, author, keywords)
â”œâ”€â”€ skills/
â”‚   â””â”€â”€ <skill-name>/
â”‚       â”œâ”€â”€ SKILL.md              # Main skill instructions (under 500 lines)
â”‚       â”œâ”€â”€ reference.md          # Detailed reference material (where needed)
â”‚       â”œâ”€â”€ LICENSE.txt           # License
â”‚       â”œâ”€â”€ templates/
â”‚       â”‚   â””â”€â”€ output-template.md    # Output format skeleton
â”‚       â”œâ”€â”€ examples/
â”‚       â”‚   â””â”€â”€ example-output.md     # Realistic completed example
â”‚       â””â”€â”€ scripts/
â”‚           â””â”€â”€ helper.sh             # Utility script (where relevant)
â”œâ”€â”€ hooks/
â”‚   â”œâ”€â”€ hooks.json                # Plugin hooks configuration
â”‚   â””â”€â”€ scripts/                  # Hook scripts
â””â”€â”€ settings.json                 # Plugin settings
```

## Repository Structure

```
official-claude-plugins/
â”œâ”€â”€ .claude/
â”‚   â””â”€â”€ CLAUDE.md                          # Project instructions for contributors
â”œâ”€â”€ .claude-plugin/
â”‚   â””â”€â”€ marketplace.json                   # Marketplace catalog (11 plugins)
â”œâ”€â”€ plugins/
â”‚   â”œâ”€â”€ data-analysis/                     # Data Analysis & Intelligence (5 skills)
â”‚   â”œâ”€â”€ knowledge-engineering/             # Knowledge Engineering (4 skills)
â”‚   â”œâ”€â”€ business-economics/                # Business Economics (2 skills)
â”‚   â”œâ”€â”€ package-manager/                   # Package Manager (2 skills)
â”‚   â”œâ”€â”€ plan-completion-audit/             # Plan Completion Audit (1 skill)
â”‚   â”œâ”€â”€ skillops/                          # SkillOps (2 skills)
â”‚   â”œâ”€â”€ brand-manager/                     # Brand Manager (9 skills)
â”‚   â”œâ”€â”€ software-development/              # Software Development (2 skills)
â”‚   â”œâ”€â”€ ppc-manager/                       # PPC Manager (22 skills)
â”‚   â”œâ”€â”€ database-design/                   # Database Design (1 skill)
â”‚   â””â”€â”€ devops/                            # DevOps (9 skills)
â”œâ”€â”€ scripts/
â”‚   â””â”€â”€ check-versions.mjs                 # Verify marketplace â†” plugin.json version sync
â”œâ”€â”€ settings.json                          # Root plugin settings
â”œâ”€â”€ CHANGELOG.md                           # Version history
â”œâ”€â”€ LICENSE                                # MIT
â””â”€â”€ README.md
```

## Creating New Skills

Use the built-in skill creator:

```bash
/skill-creator customer-churn-predictor â€” predict churn risk from behavioural signals
```

Or follow the conventions in [`.claude/CLAUDE.md`](.claude/CLAUDE.md) to create skills manually.

### Skill Development Checklist

- [ ] SKILL.md has valid YAML frontmatter with `name`, `description`, `effort`
- [ ] SKILL.md is under 500 lines
- [ ] Uses `$ARGUMENTS` for user input
- [ ] Description is under 250 characters, front-loaded with key use case
- [ ] `effort` field set appropriately (`medium`, `high`, or `max`)
- [ ] `paths` field set if skill should auto-activate on file patterns
- [ ] `templates/` directory has at least one output template
- [ ] `examples/` directory has at least one example output
- [ ] Dense reference material is in `reference.md`, not SKILL.md
- [ ] Plugin version in `plugin.json` matches marketplace entry (run `node scripts/check-versions.mjs`)
- [ ] Tested locally with `claude --plugin-dir .`

## Contributing

1. Fork the repository
2. Create a new skill using `/skill-creator`
3. Place it in the appropriate plugin directory under `plugins/`
4. Test locally with `claude --plugin-dir .`
5. Submit a pull request

See [`.claude/CLAUDE.md`](.claude/CLAUDE.md) for detailed development standards.

## Sponsors

This project is maintained by [Anthril](https://github.com/anthril) and funded by our sponsors.

[Become a sponsor â†’](https://github.com/sponsors/anthril)

<!-- sponsors --><!-- sponsors -->

## License

MIT
