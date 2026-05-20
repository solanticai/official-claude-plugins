---
name: observability-audit
description: Score observability across the four pillars — logs, metrics, traces, and alerts/dashboards — with per-service coverage heatmap. Cross-cutting synthesis. Static, live (Prometheus/Grafana/OTel/Datadog), and runtime (synthetic alert) modes.
argument-hint: [repo-path]
allowed-tools: Read Grep Glob Write Edit Bash(bash:*) Agent
effort: high
---

# Observability Audit

## When to use

Run this skill when the user mentions:
- Observability audit, logging review
- Metrics coverage, tracing coverage, alert quality, dashboard review
- OpenTelemetry, Prometheus, Grafana, Datadog, New Relic

Scores four pillars 0–5: logs (structured, correlation IDs, PII scrubbing, level discipline), metrics (RED/USE coverage, cardinality discipline, histogram buckets), traces (service-boundary spans, attribute conventions, sampling), and alerts/dashboards (paging vs non-paging, runbook links, symptom-based alerts, golden-signal dashboards, SLO burn-rate panels). Cross-cutting — does not spawn parallel sub-agents.

## Before You Start

1. **Determine operating mode.** `--live` requires Prometheus / Grafana / OTel / Datadog endpoint config and read-only API keys via env (`PROM_URL`, `GRAFANA_URL`, `GRAFANA_API_KEY`, `DD_API_KEY`). `--runtime` fires a synthetic alert — **non-prod only unless `--i-really-mean-prod`**.
2. **Find observability surface.** Run the four per-pillar discovery scripts — `scripts/scan-logging.sh`, `scripts/scan-metrics.sh`, `scripts/scan-traces.sh`, and `scripts/find-dashboards.sh`. Each emits a labelled inventory for its pillar.
3. **Load `.obs-ignore`** for suppression rules.

## User Context

$ARGUMENTS

Logging surface: !`bash "${CLAUDE_PLUGIN_ROOT}/skills/observability-audit/scripts/scan-logging.sh"`

Metrics surface: !`bash "${CLAUDE_PLUGIN_ROOT}/skills/observability-audit/scripts/scan-metrics.sh"`

Tracing surface: !`bash "${CLAUDE_PLUGIN_ROOT}/skills/observability-audit/scripts/scan-traces.sh"`

Dashboards & alerts: !`bash "${CLAUDE_PLUGIN_ROOT}/skills/observability-audit/scripts/find-dashboards.sh"`

Live mode env: !`if [ -n "$PROM_URL" ]; then echo prom-ready; else echo prom-unset; fi` · !`if [ -n "$GRAFANA_URL" ]; then echo grafana-ready; else echo grafana-unset; fi`

---

## Audit Phases

### Phase 1: Surface Discovery

Catalogue:

- **Logs** — library imports (`pino`, `winston`, `bunyan`, `zap`, `logrus`, `zerolog`, `structlog`, `slog`); log shippers (`filebeat.yml`, `vector.toml`, `fluent-bit.conf`); log-sink config.
- **Metrics** — Prometheus scrape config, rule files, exporter deployments; metric emission sites (grep for `counter`, `histogram`, `gauge` instantiations in source).
- **Traces** — OpenTelemetry SDK init, tracer setup, Sentry init, Datadog APM init; sampler config.
- **Dashboards** — Grafana JSON exports under `grafana/`, Datadog dashboard JSON, any `dashboards/` directory.
- **Alerts** — Prometheus rule files (`*.rules.yml`), Alertmanager config, Datadog monitors (JSON), PagerDuty service config.

### Phase 2: Per-Pillar Scoring

For each pillar, score 0–5 using `reference.md` §1 and emit findings.

#### Logs (0–5)
- Structured format (JSON) throughout
- Correlation ID / trace ID propagated into every log line
- Log level discipline (INFO for normal, WARN/ERROR appropriately)
- PII scrubbing at source or sink
- Retention + rotation policy sane
- Search / query tooling in place (Loki / Axiom / Datadog / CloudWatch Insights)

#### Metrics (0–5)
- RED metrics (Rate, Errors, Duration) per service endpoint
- USE metrics (Utilisation, Saturation, Errors) for host/container resources
- Cardinality discipline (no high-cardinality labels like `user_id`, `request_id` as labels)
- Histogram buckets sensible (not default 10-bucket on a 200ms service)
- Business-domain metrics (not just infra)

#### Traces (0–5)
- Spans at every service boundary (HTTP in, HTTP out, DB query)
- Consistent attribute conventions (OTel semantic conventions)
- Trace context propagation across async boundaries (queues, workers)
- Sampling strategy explicit (head-based vs tail-based, rate chosen)
- Exemplars link metrics → traces

#### Alerts & Dashboards (0–5)
- Paging alerts separate from non-paging (e.g., warning-only)
- Runbook link in every paging alert
- Symptom-based alerts (user-facing outage) not cause-based (CPU at 80%)
- Golden signals (rate, error, duration, saturation) dashboard per service
- SLO burn-rate alerts (multi-window, multi-burn-rate)
- Dashboard versioning (Grafana-as-code via JSON in repo)

### Phase 3: Cross-Pillar Gap Analysis

- Which services have all four pillars? Which have none?
- Heatmap: services × pillars.
- Identify the **weakest link** — typically traces or SLO-based alerts.

### Phase 4: Live Mode (opt-in)

If `--live`:
- Query Prometheus for 24h metric delivery stats per service.
- List recently firing alerts via Alertmanager/Datadog.
- Inspect Grafana dashboards for last-edited dates (stale dashboards > 180 days flagged).
- Query Loki / Axiom / Datadog Logs for a sample log line per service — confirm it's actually being ingested.

### Phase 5: Runtime Testing (opt-in)

If `--runtime` and non-prod confirmed:
- Fire a synthetic alert: push a metric that violates a known threshold or send a crafted log line that matches a log-based alert.
- Trace its path: alert rule fires → Alertmanager / Datadog routes → notification channel (Slack / PagerDuty sandbox) → user receives it.
- Record latency at each hop. Confirm runbook link resolves to a non-404 page.
- Write `synthetic-alert-trace.md` with the hop-by-hop trace.

### Phase 6: Reporting

Write `observability-audit.md` + `observability-audit.json` (+ `synthetic-alert-trace.md` in runtime mode). Report includes per-pillar scores, service × pillar heatmap, gap list, prioritised action list.

---

## Scoring

Pillar weights equal: logs 25, metrics 25, traces 25, alerts/dashboards 25. Each pillar scored 0–5 → aggregate = (sum / 20) × 100.

| Total | Verdict |
|---|---|
| 90+ | Observability mature |
| 70–89 | Observability good; gaps exist |
| 50–69 | Observability patchy; significant uplift needed |
| <50 | Observability blind — urgent |

---

## Important Principles

- **Unstructured logs are a tax.** Text logs are searchable with grep only; JSON logs are queryable.
- **Cardinality kills metrics backends.** `user_id` as a Prometheus label will destroy a retention budget.
- **Alert fatigue is a reliability risk in itself.** If every alert pages, none do.
- **A runbook link that 404s is worse than no link.** Runtime testing catches this.
- **Default sampling on traces is usually wrong.** 100% is too much; 0.01% hides issues. Tail-based sampling is often the answer.
- **SLO burn-rate alerts replace CPU alerts.** Page on user-visible symptoms, not on substrate metrics.
- **Australian English. DD/MM/YYYY. Markdown-first.**

---

## Edge Cases

1. **Monolithic app with no service decomposition.** Use endpoint-level decomposition instead of service-level.
2. **Serverless (Lambda / Cloud Functions).** Traces via X-Ray / Cloud Trace; metrics via platform-native. Cardinality limits different.
3. **No metrics backend at all, only logs.** Score metrics = 0. Don't fabricate.
4. **Only vendor observability (Datadog/New Relic), nothing in source.** Check agent config + Datadog API inventory in live mode.
5. **Alerts exist but nobody gets paged.** Flag as HIGH — untested alerts degrade.
6. **Grafana dashboards not in Git.** Flag as MEDIUM — dashboard drift is a reliability risk.
