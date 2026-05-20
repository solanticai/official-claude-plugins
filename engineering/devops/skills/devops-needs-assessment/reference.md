# DevOps Needs Assessment — Reference

## §1 — Nine-Dimension Scoring Rubric

### 1. CI/CD

| Score | Condition |
|---|---|
| 0 | Pre-launch, single developer, manual deploys are fine |
| 1 | Small team, no automated tests on push, but deploys are scripted |
| 2 | Paying users, no automated tests — regressions are finding them instead of CI |
| 3 | Team of 2+, no CI at all, or CI exists but tests are failing/skipped and nobody cares |

### 2. Infrastructure as Code

| Score | Condition |
|---|---|
| 0 | On a PaaS (Vercel / Netlify / Heroku / Fly / Render) that manages infra for you |
| 1 | A single VM or managed service set up once via the console; rarely changes |
| 2 | Multiple services, multiple environments, all clicked together — nobody can reproduce it |
| 3 | Production relies on undocumented console state; the person who set it up has left or is leaving |

### 3. Containers

| Score | Condition |
|---|---|
| 0 | PaaS handles packaging; no custom Dockerfile needed |
| 1 | Single Dockerfile works, no multi-stage, no `.dockerignore` |
| 2 | Dockerfile copies secrets, runs as root, or uses `latest` tag — would fail a basic security review |
| 3 | Container builds are flaky, images are multi-GB, or `docker build` isn't reproducible across machines |

### 4. Kubernetes

| Score | Condition |
|---|---|
| 0 | Not on Kubernetes and not planning to be |
| 1 | On Kubernetes via a managed service (EKS/GKE/AKS) with default settings |
| 2 | Custom manifests exist but no resource limits, probes, or NetworkPolicies |
| 3 | Running production workloads as root, no RBAC, or Secrets in plaintext YAML in Git |

### 5. Observability

| Score | Condition |
|---|---|
| 0 | Hobby project, no real users, uptime doesn't matter |
| 1 | Paying users, only `console.log` output visible through the PaaS dashboard |
| 2 | Had one or two outages; no structured logs, no metrics, no alerts — diagnosis took hours |
| 3 | Had an outage this month that took more than 30 minutes to diagnose because there was no telemetry |

### 6. Release process

| Score | Condition |
|---|---|
| 0 | Single-tenant tool used by one person; a bad deploy can be rolled back with a git revert |
| 1 | Deploys go straight to production; rollback is "push a revert commit" |
| 2 | Migrations have broken things before; no canary / staging gate |
| 3 | Deploys break users regularly; no rollback plan; migrations are one-way |

### 7. Security & Supply chain

| Score | Condition |
|---|---|
| 0 | Pre-launch, no user data, dependencies are few |
| 1 | Handles user data; lockfile committed but no vulnerability scans |
| 2 | Secrets in `.env` files risk being committed; no branch protection; deps range-pinned |
| 3 | Known vulnerabilities in dependencies and nobody's updating; secrets have leaked before; no 2FA on GitHub |

### 8. Reliability

| Score | Condition |
|---|---|
| 0 | No paying users; if it's down for an hour nobody notices |
| 1 | Has paying users; uptime matters but there's no formal target |
| 2 | Has SLAs to customers but no SLOs internally; on-call is "whoever notices" |
| 3 | Customers pay for reliability that isn't being measured or maintained |

### 9. Docs & Ops knowledge

| Score | Condition |
|---|---|
| 0 | Solo developer; the docs are in their head and that's fine for now |
| 1 | Small team; a `README.md` covers setup; ops knowledge still largely in one person's head |
| 2 | More than one person operates the app; no runbooks; onboarding a new engineer takes weeks |
| 3 | Production depends on one person; if they leave, recovery time is measured in weeks |

---

## §2 — Signal-Detection Heuristics

**Hosting platform detection:**
- Vercel: `vercel.json`, `.vercel/`
- Netlify: `netlify.toml`, `_redirects`
- Heroku: `Procfile`, `app.json`
- Fly.io: `fly.toml`
- Render: `render.yaml`
- AWS Amplify: `amplify.yml`
- Cloudflare: `wrangler.toml`, `wrangler.json`

**Language detection:**
- `package.json` → JavaScript/TypeScript
- `pyproject.toml` / `requirements.txt` / `setup.py` → Python
- `go.mod` → Go
- `Cargo.toml` → Rust
- `pom.xml` / `build.gradle` → Java/Kotlin
- `Gemfile` → Ruby
- `composer.json` → PHP
- `*.csproj` → C#/.NET

**Observability library imports** (grep patterns):
- Logs: `pino`, `winston`, `bunyan`, `zap`, `logrus`, `zerolog`, `structlog`
- Traces: `@opentelemetry/`, `opentelemetry-`, `ddtrace`, `@sentry/`, `sentry-sdk`
- Metrics: `prom-client`, `prometheus_client`, `micrometer`, `statsd`

---

## §3 — Verdict Thresholds (aggregate)

Sum the nine dimension scores (max 27):

| Total | Verdict |
|---|---|
| 0–3 | **Not needed yet.** Re-run in 3 months or after a growth event. |
| 4–8 | **Targeted work.** Pick the top one or two dimensions and address them. |
| 9–14 | **Needed soon.** Your top three actions will pay for themselves. |
| 15+ | **Urgent.** The app is taking on operational debt faster than you're paying it down. |

Override: if any single dimension scores 3, the verdict is at minimum "Needed soon" regardless of total.
