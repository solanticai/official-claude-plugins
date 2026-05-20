# Schema Bootstrap — {{project_name}}

**Date:** {{date_dd_mm_yyyy}}
**Supabase region:** {{ap-southeast-2 or other}}

---

## Domain Summary

- **Multi-tenant:** {{Y/N}}
- **Core entities:** {{list}}
- **Access model:** {{summary}}

---

## Tables

| Table | Purpose | Tenant column | Notes |
|-------|---------|--------------|-------|
| orgs | Tenant root | — | |
| users | Org members | org_id | Mirror of auth.users |
| ... | | | |

---

## RLS Approach

| Table | Pattern | Reference |
|-------|---------|----------|
| {{table}} | {{pattern}} | `[[rls-policy-designer]]` reference.md |

---

## Indexes Added

| Index | Purpose |
|-------|---------|
| {{idx}} | {{purpose}} |

---

## Triggers

| Trigger | Tables | Purpose |
|---------|--------|---------|
| set_updated_at | all | Maintains updated_at automatically |
| audit_log_insert | sensitive tables | Appends to audit_log on write |

---

## Bootstrap SQL

```sql
-- supabase/migrations/{{timestamp}}_initial_bootstrap.sql

-- 1. Extensions
create extension if not exists pgcrypto;
create extension if not exists pg_stat_statements;

-- 2. Helper functions
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

-- 3. Tables
create table orgs (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- (... more tables ...)

-- 4. Indexes
create index ... on ...;

-- 5. Triggers
create trigger set_updated_at_orgs
  before update on orgs
  for each row execute function set_updated_at();

-- 6. RLS
alter table orgs enable row level security;
create policy orgs_select on orgs ... ;
```

---

## Companion Files

- `supabase/migrations/{{timestamp}}_initial_bootstrap.sql` — bootstrap
- `supabase/seed.sql` — minimal dev seed
- `types/supabase.ts` — regenerate via `supabase gen types typescript --linked > types/supabase.ts`
- `README-database.md` — apply/expect

---

## Advisor Checks

After applying:

1. **Security advisor:** `supabase advisors list --type security` (or Studio → Database → Advisors)
2. **Performance advisor:** `supabase advisors list --type performance`

Expect to fix any flagged issues before opening to traffic.
