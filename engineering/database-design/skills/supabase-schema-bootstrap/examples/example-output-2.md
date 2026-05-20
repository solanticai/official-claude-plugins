# Schema Bootstrap — Minimal SaaS (small surface, full RLS bundle inlined)

**Date:** 20/05/2026
**Supabase region:** ap-southeast-2 (Sydney)

This is a deliberately smaller bootstrap than the multi-tenant Jobs-and-Quotes example — used to demonstrate the **complete RLS bundle inline**, not truncated. Use when you want to see exactly which policies + helper functions + indexes a working bootstrap ships.

---

## Domain Summary

- **Multi-tenant:** Yes — by `workspace_id`
- **Core entities:** workspaces, users, projects, tasks, comments
- **Access model:** Workspace-isolated; members read/write their workspace's resources; admins additionally manage workspace settings

---

## Tables

| Table | Purpose | Tenant column |
|-------|---------|---------------|
| workspaces | Tenant root | — |
| users | Workspace members | workspace_id |
| projects | Work containers | workspace_id |
| tasks | Items in projects | (via project_id) |
| comments | Discussion on tasks | (via task_id) |

---

## RLS Approach

| Table | Pattern |
|-------|---------|
| workspaces | Tenant root — members read; admins update |
| users | Tenant-isolated; self-update |
| projects | Tenant-isolated; all members read/write |
| tasks | Inherited via project_id |
| comments | Inherited via task_id; soft-delete-aware |

---

## Indexes Added

| Index | Purpose |
|-------|---------|
| users_workspace_id_idx | RLS filter |
| projects_workspace_id_idx | RLS filter |
| tasks_project_id_idx | FK + RLS via project |
| tasks_assignee_id_idx | Common filter for "my tasks" |
| comments_task_id_idx | FK + RLS via task |
| comments_active_idx | Partial index on `where deleted_at is null` |

---

## Triggers

| Trigger | Tables | Purpose |
|---------|--------|---------|
| set_updated_at | workspaces, users, projects, tasks, comments | Auto-update timestamp |
| handle_new_user | auth.users → public.users | Create public.users row on signup |

---

## Bootstrap SQL (complete + RLS bundle inlined)

```sql
-- =====================================
-- supabase/migrations/20260520120000_initial_bootstrap.sql
-- =====================================

-- 1. Extensions
create extension if not exists pgcrypto;

-- 2. Helper functions (all security definer with empty search_path)
create or replace function public.set_updated_at()
returns trigger
language plpgsql
security definer
set search_path = ''
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

create or replace function auth.current_workspace_id()
returns uuid
language sql
stable
security definer
set search_path = ''
as $$
  select (auth.jwt() -> 'app_metadata' -> 'workspace_id')::uuid
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

create or replace function auth.is_admin()
returns boolean
language sql
stable
security definer
set search_path = ''
as $$
  select auth.current_role() = 'admin'
$$;

-- 3. Tables
create table workspaces (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create table users (
  id uuid primary key references auth.users(id) on delete cascade,
  workspace_id uuid not null references workspaces(id) on delete cascade,
  email text not null,
  role text not null default 'member' check (role in ('admin', 'member')),
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create table projects (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid not null references workspaces(id) on delete cascade,
  name text not null,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create table tasks (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references projects(id) on delete cascade,
  assignee_id uuid references users(id) on delete set null,
  title text not null,
  status text not null default 'open' check (status in ('open', 'in_progress', 'done', 'cancelled')),
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create table comments (
  id uuid primary key default gen_random_uuid(),
  task_id uuid not null references tasks(id) on delete cascade,
  author_id uuid not null references users(id),
  body text not null,
  created_at timestamptz default now(),
  updated_at timestamptz default now(),
  deleted_at timestamptz
);

-- 4. Indexes
create index users_workspace_id_idx       on users (workspace_id);
create index projects_workspace_id_idx    on projects (workspace_id);
create index tasks_project_id_idx         on tasks (project_id);
create index tasks_assignee_id_idx        on tasks (assignee_id);
create index comments_task_id_idx         on comments (task_id);
create index comments_active_idx          on comments (task_id) where deleted_at is null;

-- 5. Triggers
create trigger set_updated_at_workspaces  before update on workspaces  for each row execute function set_updated_at();
create trigger set_updated_at_users       before update on users       for each row execute function set_updated_at();
create trigger set_updated_at_projects    before update on projects    for each row execute function set_updated_at();
create trigger set_updated_at_tasks       before update on tasks       for each row execute function set_updated_at();
create trigger set_updated_at_comments    before update on comments    for each row execute function set_updated_at();

create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = ''
as $$
begin
  insert into public.users (id, workspace_id, email, role)
  values (
    new.id,
    (new.raw_app_meta_data -> 'workspace_id')::uuid,
    new.email,
    coalesce(new.raw_app_meta_data ->> 'role', 'member')
  );
  return new;
end;
$$;

create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function handle_new_user();

-- 6. Enable RLS on all tables
alter table workspaces enable row level security;
alter table users      enable row level security;
alter table projects   enable row level security;
alter table tasks      enable row level security;
alter table comments   enable row level security;

-- 7. Policies — workspaces
create policy "workspaces_select" on workspaces
  for select to authenticated
  using (id = auth.current_workspace_id());

create policy "workspaces_update_admin" on workspaces
  for update to authenticated
  using (id = auth.current_workspace_id() and auth.is_admin())
  with check (id = auth.current_workspace_id() and auth.is_admin());

-- 8. Policies — users
create policy "users_select_same_workspace" on users
  for select to authenticated
  using (workspace_id = auth.current_workspace_id());

create policy "users_update_self" on users
  for update to authenticated
  using (id = auth.uid())
  with check (id = auth.uid() and workspace_id = auth.current_workspace_id());

-- 9. Policies — projects
create policy "projects_select" on projects
  for select to authenticated
  using (workspace_id = auth.current_workspace_id());

create policy "projects_insert" on projects
  for insert to authenticated
  with check (workspace_id = auth.current_workspace_id());

create policy "projects_update" on projects
  for update to authenticated
  using (workspace_id = auth.current_workspace_id())
  with check (workspace_id = auth.current_workspace_id());

create policy "projects_delete_admin" on projects
  for delete to authenticated
  using (workspace_id = auth.current_workspace_id() and auth.is_admin());

-- 10. Policies — tasks (inherit via project)
create policy "tasks_select" on tasks
  for select to authenticated
  using (
    exists (
      select 1 from projects
      where projects.id = tasks.project_id
        and projects.workspace_id = auth.current_workspace_id()
    )
  );

create policy "tasks_insert" on tasks
  for insert to authenticated
  with check (
    exists (
      select 1 from projects
      where projects.id = tasks.project_id
        and projects.workspace_id = auth.current_workspace_id()
    )
  );

create policy "tasks_update" on tasks
  for update to authenticated
  using (
    exists (
      select 1 from projects
      where projects.id = tasks.project_id
        and projects.workspace_id = auth.current_workspace_id()
    )
  )
  with check (
    exists (
      select 1 from projects
      where projects.id = tasks.project_id
        and projects.workspace_id = auth.current_workspace_id()
    )
  );

create policy "tasks_delete" on tasks
  for delete to authenticated
  using (
    exists (
      select 1 from projects
      where projects.id = tasks.project_id
        and projects.workspace_id = auth.current_workspace_id()
        and auth.is_admin()
    )
  );

-- 11. Policies — comments (inherit via task; soft-delete aware on select)
create policy "comments_select_active" on comments
  for select to authenticated
  using (
    deleted_at is null
    and exists (
      select 1 from tasks
      join projects on projects.id = tasks.project_id
      where tasks.id = comments.task_id
        and projects.workspace_id = auth.current_workspace_id()
    )
  );

create policy "comments_insert" on comments
  for insert to authenticated
  with check (
    author_id = auth.uid()
    and exists (
      select 1 from tasks
      join projects on projects.id = tasks.project_id
      where tasks.id = comments.task_id
        and projects.workspace_id = auth.current_workspace_id()
    )
  );

-- Soft-delete: only the author can "delete" (which is an update of deleted_at)
create policy "comments_soft_delete_own" on comments
  for update to authenticated
  using (author_id = auth.uid())
  with check (author_id = auth.uid());
```

---

## Companion Files

- `supabase/migrations/20260520120000_initial_bootstrap.sql` — the bootstrap above
- `supabase/seed.sql` — one demo workspace + 2 users + 1 project + 3 tasks for `supabase db reset`
- `types/supabase.ts` — regenerate via `supabase gen types typescript --linked > types/supabase.ts`
- `README-database.md` — apply via `supabase db push`

---

## Advisor Checks

After applying:

1. **Security advisor:** `supabase advisors list --type security` (or Studio → Database → Advisors)
   - Expect: clean — every table has RLS; all helpers have `search_path = ''`
2. **Performance advisor:** `supabase advisors list --type performance`
   - Expect: clean — every RLS-filter column is indexed; FK columns indexed

Run both before opening to traffic.
