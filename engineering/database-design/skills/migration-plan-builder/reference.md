# Migration Plan Builder — Reference Material

## Postgres Lock-Impact Matrix

For DDL operations on production tables:

| Operation | Lock | Blocks reads? | Blocks writes? | Duration |
|-----------|------|---------------|----------------|----------|
| `ALTER TABLE ADD COLUMN` (nullable, no default) | ACCESS EXCLUSIVE | momentary | momentary | < 1 second |
| `ALTER TABLE ADD COLUMN` (with default — Postgres 11+) | ACCESS EXCLUSIVE | momentary | momentary | < 1 second |
| `ALTER TABLE ADD COLUMN` (with default — Postgres < 11) | ACCESS EXCLUSIVE | YES — until rewrite done | YES | Minutes to hours on large table |
| `ALTER COLUMN SET NOT NULL` | ACCESS EXCLUSIVE | YES — full table scan to verify | YES | Minutes |
| `ALTER COLUMN SET NOT NULL` (with NOT VALID then VALIDATE) | SHARE UPDATE EXCLUSIVE | No | No | Slow but non-blocking |
| `ALTER COLUMN TYPE` | ACCESS EXCLUSIVE | YES — rewrite | YES | Minutes-hours |
| `ALTER COLUMN DROP DEFAULT` | ACCESS EXCLUSIVE | momentary | momentary | < 1 second |
| `ALTER TABLE DROP COLUMN` | ACCESS EXCLUSIVE | momentary | momentary | < 1 second (logical drop) |
| `CREATE INDEX` (no CONCURRENTLY) | SHARE | No | YES | Minutes |
| `CREATE INDEX CONCURRENTLY` | SHARE UPDATE EXCLUSIVE | No | No (only sup) | Slow but non-blocking |
| `DROP INDEX` | ACCESS EXCLUSIVE | momentary | momentary | < 1 second |
| `DROP INDEX CONCURRENTLY` | SHARE UPDATE EXCLUSIVE | No | No | Slow but non-blocking |
| `ALTER TABLE ADD FOREIGN KEY` | SHARE ROW EXCLUSIVE | No | YES briefly | Validation can be long |
| `ALTER TABLE ADD FOREIGN KEY NOT VALID` | SHARE ROW EXCLUSIVE | No | YES briefly | Fast — no validation |
| `ALTER TABLE VALIDATE CONSTRAINT` | SHARE UPDATE EXCLUSIVE | No | No | Slow but non-blocking |
| `CLUSTER` | ACCESS EXCLUSIVE | YES | YES | Long — avoid in prod |
| `VACUUM FULL` | ACCESS EXCLUSIVE | YES | YES | Long — avoid in prod |
| `TRUNCATE` | ACCESS EXCLUSIVE | momentary | momentary | < 1 second |

---

## Replication-Lag Thresholds

| Metric | Healthy | Warning | Critical |
|--------|---------|---------|----------|
| Read-replica lag | < 1 second | 1–10s | > 10s — pause migrations |
| WAL generation | normal | 2× normal | 5× normal — chunk further |
| Logical replication slot lag | < 1MB | 100MB | 1GB — pause |

---

## Chunked Backfill Pattern

```sql
do $$
declare
  batch_size int := {{1k-10k}};
  rows_updated int;
  sleep_secs numeric := {{0.1-1.0}};
begin
  loop
    update {{table}}
    set {{new_col}} = {{expr}}
    where {{new_col}} is null
      and id in (
        select id from {{table}}
        where {{new_col}} is null
        order by id
        limit batch_size
      );
    get diagnostics rows_updated = row_count;
    if rows_updated = 0 then exit; end if;
    perform pg_sleep(sleep_secs);
  end loop;
end $$;
```

Batch size: 1k for high-write tables, up to 10k for read-mostly. Sleep: 100ms baseline; 500ms+ if replication lag spikes.

---

## Strangler-Fig Migration Pattern (Fowler)

For big architectural changes:

1. **New surface** (new table / new column / new endpoint) — additive
2. **Dual-write** — app writes to both old and new
3. **Read shift** — app reads from new; falls back to old if new is null
4. **Verification** — shadow query confirms parity
5. **Drop old** — once verification stable for observation window

---

## App-Deploy Gating Rules

| Schema change | App-deploy direction |
|--------------|---------------------|
| Add nullable column | Schema first; app later |
| Drop column | App stops writing first; schema later (after observation) |
| Rename column | Schema = view alias first; app shifts; schema drops alias |
| Type change | Add new col; backfill; app dual-writes; switch reads; drop old |
| Add NOT NULL | Backfill default; app starts populating; alter; (optionally drop default) |
| Add FK | Add NOT VALID first; backfill / clean orphans; VALIDATE |

---

## Rollback-Safe Migration Checklist

- ☐ Each stage has a documented rollback procedure
- ☐ Rollback procedure tested in staging
- ☐ Backup taken before non-trivial stages
- ☐ Replication lag monitor in place during backfill
- ☐ Alert on replication-lag breach
- ☐ Feature flag for app cutover (instant rollback)
- ☐ Observation window > 1 weekly batch cycle
- ☐ DBA / SRE notified of deploy window
