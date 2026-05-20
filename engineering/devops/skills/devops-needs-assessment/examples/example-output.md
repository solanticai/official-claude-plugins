# DevOps Needs Assessment — Tasklet

**Assessed:** 21/04/2026
**Verdict:** Needed soon
**Stage:** Early users

---

## TL;DR

Tasklet is a Next.js SaaS with about 400 paying customers running on Vercel with a Supabase backend. The app itself is stable, but there's no automated testing on push, no structured logs, and no runbook — when something breaks, diagnosis takes hours because nothing is instrumented. You don't need infrastructure-as-code (Vercel handles that) or Kubernetes (not applicable), so the work is focused: get CI tests running, wire up proper logging, and write down how to recover from the three most likely failure modes.

**The three things to fix first:**

1. Set up automated tests that run on every push — *1–2 days*
2. Replace `console.log` with structured logging and pipe it somewhere you can search — *1 day*
3. Write a short runbook for the three things most likely to go wrong — *½ day*

---

## What your app looks like right now

- **What it is:** A team task manager with real-time collaboration.
- **Built with:** TypeScript, Next.js 15, Supabase (Postgres + Auth).
- **Where it runs:** Vercel (edge). Database on Supabase.
- **Users today:** 400 paying customers, growing ~5% month-on-month.
- **How a change gets shipped today:** You push to `main` and Vercel auto-deploys.
- **Outage history:** Three incidents in the last six months. Longest was 90 minutes because it took ages to figure out where the error was coming from.

---

## Nine-dimension heatmap

| # | Dimension | Score | Label |
|---|---|---|---|
| 1 | CI/CD | 2 | Needed |
| 2 | Infrastructure as Code | 0 | Not needed yet (Vercel) |
| 3 | Containers | 0 | Not needed yet (Vercel) |
| 4 | Kubernetes | 0 | Not applicable |
| 5 | Observability | 3 | Urgent |
| 6 | Release process | 1 | Would help |
| 7 | Security & Supply chain | 2 | Needed |
| 8 | Reliability | 2 | Needed |
| 9 | Docs & Ops knowledge | 2 | Needed |

**Aggregate:** 12 / 27

---

## Dimension breakdown

### 1. CI/CD — 2 (Needed)

`.github/workflows/` is empty — every push goes straight to Vercel without running tests.

**What "good" looks like for your app right now:** a single GitHub Actions workflow that runs `npm test` and `tsc --noEmit` on every PR, blocking merges until they pass.

### 2. Infrastructure as Code — 0 (Not needed yet)

Vercel manages the runtime; Supabase manages the database. There's no custom infra to codify.

**What "good" looks like for your app right now:** nothing. Revisit if you ever leave Vercel or add a second cloud.

### 3. Containers — 0 (Not needed yet)

No Dockerfile; Vercel handles packaging.

**What "good" looks like for your app right now:** nothing.

### 4. Kubernetes — 0 (Not applicable)

You're not on Kubernetes.

**What "good" looks like for your app right now:** nothing.

### 5. Observability — 3 (Urgent)

The codebase has 87 `console.log` calls and no structured logger. No metrics, no traces. An outage last month took 90 minutes to diagnose because there was no way to search logs by user.

**What "good" looks like for your app right now:** a structured logger (`pino`) in every API route, shipped to Axiom or Datadog, plus error tracking via Sentry.

### 6. Release process — 1 (Would help)

Vercel's preview deployments and instant rollback do most of the work. Migrations go via Supabase and have broken prod once.

**What "good" looks like for your app right now:** a short pre-deploy checklist for migrations, and turning on Vercel's "promote to production" manual gate.

### 7. Security & Supply chain — 2 (Needed)

`package-lock.json` is committed. No Dependabot, no `.env` rules in CI. One secret leaked last year via a screenshot in a GitHub issue.

**What "good" looks like for your app right now:** enable Dependabot grouped weekly, add secret scanning, require PR reviews on `main`.

### 8. Reliability — 2 (Needed)

You charge customers monthly but have no internal uptime target, no alerts, no on-call — outages are noticed via support tickets.

**What "good" looks like for your app right now:** one SLO (e.g., "99.5% of API requests succeed in under 2 seconds"), one alert on that SLO, one phone number that gets paged.

### 9. Docs & Ops knowledge — 2 (Needed)

`README.md` covers local setup but there's nothing on how to recover the app if Supabase has a partial outage or if the Next.js build breaks production.

**What "good" looks like for your app right now:** a one-page runbook per "thing most likely to break" — three documents, total maybe three hours to write.

---

## Top three actions

### 1. Wire up automated testing in CI

**Why this matters for your app:** you're shipping to 400 paying customers every push, with no safety net. The first PR that breaks production will be expensive.

**Run next:** `/devops:cicd-pipeline-audit`

**Rough effort:** 1–2 days

### 2. Add structured logging and error tracking

**Why this matters for your app:** your last outage cost 90 minutes of diagnosis you didn't have to pay. Replacing `console.log` with `pino` + Sentry will cut that to minutes.

**Run next:** `/devops:observability-audit`

**Rough effort:** 1 day

### 3. Write three runbooks

**Why this matters for your app:** the knowledge of how to recover from common failures lives in your head. When you're on holiday, nobody else can help.

**Run next:** `/devops:sre-reliability-audit`

**Rough effort:** ½ day

---

## When to revisit

Re-run this skill after your next outage, or in 3 months — whichever comes first. If you cross 1,000 paying customers, re-run immediately: the Reliability score needs a new target.

---

## Glossary

| Term | Plain-language meaning |
|---|---|
| CI/CD | "Continuous Integration / Continuous Delivery" — automation that runs tests and ships code without a human doing it by hand. |
| SLO | Service Level Objective — a written target for how often the app works, e.g., 99.5% of requests succeed. |
| IaC | Infrastructure as Code — writing your server / database / network setup as text files instead of clicking through a console. |
| Runbook | A short document that tells whoever is on call exactly what to do when a specific alert fires. |
| Structured logging | Logs as JSON (with fields like `user_id`, `request_id`) rather than free-form text — so you can search them. |

---

*Generated by `devops:devops-needs-assessment` — Anthril DevOps plugin*
