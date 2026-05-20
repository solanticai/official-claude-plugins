# Observability Audit — Reference

## §1 — Pillar Scoring Rubric

### Logs (0–5)

| Score | Condition |
|---|---|
| 0 | `console.log` / `print` only; no structure |
| 1 | Some structured logging but inconsistent; no correlation ID |
| 2 | JSON logs throughout; correlation ID in most paths |
| 3 | JSON logs; correlation ID everywhere; PII scrubbing via library/sink |
| 4 | 3 + sensible retention, level discipline, queryable backend |
| 5 | 4 + log sampling for high-volume endpoints; metric extraction from logs; audit trail for sensitive operations |

### Metrics (0–5)

| Score | Condition |
|---|---|
| 0 | No metrics emitted |
| 1 | Some ad-hoc counters; no histograms |
| 2 | RED metrics on HTTP boundary; USE on hosts |
| 3 | 2 + cardinality discipline + business-domain metrics |
| 4 | 3 + histogram buckets tuned + PromQL recording rules for common queries |
| 5 | 4 + exemplars + runtime-config label controls + metric cost budget |

### Traces (0–5)

| Score | Condition |
|---|---|
| 0 | No tracing |
| 1 | Tracer installed but few spans; no propagation across services |
| 2 | Spans at HTTP boundaries; propagation across sync calls |
| 3 | 2 + async context propagation (queue workers, background jobs) |
| 4 | 3 + tail-based sampling + exemplar links |
| 5 | 4 + schema-validated spans + trace-driven SLO computations |

### Alerts & Dashboards (0–5)

| Score | Condition |
|---|---|
| 0 | No alerts; no dashboards |
| 1 | Some alerts; CPU/memory only; no runbooks |
| 2 | Golden-signal dashboards per service; some symptom alerts |
| 3 | 2 + every paging alert has a runbook link |
| 4 | 3 + SLO burn-rate alerts multi-window |
| 5 | 4 + alert quality metrics (MTTR by alert, noisy-alert retirement cadence) |

---

## §2 — RED / USE cheatsheet

**RED (request-oriented):**
- **Rate** — requests per second
- **Errors** — errors per second (or error rate)
- **Duration** — latency distribution (p50, p95, p99)

**USE (resource-oriented):**
- **Utilisation** — % of capacity used
- **Saturation** — queue length / wait time
- **Errors** — operation failures (disk errors, network drops)

---

## §3 — Alert quality rubric

| Dimension | Good | Bad |
|---|---|---|
| Symptom vs cause | "Checkout p99 > 2s for 5min" | "CPU > 80%" |
| Paging threshold | Tied to SLO burn rate | Fixed number |
| Runbook link | Exists and resolves | Missing or 404 |
| Actionability | Responder knows what to do | Generic |
| Blast radius | Per-service; routed to owner | Fires to everyone |

---

## §4 — OpenTelemetry attribute cheatsheet

Required attributes (semantic conventions):

- **HTTP server span:** `http.method`, `http.route`, `http.status_code`, `http.target`
- **HTTP client span:** `http.method`, `http.url`, `http.status_code`
- **DB span:** `db.system`, `db.statement` (redacted), `db.operation`
- **Messaging span:** `messaging.system`, `messaging.destination`, `messaging.operation`

---

## §5 — Sampling strategies

| Strategy | When to use |
|---|---|
| Head-based, fixed rate | Low-volume services; simple setup |
| Head-based, per-operation | When you want high sampling for rare but important operations |
| Tail-based | High-volume services where you want errors + long traces sampled preferentially |
| Adaptive | Dynamic rate based on current error rate |
