# SRE Reliability Audit — Reference

## §1 — SLO Library (cheatsheet)

### Request-based SLIs

| Service type | SLI | Typical SLO |
|---|---|---|
| HTTP API | `% of requests that succeed (status < 500)` | 99.5 – 99.95% |
| HTTP API | `% of requests faster than 300ms` | 95 – 99% |
| Queue worker | `% of jobs that complete within SLA` | 99 – 99.9% |
| Batch job | `% of scheduled runs that complete` | 95 – 99% |
| Static asset | `% of edge requests with cache hit` | 95 – 99% |

### Error budget formula

`error_budget_30d = (1 - SLO) × total_requests_30d`

Burn rate: rate at which budget is being consumed relative to elapsed time.
- 1× burn = budget lasts a month
- 2× burn = budget lasts 2 weeks (page at 1-hour window if this persists)

## §2 — Runbook Template Elements

Every good runbook has:

1. **Alert name + link back to the rule**
2. **What the user sees** (symptom)
3. **First action** (one command to confirm / mitigate)
4. **Decision tree** (common causes)
5. **Mitigation steps** (with rollback)
6. **Escalation path** (who to wake up, when)
7. **Last updated** date + author

## §3 — On-call Maturity Indicators

| Indicator | Mature |
|---|---|
| Rotation period | 1 week on, 3+ weeks off |
| Max consecutive weeks oncall | 1 |
| Secondary / escalation | Named person, not "whoever's around" |
| Response time target | P1 < 15 min, P2 < 1 hour |
| Handover cadence | Monday morning sync |
| Compensation / TOIL | Documented |

## §4 — Postmortem Template

- Incident name
- Date / duration
- Summary
- Impact (users affected, revenue, etc.)
- Timeline (with timestamps)
- Root cause (technical)
- Contributing factors (process, tooling, communication)
- What went well
- What went poorly
- Action items (with owners and dates)
- Follow-up review date

## §5 — Game Day Exercise Ideas (safe on non-prod)

| Exercise | Target | Teaches |
|---|---|---|
| Kill a pod | Deployment | Rolling recovery, PDB correctness |
| Inject 500ms latency | Service-to-service | Timeout handling, backoff |
| DNS failure | Upstream | Retry / circuit breaker |
| Disk fill | Node | Pod eviction, alerting |
| Expired certificate | LB / TLS | Cert rotation automation |
| Oncall person unreachable | Schedule | Escalation correctness |

## §6 — Maturity Tier Labels

| Tier | Label |
|---|---|
| 0 | None |
| 1 | Ad-hoc |
| 2 | Defined |
| 3 | Measured |
| 4 | Optimising |
