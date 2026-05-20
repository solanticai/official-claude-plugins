# Index Strategy — Jobs-and-Quotes SaaS (Postgres 15 / Supabase)

**Date:** 20/05/2026

---

## Query Diagnoses

| Query (abbreviated) | Current plan issue | Filter cols | Sort cols | Join cols |
|--------------------|--------------------|-------------|-----------|-----------|
| `select * from jobs where org_id = $1 and status in ('draft','quoted') order by scheduled_at desc limit 50` | Seq scan on 2.1M rows; current jobs_org_id_idx exists but not used because of status + sort | org_id, status | scheduled_at desc | — |
| `select * from quotes where job_id = $1 order by version desc` | Index-only scan possible but missing covering index | job_id | version desc | — |
| `select count(*) from audit_log where org_id = $1 and at > now() - interval '7 days'` | Seq scan on 8.4M rows + time predicate | org_id, at | — | — |
| `select * from attachments where metadata @> '{"client_visible": true}'` | Seq scan; JSONB filter | metadata | — | — |
| `select * from users where lower(email) = lower($1)` | Seq scan (function on column blocks btree on email) | lower(email) | — | — |

---

## Recommended New Indexes

| # | Slow query | Recommended index | Type | DDL | Estimated impact |
|---|------------|-------------------|------|-----|-----------------|
| 1 | jobs list | `jobs_org_status_scheduled_idx` | Partial composite | `create index concurrently jobs_org_status_scheduled_idx on jobs (org_id, scheduled_at desc) where status in ('draft', 'quoted');` | 50–200× — index-only on common dashboard list |
| 2 | quotes by job | `quotes_job_version_idx` | Composite covering | `create index concurrently quotes_job_version_idx on quotes (job_id, version desc) include (total_aud, status);` | 5–10× (already fast; this enables index-only) |
| 3 | audit recent | `audit_log_org_at_brin_idx` | BRIN | `create index concurrently audit_log_org_at_brin_idx on audit_log using brin (at) with (pages_per_range = 32);` plus `create index concurrently audit_log_org_id_idx_v2 on audit_log (org_id, at desc) where at > '2026-01-01';` | 10–50× — BRIN for time-range + partial btree for recent |
| 4 | attachments JSONB | `attachments_metadata_gin_idx` | GIN with jsonb_path_ops | `create index concurrently attachments_metadata_gin_idx on attachments using gin (metadata jsonb_path_ops);` | 100–1000× on JSONB containment |
| 5 | case-insensitive email | `users_email_lower_idx` | Expression unique | `create unique index concurrently users_email_lower_idx on users (lower(email));` | 100× — enables index lookup |

---

## Indexes to Drop

| Index | Reason | DDL |
|-------|--------|-----|
| `jobs_owner_id_idx` | Single-col duplicate of new `jobs_org_owner_status_idx` (when added later) | Defer drop until composite usage confirmed |
| `audit_log_at_idx` (existing) | Will be superseded by BRIN + composite partial | `drop index concurrently audit_log_at_idx;` (after new indexes prove out) |
| `quotes_status_idx` | < 1% usage per pg_stat_user_indexes; status filter rare | `drop index concurrently quotes_status_idx;` |
| `users_email_idx` (case-sensitive on raw email) | Superseded by `users_email_lower_idx` | `drop index concurrently users_email_idx;` after week of dual-existence |

---

## Cost Summary

| New index | Est. size | Write-amplification on parent table |
|-----------|----------|-------------------------------------|
| `jobs_org_status_scheduled_idx` (partial) | ~80 MB | +3% on inserts only when status in (draft, quoted) |
| `quotes_job_version_idx` (covering) | ~120 MB | +4% on quote inserts/updates |
| `audit_log_org_at_brin_idx` | ~10 MB | +<1% on insert (BRIN is cheap to maintain) |
| `audit_log_org_id_idx_v2` (partial recent) | ~60 MB | +2% on insert; halves yearly |
| `attachments_metadata_gin_idx` | ~40 MB | +8% on attachment insert/update (GIN is slow to maintain) |
| `users_email_lower_idx` | ~15 MB | +3% on user insert (rare op) |

**Total added storage:** ~325 MB
**Total estimated write-overhead increase:** +3-4% average across hot tables; +8% on attachments (acceptable — low write volume)

---

## Sequencing — Order to Apply

1. **Drop unused indexes first:** `quotes_status_idx` and (after verification next week) `users_email_idx`
2. **Add partial indexes:** `jobs_org_status_scheduled_idx`, `audit_log_org_id_idx_v2` — smallest first
3. **Add BRIN:** `audit_log_org_at_brin_idx`
4. **Add GIN:** `attachments_metadata_gin_idx`
5. **Add expression:** `users_email_lower_idx` (verify no duplicate-email collision in existing data first)
6. **Add covering:** `quotes_job_version_idx`
7. **`analyze`** all affected tables
8. **Verify** each slow query with `explain (analyze, buffers)`

---

## Verification Queries

```sql
-- Confirm indexes are being used
explain (analyze, buffers)
select * from jobs where org_id = '<uuid>' and status in ('draft','quoted') order by scheduled_at desc limit 50;
-- Expect: Index Scan using jobs_org_status_scheduled_idx; not seq scan

-- After 1 week, check usage
select
  schemaname, tablename, indexname,
  idx_scan, idx_tup_read, idx_tup_fetch,
  pg_size_pretty(pg_relation_size(indexrelid)) as size
from pg_stat_user_indexes
where indexrelid in (
  'jobs_org_status_scheduled_idx'::regclass,
  'quotes_job_version_idx'::regclass,
  'audit_log_org_at_brin_idx'::regclass,
  'audit_log_org_id_idx_v2'::regclass,
  'attachments_metadata_gin_idx'::regclass,
  'users_email_lower_idx'::regclass
)
order by idx_scan desc;
-- Each new index should have idx_scan > 0 within 7 days; if not, reconsider
```
