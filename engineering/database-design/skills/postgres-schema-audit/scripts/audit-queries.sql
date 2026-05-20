-- =============================================================================
-- audit-queries.sql
--
-- Canonical read-only SQL query library for the postgres-schema-audit skill.
-- Every query in this file is SELECT-only and safe to run through the Supabase
-- MCP `execute_sql` tool. NONE of these queries mutate data, DDL, policies, or
-- extensions.
--
-- Conventions:
--   :schema       -> psql variable; sub-agents should substitute before running
--                    (via `set_config('audit.schema', 'public', true)` + current_setting
--                    or by string-formatting into mcp__*Supabase__execute_sql calls).
--   LIMIT N       -> every query has a hard limit; bump only for deliberate
--                    deep dives, never by default.
--
-- Organisation (matches reference.md §2):
--   1. Inventory           — tables, columns, PK/FK
--   2. Constraints         — CHECK, NOT NULL, UNIQUE, default values
--   3. Indexes             — coverage, duplication, unused/low-selectivity
--   4. Triggers & functions
--   5. RLS policies
--   6. Type-quality probes — text-that-looks-like-uuid, timestamp hygiene,
--                            JSON vs JSONB, array candidates, enum candidates
--   7. Row counts & bloat  — context for findings (not fixes)
--   8. Cross-schema links  — dependencies between the audited schema and others
--
-- =============================================================================


-- -----------------------------------------------------------------------------
-- 1. INVENTORY
-- -----------------------------------------------------------------------------

-- 1.1  All tables in :schema (base tables only, no views/matviews)
select
  c.relname                                 as table_name,
  c.relrowsecurity                          as rls_enabled,
  c.relforcerowsecurity                     as rls_forced,
  c.reltuples::bigint                       as approx_row_count,
  pg_size_pretty(pg_total_relation_size(c.oid)) as total_size,
  obj_description(c.oid, 'pg_class')        as table_comment
from pg_class c
join pg_namespace n on n.oid = c.relnamespace
where n.nspname = :'schema'
  and c.relkind = 'r'
order by c.relname
limit 500;

-- 1.2  All columns in :schema with data type and nullability
select
  table_name,
  column_name,
  ordinal_position,
  data_type,
  udt_name,
  is_nullable,
  column_default,
  character_maximum_length,
  numeric_precision,
  numeric_scale,
  is_generated,
  generation_expression,
  is_identity,
  identity_generation
from information_schema.columns
where table_schema = :'schema'
order by table_name, ordinal_position
limit 5000;

-- 1.3  Primary keys per table
select
  tc.table_name,
  kcu.column_name,
  kcu.ordinal_position
from information_schema.table_constraints tc
join information_schema.key_column_usage kcu
  on kcu.constraint_name = tc.constraint_name
 and kcu.table_schema    = tc.table_schema
where tc.table_schema = :'schema'
  and tc.constraint_type = 'PRIMARY KEY'
order by tc.table_name, kcu.ordinal_position
limit 2000;

-- 1.4  Foreign keys per table (incl. cross-schema refs)
select
  tc.table_schema              as from_schema,
  tc.table_name                as from_table,
  kcu.column_name              as from_column,
  ccu.table_schema             as to_schema,
  ccu.table_name               as to_table,
  ccu.column_name              as to_column,
  rc.update_rule,
  rc.delete_rule,
  tc.constraint_name
from information_schema.table_constraints tc
join information_schema.key_column_usage kcu
  on kcu.constraint_name = tc.constraint_name
 and kcu.table_schema    = tc.table_schema
join information_schema.referential_constraints rc
  on rc.constraint_name = tc.constraint_name
 and rc.constraint_schema = tc.table_schema
join information_schema.constraint_column_usage ccu
  on ccu.constraint_name = rc.unique_constraint_name
 and ccu.table_schema    = rc.unique_constraint_schema
where tc.table_schema = :'schema'
  and tc.constraint_type = 'FOREIGN KEY'
order by tc.table_name, kcu.ordinal_position
limit 2000;


-- -----------------------------------------------------------------------------
-- 2. CONSTRAINTS
-- -----------------------------------------------------------------------------

-- 2.1  CHECK constraints per table (excludes NOT NULL pseudo-checks)
select
  nsp.nspname           as schema_name,
  cls.relname           as table_name,
  con.conname           as constraint_name,
  pg_get_constraintdef(con.oid, true) as definition
from pg_constraint con
join pg_class cls      on cls.oid = con.conrelid
join pg_namespace nsp  on nsp.oid = cls.relnamespace
where nsp.nspname = :'schema'
  and con.contype = 'c'
order by cls.relname, con.conname
limit 1000;

-- 2.2  UNIQUE constraints per table
select
  tc.table_name,
  tc.constraint_name,
  string_agg(kcu.column_name, ', ' order by kcu.ordinal_position) as columns
from information_schema.table_constraints tc
join information_schema.key_column_usage kcu
  on kcu.constraint_name = tc.constraint_name
 and kcu.table_schema    = tc.table_schema
where tc.table_schema = :'schema'
  and tc.constraint_type = 'UNIQUE'
group by tc.table_name, tc.constraint_name
order by tc.table_name
limit 1000;

-- 2.3  Columns WITHOUT defaults (candidates for default-value findings)
select
  table_name,
  column_name,
  data_type,
  is_nullable
from information_schema.columns
where table_schema = :'schema'
  and column_default is null
  and is_nullable = 'NO'
order by table_name, ordinal_position
limit 2000;


-- -----------------------------------------------------------------------------
-- 3. INDEXES
-- -----------------------------------------------------------------------------

-- 3.1  All indexes with definitions
select
  schemaname as schema_name,
  tablename  as table_name,
  indexname  as index_name,
  indexdef   as definition
from pg_indexes
where schemaname = :'schema'
order by tablename, indexname
limit 2000;

-- 3.2  Foreign-key columns WITHOUT a covering index (classic perf footgun)
with fks as (
  select
    c.conrelid                      as table_oid,
    n.nspname                       as schema_name,
    cl.relname                      as table_name,
    c.conname                       as fk_name,
    c.conkey                        as fk_colnums
  from pg_constraint c
  join pg_class cl      on cl.oid = c.conrelid
  join pg_namespace n   on n.oid = cl.relnamespace
  where c.contype = 'f'
    and n.nspname = :'schema'
),
idx as (
  select
    i.indrelid                      as table_oid,
    i.indkey                        as idx_colnums
  from pg_index i
)
select
  fks.schema_name,
  fks.table_name,
  fks.fk_name,
  array(
    select a.attname
    from pg_attribute a
    where a.attrelid = fks.table_oid
      and a.attnum = any(fks.fk_colnums)
    order by array_position(fks.fk_colnums, a.attnum)
  ) as fk_columns
from fks
where not exists (
  select 1 from idx
  where idx.table_oid = fks.table_oid
    and (
      -- Index leading columns must cover the FK columns (in order)
      (fks.fk_colnums::int[])[1:array_length(fks.fk_colnums, 1)]
        = (idx.idx_colnums::int[])[1:array_length(fks.fk_colnums, 1)]
    )
)
order by fks.table_name
limit 500;

-- 3.3  Duplicate or near-duplicate indexes (same key columns on same table)
select
  schemaname  as schema_name,
  tablename   as table_name,
  array_agg(indexname order by indexname) as duplicate_indexes,
  regexp_replace(indexdef, '^[^(]+', '') as key_signature
from pg_indexes
where schemaname = :'schema'
group by schemaname, tablename, key_signature
having count(*) > 1
order by tablename
limit 200;


-- -----------------------------------------------------------------------------
-- 4. TRIGGERS & FUNCTIONS
-- -----------------------------------------------------------------------------

-- 4.1  Triggers in :schema (excludes internal FK-enforcement triggers)
select
  n.nspname     as schema_name,
  c.relname     as table_name,
  t.tgname      as trigger_name,
  pg_get_triggerdef(t.oid, true) as definition,
  t.tgenabled   as enabled_state,
  p.proname     as function_name
from pg_trigger t
join pg_class c      on c.oid = t.tgrelid
join pg_namespace n  on n.oid = c.relnamespace
join pg_proc p       on p.oid = t.tgfoid
where n.nspname = :'schema'
  and not t.tgisinternal
order by c.relname, t.tgname
limit 1000;

-- 4.2  Functions (including RPCs) in :schema
select
  n.nspname              as schema_name,
  p.proname              as function_name,
  pg_get_function_identity_arguments(p.oid) as args,
  pg_get_function_result(p.oid)             as return_type,
  l.lanname              as language,
  p.prosecdef            as is_security_definer,
  p.provolatile          as volatility,       -- 'i'=immutable,'s'=stable,'v'=volatile
  p.proconfig            as config_settings,  -- contains search_path if set
  obj_description(p.oid, 'pg_proc') as description
from pg_proc p
join pg_namespace n on n.oid = p.pronamespace
join pg_language  l on l.oid = p.prolang
where n.nspname = :'schema'
  and p.prokind = 'f'                         -- plain functions, not aggs/windows
order by p.proname
limit 1000;

-- 4.3  SECURITY DEFINER functions WITHOUT a pinned search_path (CRITICAL)
-- A SECURITY DEFINER function without `SET search_path = ...` in its proconfig
-- is vulnerable to schema-spoofing privilege escalation.
select
  n.nspname               as schema_name,
  p.proname               as function_name,
  pg_get_function_identity_arguments(p.oid) as args,
  coalesce(
    array_to_string(p.proconfig, ', '),
    '(no config)'
  )                       as config_settings
from pg_proc p
join pg_namespace n on n.oid = p.pronamespace
where n.nspname = :'schema'
  and p.prosecdef = true
  and (
    p.proconfig is null
    or not exists (
      select 1 from unnest(coalesce(p.proconfig, array[]::text[])) as cfg
      where cfg ilike 'search_path=%'
    )
  )
order by p.proname
limit 500;


-- -----------------------------------------------------------------------------
-- 5. RLS POLICIES
-- -----------------------------------------------------------------------------

-- 5.1  All policies in :schema
select
  schemaname  as schema_name,
  tablename   as table_name,
  policyname  as policy_name,
  permissive,
  roles,
  cmd         as command,     -- SELECT / INSERT / UPDATE / DELETE / ALL
  qual        as using_expression,
  with_check  as with_check_expression
from pg_policies
where schemaname = :'schema'
order by tablename, policyname
limit 1000;

-- 5.2  Tables with RLS enabled but NO policies (practically un-writable by
--      non-superuser roles; almost always a bug in Supabase projects)
select
  n.nspname     as schema_name,
  c.relname     as table_name
from pg_class c
join pg_namespace n on n.oid = c.relnamespace
where c.relkind = 'r'
  and c.relrowsecurity = true
  and n.nspname = :'schema'
  and not exists (
    select 1 from pg_policies p
    where p.schemaname = n.nspname
      and p.tablename  = c.relname
  )
order by c.relname
limit 200;

-- 5.3  Tables WITHOUT RLS enabled (in a Supabase project this is normally wrong
--      for any user-facing table — flag for review)
select
  n.nspname     as schema_name,
  c.relname     as table_name
from pg_class c
join pg_namespace n on n.oid = c.relnamespace
where c.relkind = 'r'
  and c.relrowsecurity = false
  and n.nspname = :'schema'
order by c.relname
limit 500;


-- -----------------------------------------------------------------------------
-- 6. TYPE-QUALITY PROBES
-- -----------------------------------------------------------------------------

-- 6.1  text/varchar columns whose name suggests a UUID (fk-wrong-type candidates)
select
  table_name,
  column_name,
  data_type,
  udt_name,
  character_maximum_length
from information_schema.columns
where table_schema = :'schema'
  and data_type in ('text', 'character varying', 'character')
  and (
    column_name ilike '%_id'
    or column_name = 'id'
    or column_name ilike '%_uuid'
    or column_name ilike 'uuid_%'
  )
order by table_name, column_name
limit 500;

-- 6.2  timestamp WITHOUT time zone columns (timestamptz hygiene)
select
  table_name,
  column_name,
  data_type,
  column_default
from information_schema.columns
where table_schema = :'schema'
  and data_type = 'timestamp without time zone'
order by table_name, column_name
limit 500;

-- 6.3  json columns that could be jsonb (json→jsonb candidates)
select
  table_name,
  column_name
from information_schema.columns
where table_schema = :'schema'
  and data_type = 'json'
order by table_name, column_name
limit 500;

-- 6.4  Text columns with low distinct-value counts = enum/lookup candidates.
--      Run this as a SAMPLE per column; do NOT run globally (expensive).
--      The sub-agent should pick 3-10 promising columns from the inventory
--      and probe each with a query like:
--
--        select column_name, count(distinct :col) as distinct_values,
--               count(*)                          as total_rows
--        from :schema.:table
--        where :col is not null;
--
--      Mark as `enum-candidate` when distinct_values <= 20 and
--      total_rows >= 1000.

-- 6.5  Columns named as plurals (repeating-group-columns candidates: arrays or
--      child tables). Heuristic: name ends in 's' AND type is text/jsonb.
select
  table_name,
  column_name,
  data_type,
  udt_name
from information_schema.columns
where table_schema = :'schema'
  and (
    column_name ilike '%tags'
    or column_name ilike '%labels'
    or column_name ilike '%categories'
    or column_name ilike '%ids'
    or column_name ilike '%_list'
  )
  and data_type in ('text', 'character varying', 'json', 'jsonb')
order by table_name, column_name
limit 500;

-- 6.6  Columns with numbered suffixes (phone1, phone2, phone3 → array or child
--      table candidate). Detected by looking at sibling column names per table.
with numbered as (
  select
    table_name,
    column_name,
    regexp_replace(column_name, '[0-9]+$', '') as stem
  from information_schema.columns
  where table_schema = :'schema'
    and column_name ~ '[a-z_]+[0-9]+$'
)
select
  table_name,
  stem,
  array_agg(column_name order by column_name) as numbered_siblings,
  count(*) as sibling_count
from numbered
group by table_name, stem
having count(*) >= 2
order by table_name
limit 200;


-- -----------------------------------------------------------------------------
-- 7. ROW COUNTS & BLOAT (context only)
-- -----------------------------------------------------------------------------

-- 7.1  Approximate row counts via pg_class (fast, uses planner stats)
select
  n.nspname                           as schema_name,
  c.relname                           as table_name,
  c.reltuples::bigint                 as approx_row_count,
  pg_size_pretty(pg_relation_size(c.oid))       as table_size,
  pg_size_pretty(pg_indexes_size(c.oid))        as indexes_size,
  pg_size_pretty(pg_total_relation_size(c.oid)) as total_size
from pg_class c
join pg_namespace n on n.oid = c.relnamespace
where n.nspname = :'schema'
  and c.relkind = 'r'
order by pg_total_relation_size(c.oid) desc
limit 200;


-- -----------------------------------------------------------------------------
-- 8. CROSS-SCHEMA LINKS
-- -----------------------------------------------------------------------------

-- 8.1  FKs leaving :schema for other schemas
select
  tc.table_name                as from_table,
  kcu.column_name              as from_column,
  ccu.table_schema             as to_schema,
  ccu.table_name               as to_table,
  ccu.column_name              as to_column,
  tc.constraint_name
from information_schema.table_constraints tc
join information_schema.key_column_usage kcu
  on kcu.constraint_name = tc.constraint_name
 and kcu.table_schema    = tc.table_schema
join information_schema.referential_constraints rc
  on rc.constraint_name = tc.constraint_name
 and rc.constraint_schema = tc.table_schema
join information_schema.constraint_column_usage ccu
  on ccu.constraint_name = rc.unique_constraint_name
 and ccu.table_schema    = rc.unique_constraint_schema
where tc.table_schema = :'schema'
  and tc.constraint_type = 'FOREIGN KEY'
  and ccu.table_schema <> tc.table_schema
order by tc.table_name
limit 500;

-- 8.2  FKs arriving into :schema from other schemas
select
  tc.table_schema              as from_schema,
  tc.table_name                as from_table,
  kcu.column_name              as from_column,
  ccu.table_name               as to_table,
  ccu.column_name              as to_column,
  tc.constraint_name
from information_schema.table_constraints tc
join information_schema.key_column_usage kcu
  on kcu.constraint_name = tc.constraint_name
 and kcu.table_schema    = tc.table_schema
join information_schema.referential_constraints rc
  on rc.constraint_name = tc.constraint_name
 and rc.constraint_schema = tc.table_schema
join information_schema.constraint_column_usage ccu
  on ccu.constraint_name = rc.unique_constraint_name
 and ccu.table_schema    = rc.unique_constraint_schema
where ccu.table_schema = :'schema'
  and tc.constraint_type = 'FOREIGN KEY'
  and tc.table_schema <> ccu.table_schema
order by ccu.table_name
limit 500;

-- =============================================================================
-- End of audit-queries.sql
-- =============================================================================
