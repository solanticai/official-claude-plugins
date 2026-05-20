# Business Data Model Designer -- Reference

Supplementary reference material for the business-data-model-designer skill.
Contains RLS policy patterns, index strategy, Supabase-specific patterns,
normalisation checklist, data type guidance, and migration sequencing rules.

---

## Table of Contents

1. [Common RLS Policy Patterns](#1-common-rls-policy-patterns)
2. [Index Strategy Reference](#2-index-strategy-reference)
3. [Supabase-Specific Patterns](#3-supabase-specific-patterns)
4. [Normalisation Checklist](#4-normalisation-checklist)
5. [Data Type Selection Guide](#5-data-type-selection-guide)
6. [Migration Sequencing Rules](#6-migration-sequencing-rules)

---

## 1. Common RLS Policy Patterns

### 1A. Tenant Isolation (Multi-Tenant SaaS)

Every row belongs to an organisation. Users can only access rows belonging
to their own organisation. This is the most common pattern for B2B SaaS.

```sql
-- Helper function (create once, use in all tenant-scoped policies)
CREATE OR REPLACE FUNCTION public.get_user_org_id()
RETURNS UUID AS $$
  SELECT organisation_id FROM public.profiles WHERE id = auth.uid()
$$ LANGUAGE SQL STABLE SECURITY DEFINER;

-- Enable RLS
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;

-- SELECT: users see only their org's data
CREATE POLICY "tenant_isolation_select" ON projects
  FOR SELECT USING (
    organisation_id = public.get_user_org_id()
  );

-- INSERT: users can only create within their org
CREATE POLICY "tenant_isolation_insert" ON projects
  FOR INSERT WITH CHECK (
    organisation_id = public.get_user_org_id()
  );

-- UPDATE: users can only modify their org's data
CREATE POLICY "tenant_isolation_update" ON projects
  FOR UPDATE USING (
    organisation_id = public.get_user_org_id()
  ) WITH CHECK (
    organisation_id = public.get_user_org_id()
  );

-- DELETE: users can only delete their org's data
CREATE POLICY "tenant_isolation_delete" ON projects
  FOR DELETE USING (
    organisation_id = public.get_user_org_id()
  );
```

### 1B. Role-Based Access (Within Tenant)

Different roles have different permissions on the same table.

```sql
-- Helper function
CREATE OR REPLACE FUNCTION public.get_user_role()
RETURNS TEXT AS $$
  SELECT role FROM public.profiles WHERE id = auth.uid()
$$ LANGUAGE SQL STABLE SECURITY DEFINER;

-- All org members can read
CREATE POLICY "members_read" ON projects
  FOR SELECT USING (
    organisation_id = public.get_user_org_id()
  );

-- Only admins and managers can create
CREATE POLICY "managers_create" ON projects
  FOR INSERT WITH CHECK (
    organisation_id = public.get_user_org_id()
    AND public.get_user_role() IN ('admin', 'manager')
  );

-- Only admins can delete
CREATE POLICY "admins_delete" ON projects
  FOR DELETE USING (
    organisation_id = public.get_user_org_id()
    AND public.get_user_role() = 'admin'
  );
```

### 1C. Owner-Only Access

Users can only access records they own. Common for personal settings,
drafts, and user-generated content before publishing.

```sql
ALTER TABLE user_drafts ENABLE ROW LEVEL SECURITY;

CREATE POLICY "owner_select" ON user_drafts
  FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "owner_insert" ON user_drafts
  FOR INSERT WITH CHECK (user_id = auth.uid());

CREATE POLICY "owner_update" ON user_drafts
  FOR UPDATE USING (user_id = auth.uid())
  WITH CHECK (user_id = auth.uid());

CREATE POLICY "owner_delete" ON user_drafts
  FOR DELETE USING (user_id = auth.uid());
```

### 1D. Public Read, Authenticated Write

Published content is visible to everyone (including anonymous users).
Only authenticated users can create or modify content.

```sql
ALTER TABLE articles ENABLE ROW LEVEL SECURITY;

-- Anyone (including anon) can read published articles
CREATE POLICY "public_read_published" ON articles
  FOR SELECT USING (status = 'published');

-- Authenticated users can read their own drafts
CREATE POLICY "authors_read_own_drafts" ON articles
  FOR SELECT USING (
    auth.uid() IS NOT NULL
    AND author_id = auth.uid()
    AND status = 'draft'
  );

-- Authenticated users can create articles
CREATE POLICY "authenticated_insert" ON articles
  FOR INSERT WITH CHECK (
    auth.uid() IS NOT NULL
    AND author_id = auth.uid()
  );

-- Authors can update their own articles
CREATE POLICY "authors_update_own" ON articles
  FOR UPDATE USING (author_id = auth.uid())
  WITH CHECK (author_id = auth.uid());
```

### 1E. Team/Group-Based Access

Access is scoped to a team. Users may belong to multiple teams.
Requires a membership junction table.

```sql
-- Prerequisite: team_members(team_id UUID, user_id UUID, role TEXT)

ALTER TABLE team_documents ENABLE ROW LEVEL SECURITY;

CREATE POLICY "team_members_read" ON team_documents
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM team_members tm
      WHERE tm.team_id = team_documents.team_id
        AND tm.user_id = auth.uid()
    )
  );

CREATE POLICY "team_members_insert" ON team_documents
  FOR INSERT WITH CHECK (
    EXISTS (
      SELECT 1 FROM team_members tm
      WHERE tm.team_id = team_documents.team_id
        AND tm.user_id = auth.uid()
        AND tm.role IN ('admin', 'editor')
    )
  );
```

### 1F. Service Role Bypass

For server-side operations (Edge Functions, webhooks) that need to bypass RLS.

```sql
-- Supabase service_role key bypasses RLS automatically.
-- For functions that run as the user but need elevated access on specific tables:
CREATE POLICY "service_role_all" ON internal_logs
  FOR ALL USING (
    auth.jwt()->>'role' = 'service_role'
  );
```

**Note:** Prefer using the Supabase service_role client on the server rather than
writing RLS bypass policies. The service_role key should never be exposed to the
client.

---

## 2. Index Strategy Reference

### When to Use Each Index Type

| Index Type | Operator Classes | Best For | Example |
|---|---|---|---|
| **B-tree** (default) | `=`, `<`, `>`, `<=`, `>=`, `BETWEEN`, `IS NULL`, `IN` | Equality and range queries on scalar types; sorting; unique constraints | `CREATE INDEX idx_projects_status ON projects(status);` |
| **GIN** | `@>`, `<@`, `?`, `?&`, `?\|`, `@@` | JSONB containment, array operations, full-text search (tsvector) | `CREATE INDEX idx_metadata ON entities USING GIN(metadata);` |
| **GiST** | `<<`, `>>`, `&&`, `@>`, `<@`, `~=` | Geometric/spatial data, range types, nearest-neighbor, full-text (less precise but faster updates than GIN) | `CREATE INDEX idx_location ON venues USING GIST(location);` |
| **BRIN** | `=`, `<`, `>` on naturally ordered data | Very large tables where the indexed column correlates with physical row order (e.g., timestamps on append-only tables) | `CREATE INDEX idx_events_created ON events USING BRIN(created_at);` |
| **Hash** | `=` only | Pure equality lookups (rare -- B-tree is usually sufficient) | `CREATE INDEX idx_lookup ON cache USING HASH(key);` |

### Composite Index Guidelines

```sql
-- Rule: put equality columns first, range columns last
-- Query: WHERE org_id = X AND status = 'active' AND created_at > '2025-01-01'
CREATE INDEX idx_projects_org_status_created
  ON projects(organisation_id, status, created_at);

-- The index above supports these queries efficiently:
--   WHERE organisation_id = X
--   WHERE organisation_id = X AND status = Y
--   WHERE organisation_id = X AND status = Y AND created_at > Z
-- But NOT:
--   WHERE status = Y (leading column skipped)
--   WHERE created_at > Z (leading columns skipped)
```

### Partial Index Examples

```sql
-- Only index active rows (most queries filter on status='active')
CREATE INDEX idx_active_projects
  ON projects(organisation_id, created_at)
  WHERE status = 'active';

-- Only index non-deleted rows (soft delete pattern)
CREATE INDEX idx_non_deleted_tasks
  ON tasks(project_id, assigned_to)
  WHERE deleted_at IS NULL;

-- Only index rows needing processing
CREATE INDEX idx_pending_jobs
  ON background_jobs(created_at)
  WHERE status = 'pending';
```

### GIN Index Patterns for JSONB

```sql
-- Index all keys and values (most flexible, largest index)
CREATE INDEX idx_settings_gin ON user_settings USING GIN(preferences);
-- Supports: preferences @> '{"theme": "dark"}'

-- Index only keys (smaller, for key-existence checks)
CREATE INDEX idx_settings_keys ON user_settings USING GIN(preferences jsonb_path_ops);
-- Supports: preferences @> '{"theme": "dark"}'
-- Does NOT support: preferences ? 'theme'

-- Index a specific JSONB path as B-tree (for equality/range on one key)
CREATE INDEX idx_settings_theme ON user_settings ((preferences->>'theme'));
-- Supports: preferences->>'theme' = 'dark'
```

### Index Recommendations for RLS-Heavy Tables

RLS policies execute subqueries on every row access. Index the columns used
inside those subqueries:

```sql
-- If your RLS policy uses: get_user_org_id() which queries profiles
CREATE INDEX idx_profiles_user_id ON profiles(id);  -- usually covered by PK
-- The profiles table must be fast to query from RLS context

-- If your RLS joins team_members
CREATE INDEX idx_team_members_user_team
  ON team_members(user_id, team_id);

-- If your RLS checks a role column
CREATE INDEX idx_profiles_org_role
  ON profiles(organisation_id, role);
```

---

## 3. Supabase-Specific Patterns

### 3A. auth.uid() and auth.jwt()

```sql
-- auth.uid() returns the UUID of the currently authenticated user
-- Equivalent to: (auth.jwt()->>'sub')::uuid

-- Common usage in RLS policies
CREATE POLICY "own_data" ON profiles
  FOR SELECT USING (id = auth.uid());

-- auth.jwt() returns the full JWT claims as JSONB
-- Useful for checking custom claims or metadata
SELECT auth.jwt()->>'role';           -- Supabase role (anon, authenticated, service_role)
SELECT auth.jwt()->'app_metadata';    -- Custom app metadata set via admin API
SELECT auth.jwt()->'user_metadata';   -- User-editable metadata
```

### 3B. Profile Auto-Creation on Signup

```sql
-- Trigger function to create a profile when a user signs up
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.profiles (id, full_name, avatar_url, email)
  VALUES (
    NEW.id,
    COALESCE(NEW.raw_user_meta_data->>'full_name', ''),
    NEW.raw_user_meta_data->>'avatar_url',
    NEW.email
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = '';

CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
```

### 3C. Storage Integration

```sql
-- Storage objects reference auth.users for ownership
-- Typical RLS on storage.objects:

-- Users can upload to their own folder
CREATE POLICY "users_upload_own_folder" ON storage.objects
  FOR INSERT WITH CHECK (
    bucket_id = 'avatars'
    AND (storage.foldername(name))[1] = auth.uid()::text
  );

-- Users can read their own files
CREATE POLICY "users_read_own_files" ON storage.objects
  FOR SELECT USING (
    bucket_id = 'avatars'
    AND (storage.foldername(name))[1] = auth.uid()::text
  );

-- Org-scoped file access
CREATE POLICY "org_members_read_files" ON storage.objects
  FOR SELECT USING (
    bucket_id = 'documents'
    AND (storage.foldername(name))[1] = public.get_user_org_id()::text
  );
```

### 3D. Realtime Subscriptions

```sql
-- Enable realtime on a table
ALTER PUBLICATION supabase_realtime ADD TABLE messages;

-- RLS must allow SELECT for the subscribing user, otherwise
-- realtime events will be filtered out silently.
-- Test: subscribe as user A and insert as user B -- user A should
-- only see events for rows their RLS policy permits.

-- Realtime works best with:
--   1. RLS enabled and policies that use auth.uid()
--   2. Primary key on the table
--   3. No overly complex RLS subqueries (performance)
```

### 3E. Supabase Client Query Patterns

```sql
-- The schema must support supabase-js auto-joins via foreign keys.
-- supabase.from('projects').select('*, clients(name, email)')
-- This requires: projects.client_id REFERENCES clients(id)

-- For many-to-many, use a junction table:
-- supabase.from('projects').select('*, tags:project_tags(tag:tags(name))')
-- Requires: project_tags.project_id -> projects.id
--           project_tags.tag_id -> tags.id

-- Computed/virtual columns via Supabase:
-- Use generated columns for simple computations
ALTER TABLE invoices ADD COLUMN total_with_tax NUMERIC
  GENERATED ALWAYS AS (subtotal * (1 + tax_rate)) STORED;
```

### 3F. SECURITY DEFINER vs SECURITY INVOKER

```sql
-- SECURITY DEFINER: runs with the privileges of the function OWNER
-- Use for: RLS helper functions, functions that need to read across tenants
CREATE FUNCTION get_user_org_id() RETURNS UUID AS $$
  SELECT organisation_id FROM profiles WHERE id = auth.uid()
$$ LANGUAGE SQL STABLE SECURITY DEFINER;

-- SECURITY INVOKER (default): runs with the privileges of the calling user
-- Use for: general-purpose functions, functions where RLS should apply
CREATE FUNCTION get_my_projects() RETURNS SETOF projects AS $$
  SELECT * FROM projects  -- RLS filters automatically
$$ LANGUAGE SQL STABLE SECURITY INVOKER;

-- IMPORTANT: SECURITY DEFINER functions should SET search_path = ''
-- to prevent search_path injection attacks.
CREATE FUNCTION safe_function() RETURNS void AS $$
BEGIN
  -- use fully qualified names: public.profiles, auth.uid()
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = '';
```

---

## 4. Normalisation Checklist

### First Normal Form (1NF)

**Rule:** Every column holds atomic (indivisible) values. No repeating groups.

| Violation | Problem | Fix |
|---|---|---|
| `tags TEXT` storing `"tag1,tag2,tag3"` | Cannot query individual tags efficiently; no referential integrity | Create a `tags` table and a `entity_tags` junction table |
| `phone_1 TEXT, phone_2 TEXT, phone_3 TEXT` | Fixed number of repeating columns; what about phone_4? | Create a `contact_phones` table with `(contact_id, phone, type)` |
| `address TEXT` storing full address as one string | Cannot query by city, state, or postcode | Split into `street`, `city`, `state`, `postcode`, `country` columns |

**Pragmatic exception:** PostgreSQL arrays (`TEXT[]`) are acceptable for simple
value lists that are always read/written as a whole and never queried individually
(e.g., `tags TEXT[]` for display-only tags with no foreign key requirement).

### Second Normal Form (2NF)

**Rule:** All non-key columns depend on the entire primary key (relevant for
composite keys).

| Violation | Problem | Fix |
|---|---|---|
| Table `order_items(order_id, product_id, product_name, quantity)` | `product_name` depends only on `product_id`, not the full key | Move `product_name` to the `products` table; reference via FK |
| Table `project_members(project_id, user_id, user_email, role)` | `user_email` depends only on `user_id` | Move `user_email` to the `profiles` table |

### Third Normal Form (3NF)

**Rule:** No non-key column depends on another non-key column (no transitive
dependencies).

| Violation | Problem | Fix |
|---|---|---|
| Table with `city` and `country` columns | `country` is determined by `city` (transitively) | Create a `cities` lookup table, or accept the denormalisation if the city-country relationship is not strict |
| Table with `unit_price`, `quantity`, `total_price` | `total_price = unit_price * quantity` (derived) | Either remove `total_price` and compute it, or use a GENERATED ALWAYS AS column |
| Table with `plan_name` alongside `plan_id` | `plan_name` depends on `plan_id`, not on the row's PK | Store only `plan_id`; join to `plans` table for the name |

**Pragmatic exceptions for Supabase applications:**
- Denormalised counters (e.g., `project_count` on organisations) maintained by
  triggers -- acceptable when the join + count is a performance bottleneck
- Caching fields (e.g., `last_activity_at` on users) -- acceptable when the
  source table is very large and the derived value is queried frequently

---

## 5. Data Type Selection Guide

| Decision | Option A | Option B | Recommendation |
|---|---|---|---|
| **Primary key** | `SERIAL` / `BIGSERIAL` | `UUID` | **UUID** (`gen_random_uuid()`). Avoids leaking record count; safe for distributed systems; Supabase standard. Serial only for internal sequence-dependent tables. |
| **Timestamps** | `TIMESTAMP` | `TIMESTAMPTZ` | **TIMESTAMPTZ always.** Stores UTC internally, converts for clients. Prevents timezone bugs. Supabase requires this. |
| **Short strings** | `VARCHAR(N)` | `TEXT` | **TEXT** in most cases. PostgreSQL stores both identically. Use `VARCHAR(N)` only if you need the DB to enforce a max length (e.g., `slug VARCHAR(100)`). Use CHECK constraints for more complex validation. |
| **Monetary values** | `NUMERIC(12,2)` | `INTEGER` (cents) | **NUMERIC(12,2)** for display values. **INTEGER** (cents) for computation-heavy or Stripe-integrated systems. Document which convention is used. Never use `FLOAT` or `REAL` for money. |
| **Boolean flags** | `BOOLEAN` | `TEXT` enum | **BOOLEAN** for true/false. Use `TEXT` CHECK or ENUM only if the field might gain more values later (e.g., a `status` that starts as active/inactive but might gain `suspended`). |
| **Status fields** | `TEXT` with CHECK | `CREATE TYPE ... AS ENUM` | **ENUM** for stable, well-known value sets (project_status, invoice_status). **TEXT with CHECK** for values that might change frequently (easier to alter). |
| **JSON data** | `JSON` | `JSONB` | **JSONB always.** Binary storage, indexable, supports containment operators. `JSON` only preserves formatting -- almost never needed. |
| **Arrays** | `TEXT[]` | Junction table | **Junction table** when the values are entities with their own identity (tags, categories). **Array** for simple value lists with no FK requirement. |
| **Email** | `TEXT` | `CITEXT` | **CITEXT** if you need case-insensitive uniqueness without lower() wrappers. Requires `CREATE EXTENSION citext`. Otherwise TEXT with a CHECK or lower() index. |
| **IP addresses** | `TEXT` | `INET` | **INET** for IP addresses. Supports network operations and containment queries. |
| **Date-only** | `DATE` | `TIMESTAMPTZ` | **DATE** when time component is irrelevant (birthdays, due dates). **TIMESTAMPTZ** when time matters. |

### Column Naming Conventions

```
id                  UUID primary key
[entity]_id         UUID foreign key (e.g., project_id, client_id)
name                TEXT display name
slug                TEXT URL-safe identifier (lowercase, hyphens)
title               TEXT longer display name
description         TEXT free-form description
status              ENUM or TEXT current state
type                ENUM or TEXT classification
email               TEXT or CITEXT
url                 TEXT
amount              NUMERIC(12,2) or INTEGER (cents)
quantity            INTEGER
is_[adjective]      BOOLEAN (is_active, is_verified, is_public)
[noun]_count        INTEGER denormalised counter
[past_participle]_at TIMESTAMPTZ event timestamp (created_at, deleted_at, published_at)
[past_participle]_by UUID reference to the user who performed the action
metadata            JSONB flexible key-value data
settings            JSONB user/org preferences
```

---

## 6. Migration Sequencing Rules

Supabase migrations must be ordered to respect dependencies. Run items in the
order listed below. Each numbered step can be a separate migration file or a
section within a single file.

### Required Order

```
1. EXTENSIONS
   CREATE EXTENSION IF NOT EXISTS ...
   (uuid-ossp, pgcrypto, citext, pg_trgm, etc.)

2. CUSTOM TYPES / ENUMS
   CREATE TYPE project_status AS ENUM (...)
   (Must exist before tables that reference them)

3. TABLES (dependency order: parents before children)
   a. Standalone tables (no foreign keys to other new tables)
      - organisations
      - categories (lookups)
   b. Tables referencing (a)
      - profiles (references auth.users and organisations)
      - clients (references organisations)
   c. Tables referencing (b)
      - projects (references clients, organisations)
   d. Tables referencing (c)
      - tasks (references projects)
      - invoices (references projects, clients)
   e. Junction tables (last -- reference two or more tables)
      - project_tags (references projects, tags)
      - team_members (references teams, profiles)

4. INDEXES
   (Tables must exist before indexes can be created)
   - Foreign key columns
   - Columns used in WHERE/JOIN/ORDER BY
   - Columns used in RLS policy subqueries
   - Composite indexes for known query patterns
   - Partial indexes for common filters

5. ROW LEVEL SECURITY
   (Tables must exist; helper functions should exist first)
   a. Enable RLS on each table
      ALTER TABLE [name] ENABLE ROW LEVEL SECURITY;
   b. Create policies for each operation
      CREATE POLICY ... FOR SELECT/INSERT/UPDATE/DELETE

6. FUNCTIONS
   a. RLS helper functions (get_user_org_id, get_user_role)
      -- These can go before step 5 since RLS policies reference them
   b. Trigger functions (handle_updated_at, handle_new_user)
   c. Business logic functions (calculate_invoice_total, etc.)
   d. RPC functions exposed via supabase.rpc()

7. TRIGGERS
   (Tables and trigger functions must exist)
   - updated_at triggers on all tables with that column
   - auth.users signup trigger
   - Audit log triggers
   - Denormalisation maintenance triggers

8. SEED DATA
   (All tables, constraints, and RLS must be in place)
   - Default roles / permission sets
   - Lookup table values (categories, statuses)
   - System configuration records
   - Test/demo data (separate migration, optional)
```

### Migration File Naming

```
-- Supabase migration format:
-- supabase/migrations/YYYYMMDDHHMMSS_description.sql

20250101000000_create_extensions.sql
20250101000001_create_enums.sql
20250101000002_create_organisations_table.sql
20250101000003_create_profiles_table.sql
20250101000004_create_core_tables.sql
20250101000005_create_junction_tables.sql
20250101000006_create_indexes.sql
20250101000007_create_rls_helpers.sql
20250101000008_create_rls_policies.sql
20250101000009_create_triggers.sql
20250101000010_seed_data.sql
```

### Idempotent Migration Patterns

```sql
-- Tables
CREATE TABLE IF NOT EXISTS organisations ( ... );

-- Enums (not natively idempotent -- use DO block)
DO $$ BEGIN
  CREATE TYPE project_status AS ENUM ('draft', 'active', 'completed');
EXCEPTION
  WHEN duplicate_object THEN NULL;
END $$;

-- Indexes
CREATE INDEX IF NOT EXISTS idx_projects_org ON projects(organisation_id);

-- Policies (drop first, then create)
DROP POLICY IF EXISTS "tenant_select" ON projects;
CREATE POLICY "tenant_select" ON projects FOR SELECT USING (...);

-- Functions (use CREATE OR REPLACE)
CREATE OR REPLACE FUNCTION public.handle_updated_at() ...

-- Triggers (drop first, then create)
DROP TRIGGER IF EXISTS set_updated_at ON projects;
CREATE TRIGGER set_updated_at BEFORE UPDATE ON projects
  FOR EACH ROW EXECUTE FUNCTION public.handle_updated_at();
```

### Common Migration Mistakes

| Mistake | Problem | Fix |
|---|---|---|
| Creating a table before its referenced table exists | FK constraint fails | Order tables by dependency (parents first) |
| Forgetting to enable RLS | Table is publicly accessible via PostgREST | Always `ALTER TABLE x ENABLE ROW LEVEL SECURITY` |
| Creating RLS policy before helper function exists | Policy references undefined function | Create helper functions before policies |
| Using `TIMESTAMP` instead of `TIMESTAMPTZ` | Timezone bugs in Supabase client | Always use `TIMESTAMPTZ` |
| Not indexing foreign key columns | Slow JOINs and slow CASCADE deletes | Explicitly create indexes on all FK columns |
| Hardcoding UUIDs in seed data | Breaks on re-run; conflicts across environments | Use `gen_random_uuid()` or variables in seed scripts |
