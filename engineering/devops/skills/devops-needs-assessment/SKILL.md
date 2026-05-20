---
name: devops-needs-assessment
description: Plain-language DevOps triage for non-experts. Given an app path or description, scores nine dimensions on a 0–3 scale and names the top three fixes. Jargon-free output with pointers into the other eight DevOps skills.
argument-hint: [application-path-or-description]
allowed-tools: Read Grep Glob Write Edit Bash(bash:*) Agent
effort: medium
---

# DevOps Needs Assessment

## When to use

Run this skill when the user asks:
- "Do I need DevOps?"
- "Is my app production-ready?"
- "What DevOps work should I do first?"
- Describes a new app and wants direction

Scores nine dimensions — CI/CD, Infrastructure as Code, Containers, Kubernetes, Observability, Release process, Security, Reliability, Docs — on a four-point scale from *Not needed yet* to *Urgent*. Designed for founders, solo developers, and designers-turned-operators.

## Before You Start

1. **This is the plain-language entry point.** The user is probably not a DevOps engineer. Explain every recommendation in everyday English. Do not use jargon without defining it. Never say "you need to implement RBAC" — say "right now anyone with access to your cluster can do anything; you should restrict who can do what."
2. **You may not have access to the code.** If the user gave you a description rather than a repo, work from the description and the questionnaire. Do not fabricate signals.
3. **Three-mode support.** This skill is always static. It never touches cloud state and never applies changes. The other eight skills in this plugin are the ones that handle live access and apply mode.
4. **Output a single markdown file.** `devops-needs-assessment.md` in the current working directory. Nothing else.
5. **Load `.dna-ignore`** if present — each line is a dimension name (e.g., `kubernetes`) to skip scoring for. Useful when the user knows a dimension doesn't apply.

## User Context

$ARGUMENTS

Stack fingerprint: !`bash "${CLAUDE_PLUGIN_ROOT}/skills/devops-needs-assessment/scripts/detect-stack.sh" 2>/dev/null || echo "no-repo"`

---

## Assessment Phases

Execute every phase in order.

---

### Phase 1: Context Capture

**Objective:** Understand what the application is and how it runs today.

1. If `$ARGUMENTS` is a path, run the stack-detection script (already run in User Context above) and read the resulting fingerprint.
2. If `$ARGUMENTS` is a description (no path), extract: language, framework, hosting platform, user count, deploy frequency, downtime history.
3. **Ask the user plain-language questions** via `AskUserQuestion` to fill any gaps. Ask at most seven. Pick from the questionnaire at `templates/questionnaire.md`. Never ask about something already answered by the fingerprint. Examples:
   - "Roughly how many people use this app right now?" (options: <100 / 100–10k / 10k–100k / 100k+)
   - "How do you deploy a change today?" (I push to main / I run a script / I click a button / someone else handles it)
   - "Have you ever had the app go down in a way users noticed?" (never / once or twice / regularly / every week)
   - "Where does it run?" (Vercel/Netlify/Heroku / A cloud VM / Kubernetes / I don't know)
4. Record answers. If critical fields are missing after seven questions, continue with "unknown" — do not ask more.

### Phase 2: Surface Scan

**Objective:** For each repo signal, record present / absent / unknown. No judgement yet.

Check for the following, via `Glob`/`Grep` if a path was given:

| Signal | What to look for |
|---|---|
| CI/CD config | `.github/workflows/*.yml`, `.gitlab-ci.yml`, `.circleci/config.yml`, `azure-pipelines.yml`, `Jenkinsfile`, `bitbucket-pipelines.yml` |
| Containerisation | `Dockerfile*`, `docker-compose*.yml` |
| Infrastructure as Code | `*.tf`, `*.tf.json`, `terragrunt.hcl`, Pulumi (`Pulumi.yaml`), CDK (`cdk.json`), Bicep (`*.bicep`), ARM templates |
| Kubernetes | `kubernetes/`, `k8s/`, `manifests/`, `charts/`, `Chart.yaml`, `kustomization.yaml` |
| Tests | `tests/`, `__tests__/`, `*_test.go`, `*.test.ts`, `pytest.ini`, `jest.config.*`, `vitest.config.*` |
| Observability | Imports of `pino`, `winston`, `zap`, `logrus`, `structlog`, `@opentelemetry/*`, `sentry-sdk`, `datadog`, `newrelic` |
| Secrets management | `.env.example` without `.env` committed, Vault/SOPS/Doppler/AWS-Secrets references, `sops.yaml` |
| Branch protection docs | `.github/CODEOWNERS`, `.github/branch-protection.yml`, notes in `CONTRIBUTING.md` |
| Runbook / ops docs | `RUNBOOK.md`, `docs/runbooks/`, `OPERATIONS.md`, `docs/on-call/` |
| Monitoring config | `prometheus.yml`, `grafana/`, `otel-collector-config.yaml`, `alertmanager.yml`, Datadog dashboard JSON |
| SLO / reliability | `slo.yaml`, `slis.yaml`, `error-budget.md` |
| Feature flags | imports of `@unleash/*`, `launchdarkly`, `flagsmith`, `posthog`, or env-var-flag patterns |

### Phase 3: Nine-Dimension Scoring

**Objective:** Score each dimension 0–3. Always explain the score in one plain sentence.

For each dimension, apply the rubric from `reference.md` §1. Scores:

- **0 — Not needed yet.** The app isn't big enough or risky enough to care.
- **1 — Would help.** You could ship without this, but you're leaving value on the table.
- **2 — Needed.** Running without this is a liability. Fix soon.
- **3 — Urgent.** This is biting you now or will the moment something goes wrong.

Dimensions:

| # | Dimension | Plain-language meaning |
|---|---|---|
| 1 | CI/CD | Does code get tested and shipped automatically? |
| 2 | Infrastructure as Code | Is the setup of servers/services written down as code rather than clicked together in a console? |
| 3 | Containers | Is the app packaged consistently so it runs the same everywhere? |
| 4 | Kubernetes | Are you running on Kubernetes? If yes, is it configured safely? If no, this dimension often scores 0. |
| 5 | Observability | If something goes wrong at 3am, can anyone tell what happened? |
| 6 | Release process | Can a change be shipped safely and rolled back if it breaks? |
| 7 | Security & Supply chain | Are dependencies locked, secrets protected, and the build pipeline trustworthy? |
| 8 | Reliability | Do you know what "working" means, get paged when it stops, and learn from outages? |
| 9 | Docs & Ops knowledge | If the main person on this left tomorrow, could the next one pick it up? |

For every dimension, write:

- **Score (0–3)** with the plain-language label
- **One-sentence reason** citing either a file signal or a questionnaire answer
- **What "good" looks like** for this project at its current stage

### Phase 4: Top-Three Action List

**Objective:** Cut through the nine dimensions and tell the user what to do next.

1. Take dimensions scored 2 or 3.
2. Rank by **(severity × leverage)** — leverage = how much downstream risk this single fix removes.
3. Keep the top three. No more. Non-experts get overwhelmed by long lists.
4. For each of the three, write:
   - **The action** in plain English ("Set up automatic tests that run every time you push code to GitHub.")
   - **Why it matters for YOUR app** (reference their specific context — framework, user count, hosting)
   - **Which skill in this plugin implements it** (`cicd-pipeline-audit`, `observability-audit`, etc.)
   - **Rough time estimate** (½ day / 1–2 days / a week / multi-week) — label as rough

### Phase 5: Reporting

**Objective:** Write `devops-needs-assessment.md` using `templates/output-template.md`.

Required sections in the report:

1. **TL;DR verdict** — one paragraph. "Your app needs DevOps support: moderately / urgently / not yet. The three things to fix first are …"
2. **What your app looks like right now** — captured context in plain English (no jargon dumps)
3. **Nine-dimension heatmap** — a small mermaid chart or a simple table with colour-coded scores
4. **Dimension-by-dimension breakdown** — per-dimension scoring with the plain-language reason
5. **Top three actions** — with time estimates and skill pointers
6. **When to revisit** — if you've scored 0–1 across the board, tell the user to re-run this in three months or after a notable growth event (10x users, first paying customer, first outage)
7. **Glossary** — a short glossary of terms that appeared in the report

Do NOT write a JSON sidecar — this skill is single-file output by design to stay approachable.

---

## Scoring & Verdict

Aggregate verdict is set from the dimension scores:

| Aggregate condition | Verdict |
|---|---|
| Any dimension scored 3 | **Urgent DevOps work required** |
| Two or more dimensions scored 2 | **DevOps work needed soon** |
| One dimension scored 2, rest ≤1 | **Targeted DevOps work recommended** |
| All dimensions ≤1 | **DevOps work not needed yet — revisit in 3 months** |

Put the verdict in the TL;DR and at the top of the report header.

---

## Important Principles

- **No jargon without definition.** "SLO" → "a target for how often the app works — e.g., 99.9% of requests succeed". "IaC" → "writing your infrastructure setup as code rather than clicking through a cloud console".
- **Be honest when something doesn't apply.** If the user isn't on Kubernetes and isn't planning to be, score Kubernetes 0 and say "not applicable — you're on Vercel". Don't invent a need.
- **Don't recommend everything at once.** Three actions, maximum. Pick the ones that unblock the most downstream value.
- **Respect the user's stage.** A pre-launch hobby project does not need SLOs. A profitable SaaS with 10k users with no monitoring absolutely does.
- **Never run code from the codebase.** This skill reads files only. It never executes `npm run`, `docker build`, `terraform plan`.
- **Point into the plugin.** Every top-three action names the specific DevOps skill that does that work in detail. This skill is the map; the others are the terrain.

---

## Edge Cases

1. **User gave a description, not a repo.** Run Phase 2 as "all signals unknown" and lean heavily on the questionnaire. Clearly state the limitation in the report header.
2. **User is on a PaaS (Vercel, Netlify, Heroku, Fly, Render).** IaC and Kubernetes usually score 0 — the PaaS handles it. CI/CD often scores low (the PaaS handles deploy, but not test automation). Observability often scores low because PaaS built-ins are shallow.
3. **User is a solo developer at idea stage.** Every dimension probably scores 0 or 1. Give a short, encouraging report: "you don't need DevOps yet — revisit when you have paying users or the first time something breaks in a way a user notices."
4. **User is at a company with a DevOps team already.** Ask whether this is a "check my team's work" run or a "greenfield" run. The recommendations are very different.
5. **Mixed stack (microservices).** Scope to a single service. Offer to rerun for other services after the first report.
6. **Static site / marketing site.** Most dimensions are N/A. Output is a one-page report saying so.
7. **User answers "I don't know" to most questions.** That's a valid answer. Score dimensions as "unknown — can't assess" and make "figure out how your app runs today" the first action.
