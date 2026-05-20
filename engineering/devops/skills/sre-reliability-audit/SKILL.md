---
name: sre-reliability-audit
description: Assess Site Reliability maturity across five dimensions — SLOs/SLIs, runbooks, on-call, postmortems, game days — with per-dimension commentary and uplift path. Static, live (PagerDuty/Opsgenie), and runtime (game day) modes.
argument-hint: [repo-path]
allowed-tools: Read Grep Glob Write Edit Bash(bash:*) Agent
effort: medium
---

# SRE Reliability Audit

## When to use

Run this skill when the user mentions:
- SRE audit, reliability maturity
- SLO review, SLI definition, error-budget alerts
- Runbook audit, runbook quality
- On-call review, rotation, escalation
- Postmortem quality, blameless template
- Game day, chaos engineering at the organisational level

Narrative assessment — scores five dimensions 0–4 rather than emitting findings-with-IDs. SLOs and SLIs (defined, error budgets computed, burn-rate alerts, review cadence), runbook quality (one per paging alert, executable steps, freshness SLA), on-call readiness (rotation, escalation policy, handover template, fair schedule), postmortem culture (blameless template, action-item tracking, retrospective cadence), and game days (scoped chaos experiments, scheduled, learnings documented).

## Before You Start

1. **Determine operating mode.** `--live` reads from PagerDuty/Opsgenie/incident.io via API keys in env (`PD_API_KEY`, `OG_API_KEY`). `--runtime` runs a scoped game-day exercise — **requires non-prod target** and explicit opt-in via `--gameday-confirmed`.
2. **Discover artefacts.** Run the three discovery scripts — `scripts/find-runbooks.sh`, `scripts/find-slos.sh`, `scripts/find-postmortems.sh`.
3. **Load `.sre-ignore`** for suppression.

## User Context

$ARGUMENTS

Runbooks: !`bash "${CLAUDE_PLUGIN_ROOT}/skills/sre-reliability-audit/scripts/find-runbooks.sh"`

SLO files: !`bash "${CLAUDE_PLUGIN_ROOT}/skills/sre-reliability-audit/scripts/find-slos.sh"`

Postmortems: !`bash "${CLAUDE_PLUGIN_ROOT}/skills/sre-reliability-audit/scripts/find-postmortems.sh"`

---

## Audit Phases

### Phase 1: Artefact Discovery

Catalogue:

- SLO/SLI files (`slo.yaml`, `slis.yaml`, `error-budget.md`, OpenSLO)
- Runbook corpus (`runbooks/`, `docs/runbooks/`, `RUNBOOK.md`)
- On-call documentation (`on-call/`, `ONCALL.md`, schedules, escalation policies)
- Postmortem archive (`postmortems/`, `incidents/`)
- Game day logs (`gameday/`, `chaos/`, `game-day-*.md`)
- Alert rule files (cross-referenced from observability-audit if available)

### Phase 2: Dimension Scoring (narrative)

For each of five dimensions, produce a maturity-level narrative (0–4) and a short prose assessment.

#### D1. SLOs/SLIs (0–4)
- **0** — No SLOs defined.
- **1** — SLOs defined in a doc but no measurement.
- **2** — SLOs defined and measured; error budget implicit.
- **3** — 2 + multi-window multi-burn-rate alerts.
- **4** — 3 + quarterly review cadence documented; budget-driven release policy.

#### D2. Runbooks (0–4)
- **0** — No runbooks.
- **1** — A few runbooks exist but coverage is spotty.
- **2** — Every paging alert has a linked runbook with executable steps.
- **3** — 2 + freshness SLA (last-updated < 90 days); runbooks tested in game days.
- **4** — 3 + runbooks generate tickets on drift; auto-linked from alerts.

#### D3. On-call (0–4)
- **0** — Whoever notices fixes it.
- **1** — One person is oncall, informally.
- **2** — Rotation documented; escalation policy; handover notes.
- **3** — 2 + fair schedule; defined response time targets; compensation / time-in-lieu.
- **4** — 3 + oncall sustainability metrics (pages per shift, false-positive rate) tracked and managed.

#### D4. Postmortems (0–4)
- **0** — No postmortems written.
- **1** — Occasional postmortems; ad-hoc format.
- **2** — Blameless template used; action items tracked in a tracker.
- **3** — 2 + retrospective cadence; action items completed > 80%.
- **4** — 3 + postmortem library surfaced to onboarding; recurring patterns escalated to platform-level.

#### D5. Game days (0–4)
- **0** — No game days.
- **1** — Occasional ad-hoc chaos.
- **2** — Scheduled game days (quarterly); scoped to one service.
- **3** — 2 + learnings documented; runbook gaps closed as a result.
- **4** — 3 + automated chaos baseline tests on non-prod CI.

### Phase 3: Cross-dimension Synthesis

- Find the weakest dimension — this is the uplift-first target.
- Find evidence of strong coupling: strong SLOs but weak runbooks = alerts without response.
- Produce a one-paragraph narrative assessment.

### Phase 4: Live Mode (opt-in)

If `--live`:
- Pull incident history from PagerDuty / Opsgenie.
- Compute MTTR by service and trend over 90 days.
- Count Dependabot-style "acknowledge and ignore" on paging alerts.
- Check that on-call rotation is currently populated (nobody missing from the schedule).

### Phase 5: Game Day (opt-in)

If `--runtime --gameday-confirmed`:
- Pick a scoped failure: kill one pod, inject 500ms latency on one service, drop a DNS entry.
- Confirm non-prod context.
- Run the exercise for a pre-set duration (default 20 minutes).
- Measure detection time, response time, rollback time.
- Write `gameday-report.md` with the narrative, timeline, findings, and follow-up actions.

### Phase 6: Reporting

Render `sre-reliability-audit.md` and `sre-reliability-audit.json`. Write `gameday-report.md` if game day was run.

---

## Scoring

Five dimensions × 0–4 scale. Maturity aggregate:

| Avg score | Maturity tier |
|---|---|
| 3.5+ | Mature — maintain and iterate |
| 2.5–3.4 | Effective — tighten runbook + postmortem loops |
| 1.5–2.4 | Developing — focus on one dimension at a time |
| <1.5 | Nascent — start with SLOs and runbooks |

---

## Important Principles

- **An SLO that isn't alerted on is aspirational.** Maturity requires teeth.
- **A runbook that hasn't been tested in a game day probably doesn't work.** Test by running.
- **Oncall without rotation is burnout.** Flag single-person oncall as HIGH.
- **Postmortem = no-blame.** Any language in the archive that names individuals as causes is a tooling/culture problem. Flag it.
- **Game day without learnings recorded is theatre.** Require documented follow-ups.
- **Runtime game day requires explicit opt-in.** Never run against prod without `--i-really-mean-prod --gameday-confirmed`.
- **Australian English. DD/MM/YYYY. Markdown-first.**

---

## Edge Cases

1. **Small team (<5 engineers).** Single-person oncall may be unavoidable; recommend page-time constraints rather than rotation.
2. **No production workload.** Many dimensions N/A — report says so and recommends revisit after launch.
3. **Strong observability + weak SRE.** Instrumentation without process is common; recommend the process work.
4. **Many postmortems but nothing changed.** Action-item backlog is the red flag; flag as HIGH.
5. **Postmortems marked "private".** Can't audit without access. Record as limitation.
6. **On-call via external vendor (eg incident response firm).** Different audit shape; flag for custom assessment.
