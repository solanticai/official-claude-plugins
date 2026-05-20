# Index Strategy Planner — Reference Material

## Index-Type Decision Tree

```
What does the query do?

├── Equality (`WHERE col = $1`) → B-tree
├── Range (`WHERE col > $1 AND col < $2`) → B-tree
├── ORDER BY col → B-tree (matching direction)
├── IN / ANY → B-tree
├── LIKE 'prefix%' → B-tree
├── LIKE '%suffix' or '%middle%' → trigram (pg_trgm GIN/GiST)
├── Full-text search (`tsvector` / `tsquery`) → GIN with tsvector_ops
├── JSONB containment (`@>`) → GIN with jsonb_path_ops
├── Array containment (`@>`) → GIN
├── Geometric (`<@`, `&&`) → GiST
├── Range (`tstzrange &&`) → GiST
├── Append-only, time-series, big table → BRIN
├── `lower(col) = lower($1)` → expression index on `lower(col)`
└── EXACT row by PK → already covered by PK
```

---

## Partial Index Patterns

When you only care about a subset:

```sql
-- Index only "active" rows (90%+ of queries filter on this)
create index orders_active_idx on orders (created_at desc) where deleted_at is null;

-- Index only "open" status
create index tickets_open_idx on tickets (org_id, priority) where status = 'open';

-- Index only recent (rolling window — useful for time-series with mostly-cold data)
create index audit_log_recent_idx on audit_log (org_id, at desc) where at > '2026-01-01';
```

Benefits: smaller index, faster scans, lower write cost.

---

## Covering Index Patterns (INCLUDE — Postgres 11+)

For queries that read a few extra columns:

```sql
-- Without INCLUDE: query needs to hit heap for total_aud
create index quotes_job_idx on quotes (job_id, version desc);

-- With INCLUDE: index-only scan possible
create index quotes_job_idx on quotes (job_id, version desc) include (total_aud, status);
```

Use when:
- The query selects 1–3 small extra columns regularly
- The covered columns are < 100 bytes total
- The table is read-heavy

Don't use for wide TEXT or large JSONB.

---

## GIN Index Details

- Best for multi-value columns (arrays, JSONB, full-text)
- Higher write cost than B-tree (~3–8× slower inserts)
- Two operator classes for JSONB:
  - `jsonb_ops` (default) — supports `@>`, `?`, `?&`, `?|`
  - `jsonb_path_ops` — only `@>` but smaller + faster

```sql
-- For pure containment queries (most common)
create index docs_metadata_gin_idx on docs using gin (metadata jsonb_path_ops);

-- For key/exists queries
create index docs_metadata_gin_idx on docs using gin (metadata jsonb_ops);
```

---

## BRIN Index Details

- Block Range INdex — stores summary per page range, not per row
- Best for: large append-only tables with natural ordering (created_at, id)
- Very small (typically < 1% of B-tree size)
- Trade-off: queries are slower than B-tree but disk usage is dramatically lower
- Use case: audit logs, IoT data, event streams

```sql
create index audit_log_at_brin on audit_log using brin (at) with (pages_per_range = 32);
```

---

## Composite Index Column Order

Rule: **leftmost columns must match equality filter; range / sort comes last**.

```sql
-- Query: WHERE org_id = $1 AND status = 'draft' ORDER BY scheduled_at DESC
-- Correct:
create index ... on jobs (org_id, status, scheduled_at desc);

-- Wrong (sort first, useless for the WHERE):
create index ... on jobs (scheduled_at desc, org_id, status);
```

The "Left, Equality, Range" order maximises index utility.

---

## Write-Amplification Estimates

Each B-tree index adds approximately:

- **+5–10%** to INSERT time on the table
- **+5–10%** to UPDATE time if updated column is in the index
- **+0%** to UPDATE time if updated column is NOT in the index (HOT updates)
- **+0%** to DELETE time

GIN indexes are heavier (+10–20%).

Aim for: most tables under 5 indexes; high-write tables under 3.

---

## How to Find Unused Indexes

```sql
select
  schemaname, tablename, indexname,
  idx_scan, idx_tup_read, idx_tup_fetch,
  pg_size_pretty(pg_relation_size(indexrelid)) as size,
  pg_stat_user_indexes.indexrelid
from pg_stat_user_indexes
where idx_scan < 50  -- very low usage
  and indexrelid not in (
    select conindid
    from pg_constraint
    where contype in ('p', 'u', 'f')  -- exclude PK / UNIQUE / FK indexes
  )
order by pg_relation_size(indexrelid) desc;
```

Run after database has had typical workload for 1+ week. Indexes with `idx_scan < 50` are candidates for dropping; verify they're not needed for occasional reports first.

---

## FK Columns Need Indexes

Postgres does NOT automatically index FK columns. The most common index-strategy miss in any codebase:

```sql
-- Whenever you add:
alter table orders add column user_id uuid references users(id);

-- ALSO add (especially if user deletion / org deletion needs to cascade):
create index orders_user_id_idx on orders (user_id);
```

Without the FK column index, `delete from users where id = X` does a sequential scan on `orders` to find dependent rows.

---

## Supabase-Specific Notes

- Supabase's `pg_stat_statements` and `pg_stat_user_indexes` are available; use them for index audit
- Supabase has a "Database Performance" page in the dashboard showing slow queries
- `EXPLAIN` output via Supabase MCP / studio is good for diagnosis
- Avoid heavy indexes on `auth.users` — that table is internal to Supabase Auth
