# Release Readiness — Reference

## §1 — Destructive DDL Patterns

| SQL pattern | Risk | Mitigation |
|---|---|---|
| `DROP TABLE t` | Data loss | Archive and keep for 30 days; never DROP in same release as the code removal |
| `DROP COLUMN c` | Data loss | Expand-contract: stop reading, stop writing, then drop in a later release |
| `ALTER COLUMN TYPE` (narrowing) | Truncation risk | Add new column; dual-write; backfill; swap; drop old |
| `RENAME TABLE` / `RENAME COLUMN` | Breaks all readers mid-deploy | Add new name (view / generated column); migrate readers; remove old |
| `ADD COLUMN NOT NULL` (no default) | Fails on existing rows | ADD nullable → backfill → SET NOT NULL |
| `ADD CHECK` that existing rows violate | Migration fails on apply | Backfill rows to comply first |
| `CREATE INDEX` (non-concurrent) | Locks writes | Use `CREATE INDEX CONCURRENTLY` |
| `ALTER TABLE` on huge table | Long lock | `ALTER` with `ONLY` and batch; or use online-migration tool |
| `TRUNCATE` | Data loss + extent release | Use DELETE with batches if rollback matters |

## §2 — Change Shape → Deploy Strategy

| Change shape | Recommended strategy |
|---|---|
| Pure additive code | Rolling |
| Backwards-incompatible API | Expand/contract over two releases |
| DB destructive migration | Expand/contract + canary-on-migration-step |
| Auth / identity change | Blue-green + feature flag |
| Payments / money-moving | Canary with slow ramp (5% → 25% → 100% over 1h) + instant rollback |
| Dependency upgrade | Blue-green |
| Config-only change | Rolling, with config reload test |
| Static asset | Rolling, with CDN invalidation verified |

## §3 — Rollback Class Hierarchy

| Class | Description |
|---|---|
| Trivial | `git revert` + redeploy; state untouched |
| Feature-flag | Toggle off; no redeploy needed |
| Config rollback | Revert config file + restart |
| Data-compatible code rollback | Roll back code, keep new schema; verify old code works against new schema |
| Forward-only | No clean rollback; recovery = forward-fix or restore from backup |

## §4 — Smoke Test Battery

Minimum checklist for canary:

- [ ] Healthz endpoint 200
- [ ] Root endpoint 200
- [ ] Version endpoint matches
- [ ] Auth endpoint rejects anonymous
- [ ] Create + read round-trip on a test record (non-destructive)
- [ ] Trace ID propagated into logs
- [ ] Error rate < 2× baseline after 5 minutes
- [ ] p95 latency < 1.5× baseline

## §5 — Verdict Matrix

| Any CRITICAL? | Any unmitigated HIGH? | Monitoring gap? | Canary failure? | Verdict |
|---|---|---|---|---|
| Yes | — | — | — | NO-GO |
| No | Yes | — | — | NO-GO |
| No | No | Yes | — | GO WITH CAVEATS |
| No | No | No | Yes | NO-GO |
| No | No | No | No/N-A | GO |
