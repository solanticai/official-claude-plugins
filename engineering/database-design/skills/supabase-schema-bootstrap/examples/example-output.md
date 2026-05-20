# Schema Bootstrap — Jobs-and-Quotes SaaS (AU)

**Date:** 20/05/2026
**Supabase region:** ap-southeast-2 (Sydney) — for AU data sovereignty

---

## Domain Summary

- **Multi-tenant:** Yes — via `org_id` on every business table
- **Core entities:** orgs, users, customers, jobs, quotes, line_items, attachments, audit_log
- **Access model:** Owner+Admin see all org data; Member sees their own; service_role bypasses all (server-only)

---

## Tables

| Table | Purpose | Tenant column | Notes |
|-------|---------|--------------|-------|
| orgs | Tenant root | — (is the tenant) | |
| users | Org members | org_id | Mirror of auth.users with role/org context |
| customers | Org's external customers | org_id | |
| jobs | Work items | org_id | Status enum: draft/quoted/scheduled/in_progress/done/cancelled |
| quotes | Versioned quotes per job | (via job_id) | Multiple per job (revision history) |
| line_items | Quote line items | (via quote_id) | |
| attachments | Files per job | (via job_id) | Stored in Supabase Storage |
| audit_log | Append-only audit | org_id | Insert only |

---

## RLS Approach

| Table | Pattern | Reference |
|-------|---------|----------|
| orgs | Tenant root — members can SELECT; owner can UPDATE | Single-tenant-root |
| users | Tenant-isolated; self can UPDATE own profile | Tenant-isolated + self-update |
| customers | Tenant-isolated | Tenant-isolated |
| jobs | Role-based within tenant (owner+admin see all; member sees own) | Role-based within tenant |
| quotes/line_items/attachments | Inherit via job_id | Inherited-via-parent |
| audit_log | Insert by authenticated; Select admin-only | Audit-table |

---

## Indexes Added

| Index | Purpose |
|-------|---------|
| users_org_id_idx | RLS filter |
| customers_org_id_idx | RLS filter |
| jobs_org_id_idx | RLS filter |
| jobs_owner_id_idx | RLS sub-filter for member-scope |
| jobs_org_status_scheduled_idx (partial) | Dashboard "active jobs" query |
| quotes_job_id_idx | FK + RLS via job |
| line_items_quote_id_idx | FK |
| attachments_job_id_idx | FK + RLS via job |
| audit_log_org_id_idx | RLS filter |
| users_email_lower_idx (unique) | Case-insensitive email lookup |

---

## Triggers

| Trigger | Tables | Purpose |
|---------|--------|---------|
| set_updated_at | orgs, users, customers, jobs, quotes, line_items, attachments | Auto-update timestamp |
| handle_new_user | auth.users → public.users | Creates public.users row on signup |
| audit_log_jobs | jobs | Inserts into audit_log on every write |
| audit_log_quotes | quotes | Same |

---

## Bootstrap SQL

```sql
-- supabase/migrations/20260520120000_initial_bootstrap.sql

-- =====================================
-- 1. Extensions
-- =====================================
create extension if not exists pgcrypto;
create extension if not exists pg_stat_statements;

-- =====================================
-- 2. Helper functions
-- =====================================
create or replace function public.set_updated_at()
returns trigger language plpgsql security definer set search_path = '' as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

create or replace function auth.current_org_id()
returns uuid language sql stable security definer set search_path = '' as $$
  select (auth.jwt() -> 'app_metadata' -> 'org_id')::uuid
$$;

create or replace function auth.current_role()
returns text language sql stable security definer set search_path = '' as $$
  select coalesce(auth.jwt() -> 'app_metadata' ->> 'role', 'member')
$$;

create or replace function auth.is_admin_or_owner()
returns boolean language sql stable security definer set search_path = '' as $$
  select auth.current_role() in ('admin', 'owner')
$$;

-- =====================================
-- 3. Core tables
-- =====================================
create table orgs (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  abn text unique,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create table users (
  id uuid primary key references auth.users(id) on delete cascade,
  org_id uuid not null references orgs(id) on delete cascade,
  email text not null,
  role text not null default 'member' check (role in ('owner', 'admin', 'member')),
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);
create unique index users_email_lower_idx on users (lower(email));

create table customers (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references orgs(id) on delete cascade,
  name text not null,
  email text,
  phone text,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create table jobs (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references orgs(id) on delete restrict,
  customer_id uuid not null references customers(id) on delete restrict,
  owner_id uuid not null references users(id) on delete restrict,
  status text not null check (status in ('draft', 'quoted', 'scheduled', 'in_progress', 'done', 'cancelled')),
  scheduled_at timestamptz,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create table quotes (
  id uuid primary key default gen_random_uuid(),
  job_id uuid not null references jobs(id) on delete cascade,
  version int not null,
  total_aud numeric(12, 2) not null,
  status text not null,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create table line_items (
  id uuid primary key default gen_random_uuid(),
  quote_id uuid not null references quotes(id) on delete cascade,
  description text not null,
  qty numeric(10, 2) not null,
  unit_price_aud numeric(12, 2) not null,
  total_aud numeric(12, 2) not null,
  created_at timestamptz default now()
);

create table attachments (
  id uuid primary key default gen_random_uuid(),
  job_id uuid not null references jobs(id) on delete cascade,
  uploader_id uuid not null references users(id),
  file_path text not null,
  size_bytes bigint not null,
  created_at timestamptz default now()
);

create table audit_log (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references orgs(id) on delete cascade,
  user_id uuid references users(id),
  entity text not null,
  entity_id uuid not null,
  action text not null,
  payload jsonb,
  at timestamptz default now()
);

-- =====================================
-- 4. Indexes for performance + RLS
-- =====================================
create index users_org_id_idx       on users (org_id);
create index customers_org_id_idx   on customers (org_id);
create index jobs_org_id_idx        on jobs (org_id);
create index jobs_owner_id_idx      on jobs (owner_id);
create index jobs_org_status_scheduled_idx
  on jobs (org_id, scheduled_at desc)
  where status in ('draft', 'quoted', 'scheduled', 'in_progress');
create index quotes_job_id_idx      on quotes (job_id);
create index line_items_quote_id_idx on line_items (quote_id);
create index attachments_job_id_idx on attachments (job_id);
create index audit_log_org_id_idx   on audit_log (org_id);
create index audit_log_at_brin_idx  on audit_log using brin (at);

-- =====================================
-- 5. Triggers
-- =====================================
create trigger set_updated_at_orgs       before update on orgs       for each row execute function set_updated_at();
create trigger set_updated_at_users      before update on users      for each row execute function set_updated_at();
create trigger set_updated_at_customers  before update on customers  for each row execute function set_updated_at();
create trigger set_updated_at_jobs       before update on jobs       for each row execute function set_updated_at();
create trigger set_updated_at_quotes     before update on quotes     for each row execute function set_updated_at();

create or replace function public.handle_new_user()
returns trigger language plpgsql security definer set search_path = '' as $$
begin
  insert into public.users (id, org_id, email, role)
  values (new.id, (new.raw_app_meta_data -> 'org_id')::uuid, new.email, coalesce(new.raw_app_meta_data ->> 'role', 'member'));
  return new;
end;
$$;
create trigger on_auth_user_created after insert on auth.users for each row execute function handle_new_user();

-- =====================================
-- 6. RLS
-- =====================================
alter table orgs enable row level security;
alter table users enable row level security;
alter table customers enable row level security;
alter table jobs enable row level security;
alter table quotes enable row level security;
alter table line_items enable row level security;
alter table attachments enable row level security;
alter table audit_log enable row level security;

-- (Policies follow the patterns documented in rls-policy-designer example)
-- ... (truncated here — see /database-design:rls-policy-designer example for full bundle)
```

---

## Companion Files

- `supabase/migrations/20260520120000_initial_bootstrap.sql` — the bootstrap above
- `supabase/seed.sql` — one demo org + 2 users + 5 customers + 3 jobs for `supabase db reset`
- `types/supabase.ts` — regenerate via `supabase gen types typescript --linked > types/supabase.ts`
- `README-database.md` — apply via `supabase db push`; what to expect on first run

---

## Advisor Checks

After applying:

1. **Security advisor:** `supabase advisors list --type security` (or Studio → Database → Advisors)
   - Expect: no warnings (all public tables have RLS; helper functions have search_path = '')
2. **Performance advisor:** `supabase advisors list --type performance`
   - Expect: possibly "missing index" warnings only on tables we haven't yet seeded — re-run after demo data is in

If any new warnings appear, fix before opening to traffic.
