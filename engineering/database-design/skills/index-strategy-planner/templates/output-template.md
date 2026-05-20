# Index Strategy — {{database_name}}

**Date:** {{date_dd_mm_yyyy}}

---

## Query Diagnoses

| Query (abbreviated) | Current plan issue | Filter cols | Sort cols | Join cols |
|--------------------|--------------------|-------------|-----------|-----------|
| {{q}} | {{seq_scan / wrong_index / sort_failed}} | {{cols}} | {{cols}} | {{cols}} |

---

## Recommended New Indexes

| # | Slow query | Recommended index | Type | DDL | Estimated impact |
|---|------------|-------------------|------|-----|-----------------|
| 1 | {{q}} | {{idx_name}} | {{btree/partial/covering/gin/brin}} | `{{ddl}}` | {{n× speedup}} |

---

## Indexes to Drop

| Index | Reason | DDL |
|-------|--------|-----|
| {{idx}} | {{duplicate / unused / superseded}} | `drop index concurrently {{idx}};` |

---

## Cost Summary

| New index | Est. size | Write-amplification on parent table |
|-----------|----------|-------------------------------------|
| {{idx}} | {{MB}} | +{{n}}% on insert/update |

**Total added storage:** ~{{n}} MB
**Total estimated write-overhead increase:** {{n}}% on heaviest-trafficked tables

---

## Sequencing — Order to Apply

1. **Drop unused indexes first** (recovers write headroom)
2. **Add partial indexes** (smallest; quickest wins)
3. **Add covering indexes** (more storage but biggest read wins)
4. **Reanalyze** affected tables
5. **Verify** with re-run of EXPLAIN ANALYZE on the slow queries

---

## Verification Queries

```sql
-- After applying indexes, re-run EXPLAIN ANALYZE on each slow query
explain (analyze, buffers) {{slow_query}};

-- Index usage statistics (after 1 week)
select
  schemaname, tablename, indexname,
  idx_scan, idx_tup_read, idx_tup_fetch,
  pg_size_pretty(pg_relation_size(indexrelid)) as size
from pg_stat_user_indexes
order by idx_scan desc;
```
