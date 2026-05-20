# Migration Plan — {{change_summary}}

**Date:** {{date_dd_mm_yyyy}}
**Table(s) affected:** {{tables}}
**Estimated total duration:** {{n}} days

---

## Change Summary

- **From:** {{current_state}}
- **To:** {{desired_state}}
- **Why:** {{rationale}}

---

## Stages

| # | Stage | Duration | Reversible? | Dependencies |
|---|-------|----------|-------------|--------------|
| 1 | Additive | < 5 min | Yes (DROP) | None |
| 2 | Backfill | {{hrs}} | Yes (TRUNCATE new col) | Stage 1 complete |
| 3 | Dual-write | {{days}} | Yes (re-deploy old code) | App deploy v1.X |
| 4 | Cutover | < 5 min | Yes (revert app deploy) | App deploy v1.Y verified |
| 5 | Cleanup | < 5 min | No | Observation period passed |

---

## Per-Stage Spec

### Stage 1 — Additive

**DDL:**
```sql
{{ddl}}
```

**Lock taken:** {{lock_type}}
**Pre-stage check:** {{check}}
**During:** {{monitor}}
**Post-stage gate:** {{gate}}
**Rollback:** {{rollback}}

### Stage 2 — Backfill

```sql
-- Chunked, sleep between batches
do $$
declare
  batch_size int := 5000;
  rows_remaining int;
begin
  loop
    update {{table}}
    set {{new_col}} = {{expr}}
    where {{new_col}} is null
      and id in (select id from {{table}} where {{new_col}} is null limit batch_size);
    get diagnostics rows_remaining = row_count;
    if rows_remaining = 0 then exit; end if;
    perform pg_sleep(0.1);  -- 100ms breath
  end loop;
end $$;
```

**Pre-stage:** {{check}}
**During:** {{monitor}}
**Post-stage gate:** {{gate}}
**Rollback:** TRUNCATE new column / drop new column

### Stage 3 — Dual-write

App now writes to both old and new column.

**App version:** {{version}}
**Verification:** {{shadow comparison query}}

### Stage 4 — Cutover

```sql
{{cutover_ddl}}
```

App deploys to read from new column.

### Stage 5 — Cleanup (after {{n}}-day observation)

```sql
{{drop_old}}
```

---

## App Deploy Ordering

| Order | Deploy | What it does |
|-------|--------|-------------|
| 1 | Schema stage 1 (additive) | New column exists, nullable |
| 2 | App v1.X | Dual-write begins |
| 3 | Schema stage 2 (backfill) | Old data populated |
| 4 | App v1.Y | Reads from new column |
| 5 | Schema stage 5 (cleanup) | After observation |

---

## DB Reviewer — Risk Assessment

_[Inserted by db-reviewer agent]_

---

## Sign-off Checklist

- ☐ Each stage tested against staging snapshot
- ☐ Rollback procedure tested for each stage
- ☐ Monitoring queries / dashboards prepared
- ☐ App deploys coordinated with DBA / SRE
- ☐ Maintenance-window scheduled (if needed)
- ☐ DB reviewer notes addressed
- ☐ Final sign-off: {{name}}
