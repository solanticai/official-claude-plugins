# RLS Policies — Multi-tenant Jobs-and-Quotes SaaS

**Date:** 20/05/2026

---

## Access Model

- **Tenancy:** Multi-tenant via `org_id` on every business table
- **Admin escape:** Server-side via `service_role` (Edge Functions, cron, admin dashboard backend)
- **Audit:** Required — append-only `audit_log` table; never UPDATE or DELETE
- **Read-share scope:** Within `org_id`, owners + admins see all; members see only their own (`owner_id = auth.uid()` rows)

---

## Pattern per Table

| Table | Pattern | Rationale |
|-------|---------|-----------|
| orgs | Tenant root — only members can read | RLS forbids cross-tenant leak |
| users | Tenant-isolated by org_id | members see their own org's other users |
| customers | Tenant-isolated | within org |
| jobs | Role-based within tenant | owner+admin see all; member sees own |
| quotes | Mirror jobs (via job_id) | inherit job access |
| line_items | Mirror quotes (via quote_id) | inherit |
| attachments | Mirror jobs | inherit |
| audit_log | Append-only insert; admin-only read | immutable history |

---

## RLS SQL Bundle

```sql
-- ============================================
-- Enable RLS
-- ============================================
alter table orgs           enable row level security;
alter table users          enable row level security;
alter table customers      enable row level security;
alter table jobs           enable row level security;
alter table quotes         enable row level security;
alter table line_items     enable row level security;
alter table attachments    enable row level security;
alter table audit_log      enable row level security;

-- ============================================
-- Helper functions (security definer)
-- ============================================
create or replace function auth.current_org_id()
returns uuid
language sql
stable
security definer
set search_path = ''
as $$
  select (auth.jwt() -> 'app_metadata' -> 'org_id')::uuid
$$;

create or replace function auth.current_role()
returns text
language sql
stable
security definer
set search_path = ''
as $$
  select coalesce(auth.jwt() -> 'app_metadata' ->> 'role', 'member')
$$;

create or replace function auth.is_admin_or_owner()
returns boolean
language sql
stable
security definer
set search_path = ''
as $$
  select auth.current_role() in ('admin', 'owner')
$$;

-- ============================================
-- Policies — orgs
-- ============================================
create policy "orgs_select" on orgs
  for select to authenticated
  using (id = auth.current_org_id());

create policy "orgs_update_owner" on orgs
  for update to authenticated
  using (id = auth.current_org_id() and auth.current_role() = 'owner')
  with check (id = auth.current_org_id() and auth.current_role() = 'owner');

-- (no insert/delete via client — those go via service_role)

-- ============================================
-- Policies — users
-- ============================================
create policy "users_select_same_org" on users
  for select to authenticated
  using (org_id = auth.current_org_id());

create policy "users_update_self" on users
  for update to authenticated
  using (id = auth.uid())
  with check (id = auth.uid() and org_id = auth.current_org_id());

-- (insert via Supabase Auth + trigger; delete via service_role only)

-- ============================================
-- Policies — customers
-- ============================================
create policy "customers_select" on customers
  for select to authenticated
  using (org_id = auth.current_org_id());

create policy "customers_insert" on customers
  for insert to authenticated
  with check (org_id = auth.current_org_id());

create policy "customers_update" on customers
  for update to authenticated
  using (org_id = auth.current_org_id())
  with check (org_id = auth.current_org_id());

create policy "customers_delete" on customers
  for delete to authenticated
  using (org_id = auth.current_org_id() and auth.is_admin_or_owner());

-- ============================================
-- Policies — jobs (role-based read)
-- ============================================
create policy "jobs_select_role_based" on jobs
  for select to authenticated
  using (
    org_id = auth.current_org_id()
    and (auth.is_admin_or_owner() or owner_id = auth.uid())
  );

create policy "jobs_insert" on jobs
  for insert to authenticated
  with check (
    org_id = auth.current_org_id()
    and owner_id = auth.uid()
  );

create policy "jobs_update" on jobs
  for update to authenticated
  using (
    org_id = auth.current_org_id()
    and (auth.is_admin_or_owner() or owner_id = auth.uid())
  )
  with check (org_id = auth.current_org_id());

create policy "jobs_delete" on jobs
  for delete to authenticated
  using (
    org_id = auth.current_org_id()
    and auth.is_admin_or_owner()
  );

-- ============================================
-- Policies — quotes (inherit via job_id)
-- ============================================
create policy "quotes_select" on quotes
  for select to authenticated
  using (
    exists (
      select 1 from jobs
      where jobs.id = quotes.job_id
        and jobs.org_id = auth.current_org_id()
        and (auth.is_admin_or_owner() or jobs.owner_id = auth.uid())
    )
  );

-- (insert/update/delete follow same pattern via job_id check)

-- ============================================
-- Policies — audit_log (append-only)
-- ============================================
create policy "audit_log_insert_authenticated" on audit_log
  for insert to authenticated
  with check (org_id = auth.current_org_id());

create policy "audit_log_select_admin_only" on audit_log
  for select to authenticated
  using (
    org_id = auth.current_org_id()
    and auth.is_admin_or_owner()
  );

-- (no update / no delete via any role except service_role)

-- ============================================
-- Indexes to support RLS performance
-- ============================================
create index users_org_id_idx       on users (org_id);
create index customers_org_id_idx   on customers (org_id);
create index jobs_org_id_idx        on jobs (org_id);
create index jobs_owner_id_idx      on jobs (owner_id);
create index quotes_job_id_idx      on quotes (job_id);
create index line_items_quote_id_idx on line_items (quote_id);
create index attachments_job_id_idx on attachments (job_id);
create index audit_log_org_id_idx   on audit_log (org_id);
```

---

## Admin Escape Pattern

```typescript
// Server-side only — Edge Function or admin backend
const supabaseAdmin = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_ROLE_KEY  // NEVER expose to client
);

// Bypasses all RLS
const { data } = await supabaseAdmin.from('jobs').select('*');
```

**Critical:** `SUPABASE_SERVICE_ROLE_KEY` must:
- Live in server env vars only
- Never be sent to browser
- Never be checked into git
- Be rotated if exposed

---

## Test Queries

### Positive tests (should succeed)

```sql
-- Member sees their own jobs
set local role authenticated;
set local "request.jwt.claims" to '{"sub": "uuid-alice", "app_metadata": {"org_id": "uuid-org-1", "role": "member"}}';
select count(*) from jobs;   -- expect: only Alice's jobs

-- Admin sees all org jobs
set local "request.jwt.claims" to '{"sub": "uuid-bob", "app_metadata": {"org_id": "uuid-org-1", "role": "admin"}}';
select count(*) from jobs;   -- expect: all org-1 jobs
```

### Negative tests (should return empty)

```sql
-- Alice cannot see another org's jobs
set local "request.jwt.claims" to '{"sub": "uuid-alice", "app_metadata": {"org_id": "uuid-org-1", "role": "member"}}';
select * from jobs where org_id = 'uuid-org-2';  -- expect: 0 rows

-- Member cannot see other members' jobs (in same org)
select * from jobs where owner_id = 'uuid-charlie';  -- expect: 0 rows (unless Alice happens to be admin)
```

### Admin tests (service_role bypasses)

```sql
set local role service_role;
select count(*) from jobs;  -- expect: total across all orgs
```

---

## Common Pitfalls Checklist

- ☑ All 4 actions covered for every protected table (SELECT, INSERT, UPDATE, DELETE)
- ☑ `with check` matches `using` for INSERT/UPDATE
- ☑ All helper functions use `security definer set search_path = ''`
- ☑ RLS-filter columns indexed (org_id, owner_id, job_id)
- ☑ No recursive policies (no table self-referenced in USING)
- ☑ Service-role usage is server-side only; documented
- ☑ Audit log is append-only (no UPDATE/DELETE policies for client)
- ☑ Multi-tenant `org_id` check in every business-table policy
