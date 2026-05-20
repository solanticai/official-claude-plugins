# Migration Plan — Split `users.full_name` into `users.first_name` + `users.last_name`

**Date:** 20/05/2026
**Table(s) affected:** users (4.2M rows)
**Estimated total duration:** 10 days (incl. observation window)

---

## Change Summary

- **From:** Single `full_name text` column with free-text content
- **To:** `first_name text` + `last_name text` (both nullable initially) plus a `full_name` view alias for backward compatibility, eventually removed
- **Why:** Search by surname is impossible against the free-text column; multiple feature requests blocked by this; safer to do it once, deliberately, than 4 quick fixes

---

## Stages

| # | Stage | Duration | Reversible? | Dependencies |
|---|-------|----------|-------------|--------------|
| 1 | Additive: add first_name + last_name nullable | < 1 min | Yes (DROP cols) | None |
| 2 | Backfill: split full_name with conservative heuristic | ~30 min (chunked) | Yes (TRUNCATE new cols) | Stage 1 complete |
| 3 | Dual-write: app writes to all three columns | 3 days | Yes (revert app) | App v3.4 deploy |
| 4 | Cutover: app reads from first/last; full_name becomes computed view | < 5 min | Yes (revert app + restore col) | App v3.5 + verification |
| 5 | Cleanup: drop full_name column | < 1 min | No | 7-day observation pass |

---

## Per-Stage Spec

### Stage 1 — Additive

**DDL:**
```sql
alter table users add column first_name text;
alter table users add column last_name text;
```

**Lock taken:** ACCESS EXCLUSIVE briefly during ALTER (no rewrite — column added nullable in metadata only; instant)
**Pre-stage check:** Confirm read replica lag < 1s; confirm app doesn't write to `users.first_name` or `users.last_name`
**During:** monitor pg_stat_activity for blocked queries
**Post-stage gate:** `\d users` shows new columns; existing queries unaffected
**Rollback:** `alter table users drop column first_name, drop column last_name;`

### Stage 2 — Backfill

```sql
-- Heuristic split: last word = last_name; remainder = first_name
-- Edge cases: empty / single-token names → first_name = full; last_name = null
do $$
declare
  batch_size int := 5000;
  rows_updated int;
begin
  loop
    update users
    set
      first_name = case
        when position(' ' in trim(full_name)) > 0
          then regexp_replace(trim(full_name), '\s+\S+$', '')
        else trim(full_name)
      end,
      last_name = case
        when position(' ' in trim(full_name)) > 0
          then regexp_replace(trim(full_name), '^.*\s+', '')
        else null
      end
    where first_name is null
      and full_name is not null
      and id in (
        select id from users
        where first_name is null and full_name is not null
        order by id
        limit batch_size
      );
    get diagnostics rows_updated = row_count;
    if rows_updated = 0 then exit; end if;
    perform pg_sleep(0.2);
  end loop;
end $$;
```

**Pre-stage:** baseline `select count(*) from users where first_name is null;` (expect 4.2M)
**During:** monitor backfill progress; watch read-replica lag (should stay < 5s)
**Post-stage gate:** `select count(*) from users where first_name is null and full_name is not null;` returns 0
**Rollback:** `update users set first_name = null, last_name = null;` (chunked similarly)

### Stage 3 — Dual-write

App v3.4 writes to **all three columns** for any user create/update:
- Continues to write `full_name`
- Also writes `first_name` + `last_name`

**Verification (shadow query, run hourly):**
```sql
select count(*)
from users
where full_name != trim(coalesce(first_name, '') || ' ' || coalesce(last_name, ''))
  and updated_at > now() - interval '1 hour';
-- Expect: 0 mismatches in newly-written rows
```

If non-zero, **abort the cutover**.

### Stage 4 — Cutover

```sql
-- Add a backward-compat computed column for any legacy clients
create or replace view users_legacy as
select id, email, trim(coalesce(first_name, '') || ' ' || coalesce(last_name, '')) as full_name, *
from users;
```

App v3.5 reads from `first_name` / `last_name` directly; legacy code via view.

**Verification:** `select count(*) from users where first_name is null;` ≈ near-zero (only single-token names that have no clean split)

### Stage 5 — Cleanup (after 7 days observation)

```sql
alter table users drop column full_name;
drop view users_legacy;
```

---

## App Deploy Ordering

| Order | Deploy | What it does |
|-------|--------|-------------|
| 1 | Schema stage 1 (run via Supabase CLI migration) | Columns exist |
| 2 | App v3.4 | Begin dual-write |
| 3 | Schema stage 2 (backfill, off-peak) | Populate existing rows |
| 4 | App v3.5 | Read from new columns; views in place |
| 5 | Schema stage 5 (after 7 days) | Drop old |

---

## DB Reviewer — Risk Assessment

### Verdict: Approve-with-changes

### Critical issues

1. **The `regexp_replace` split is naive.** Names like "Mary-Anne O'Brien-Smith" or "Anh Nguyen Văn" (Vietnamese 3-token names where surname is first) will break. The heuristic produces wrong data ~3–5% of the time at AU population scale (multicultural). The backfill should produce *plausible defaults* and the **app should prompt users to confirm/edit on next login**, with audit logging.

### Important caveats

2. **`pg_sleep(0.2)` in the backfill** is fine for a single-region setup but will increase backfill duration to ~40 minutes. If you have read-replica lag spikes, consider 0.5s. The trade-off: 30 vs 100 min.
3. **Observation window of 7 days is aggressive.** If your app has weekly batch jobs (e.g. monthly invoicing on day 1), the dependent code may not run within the window. Recommend 14 days.

### Optional improvements

1. Add an `original_full_name` text column (preserved indefinitely or for 90 days) — if the split is wrong, you can recover.
2. Add an event in your application metrics for "user edited their first/last name in profile" so you can measure data-quality improvement post-launch.

### Lock impact summary

| Operation | Lock taken | Blocks reads? | Blocks writes? |
|-----------|-----------|---------------|----------------|
| `alter table add column` (nullable, no default) | ACCESS EXCLUSIVE momentarily | No (sub-second) | Yes briefly |
| Chunked UPDATE (5k rows at a time) | ROW EXCLUSIVE | No | Only the rows being updated |
| `alter table drop column` | ACCESS EXCLUSIVE | Briefly | Briefly |
| `create or replace view` | ACCESS EXCLUSIVE on the view name | No | No (separate object) |

### Suggested rollout

1. Schema stage 1 in next deploy window
2. Backfill scheduled for Saturday off-peak (lowest replication concern)
3. App v3.4 deploy with dual-write — monitor shadow query daily
4. App v3.5 cutover Mon 03/06; 14-day observation
5. Cleanup Mon 17/06

---

## Sign-off Checklist

- ☐ Each stage tested against staging snapshot of production (4.2M rows)
- ☐ Rollback procedure tested for each stage
- ☐ Shadow comparison query saved as a daily cron alert
- ☐ App deploys coordinated with platform team
- ☐ Off-peak backfill window booked (Sat 25/05 from 22:00 AEST)
- ☐ `original_full_name` preserve-column added (DB reviewer suggestion)
- ☐ Observation window extended to 14 days (DB reviewer)
- ☐ Final sign-off: {Engineering Lead} + {DBA}
