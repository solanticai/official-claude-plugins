# Data Model: SaaS Project Management Application

**Application:** TaskFlow -- collaborative project management for Australian SMBs
**Database:** Supabase (PostgreSQL 15)
**Auth:** Supabase Auth (auth.users)

---

## Entity Relationship Diagram

```
┌──────────────┐       ┌──────────────────┐       ┌──────────────┐
│   profiles   │       │   workspaces     │       │   projects   │
├──────────────┤       ├──────────────────┤       ├──────────────┤
│ id (PK, FK)  │──┐    │ id (PK)          │──┐    │ id (PK)      │
│ full_name    │  │    │ name             │  │    │ workspace_id │──→ workspaces.id
│ avatar_url   │  │    │ slug             │  │    │ name         │
│ timezone     │  │    │ plan             │  │    │ description  │
│ created_at   │  │    │ owner_id (FK)    │──┘    │ status       │
│ updated_at   │  │    │ created_at       │       │ created_by   │──→ profiles.id
└──────────────┘  │    └──────────────────┘       │ created_at   │
                  │                                │ updated_at   │
                  │    ┌──────────────────┐       └──────────────┘
                  │    │ workspace_members │              │
                  │    ├──────────────────┤              │
                  └──→ │ workspace_id(FK) │              │
                       │ user_id (FK)     │       ┌──────────────┐
                       │ role             │       │    tasks      │
                       │ invited_at       │       ├──────────────┤
                       │ joined_at        │       │ id (PK)      │
                       └──────────────────┘       │ project_id   │──→ projects.id
                                                  │ title        │
                                                  │ description  │
                                                  │ status       │
                                                  │ priority     │
                                                  │ assignee_id  │──→ profiles.id
                                                  │ due_date     │
                                                  │ position     │
                                                  │ created_by   │──→ profiles.id
                                                  │ created_at   │
                                                  │ updated_at   │
                                                  └──────────────┘
                                                         │
                                                  ┌──────────────┐
                                                  │   comments   │
                                                  ├──────────────┤
                                                  │ id (PK)      │
                                                  │ task_id (FK) │──→ tasks.id
                                                  │ author_id    │──→ profiles.id
                                                  │ body         │
                                                  │ created_at   │
                                                  │ updated_at   │
                                                  └──────────────┘
```

---

## Migration: Profiles and Workspaces

```sql
-- 001_create_profiles_and_workspaces.sql

CREATE TABLE public.profiles (
  id          UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  full_name   TEXT NOT NULL,
  avatar_url  TEXT,
  timezone    TEXT NOT NULL DEFAULT 'Australia/Sydney',
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE public.workspaces (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name        TEXT NOT NULL,
  slug        TEXT NOT NULL UNIQUE,
  plan        TEXT NOT NULL DEFAULT 'free' CHECK (plan IN ('free', 'pro', 'business')),
  owner_id    UUID NOT NULL REFERENCES public.profiles(id) ON DELETE RESTRICT,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE public.workspace_members (
  workspace_id  UUID NOT NULL REFERENCES public.workspaces(id) ON DELETE CASCADE,
  user_id       UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  role          TEXT NOT NULL DEFAULT 'member' CHECK (role IN ('owner', 'admin', 'member', 'viewer')),
  invited_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  joined_at     TIMESTAMPTZ,
  PRIMARY KEY (workspace_id, user_id)
);

-- RLS policies
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view any profile"
  ON public.profiles FOR SELECT
  USING (true);

CREATE POLICY "Users can update own profile"
  ON public.profiles FOR UPDATE
  USING (auth.uid() = id);

ALTER TABLE public.workspaces ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Members can view their workspaces"
  ON public.workspaces FOR SELECT
  USING (
    id IN (SELECT workspace_id FROM public.workspace_members WHERE user_id = auth.uid())
  );

CREATE POLICY "Owners can update workspace"
  ON public.workspaces FOR UPDATE
  USING (owner_id = auth.uid());

ALTER TABLE public.workspace_members ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Members can view membership of their workspaces"
  ON public.workspace_members FOR SELECT
  USING (
    workspace_id IN (SELECT workspace_id FROM public.workspace_members WHERE user_id = auth.uid())
  );
```

---

## Migration: Projects and Tasks

```sql
-- 002_create_projects_and_tasks.sql

CREATE TABLE public.projects (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id  UUID NOT NULL REFERENCES public.workspaces(id) ON DELETE CASCADE,
  name          TEXT NOT NULL,
  description   TEXT,
  status        TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'archived', 'completed')),
  created_by    UUID NOT NULL REFERENCES public.profiles(id),
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE public.tasks (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id    UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
  title         TEXT NOT NULL,
  description   TEXT,
  status        TEXT NOT NULL DEFAULT 'todo' CHECK (status IN ('todo', 'in_progress', 'in_review', 'done')),
  priority      SMALLINT NOT NULL DEFAULT 2 CHECK (priority BETWEEN 0 AND 3),
  assignee_id   UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
  due_date      DATE,
  position       REAL NOT NULL DEFAULT 0,
  created_by    UUID NOT NULL REFERENCES public.profiles(id),
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE public.projects ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Workspace members can view projects"
  ON public.projects FOR SELECT
  USING (
    workspace_id IN (SELECT workspace_id FROM public.workspace_members WHERE user_id = auth.uid())
  );

CREATE POLICY "Members and above can create projects"
  ON public.projects FOR INSERT
  WITH CHECK (
    workspace_id IN (
      SELECT workspace_id FROM public.workspace_members
      WHERE user_id = auth.uid() AND role IN ('owner', 'admin', 'member')
    )
  );

ALTER TABLE public.tasks ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Workspace members can view tasks"
  ON public.tasks FOR SELECT
  USING (
    project_id IN (
      SELECT p.id FROM public.projects p
      JOIN public.workspace_members wm ON wm.workspace_id = p.workspace_id
      WHERE wm.user_id = auth.uid()
    )
  );

CREATE POLICY "Members can create and update tasks"
  ON public.tasks FOR ALL
  USING (
    project_id IN (
      SELECT p.id FROM public.projects p
      JOIN public.workspace_members wm ON wm.workspace_id = p.workspace_id
      WHERE wm.user_id = auth.uid() AND wm.role IN ('owner', 'admin', 'member')
    )
  );
```

---

## Migration: Comments

```sql
-- 003_create_comments.sql

CREATE TABLE public.comments (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  task_id     UUID NOT NULL REFERENCES public.tasks(id) ON DELETE CASCADE,
  author_id   UUID NOT NULL REFERENCES public.profiles(id),
  body        TEXT NOT NULL CHECK (char_length(body) > 0),
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE public.comments ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Workspace members can view comments"
  ON public.comments FOR SELECT
  USING (
    task_id IN (
      SELECT t.id FROM public.tasks t
      JOIN public.projects p ON p.id = t.project_id
      JOIN public.workspace_members wm ON wm.workspace_id = p.workspace_id
      WHERE wm.user_id = auth.uid()
    )
  );

CREATE POLICY "Authors can update own comments"
  ON public.comments FOR UPDATE
  USING (author_id = auth.uid());

CREATE POLICY "Members can create comments"
  ON public.comments FOR INSERT
  WITH CHECK (author_id = auth.uid());
```

---

## Index Recommendations

```sql
-- Workspace lookups by slug (unique already indexed)
-- Membership lookups -- PK covers (workspace_id, user_id)

-- Project listing within a workspace
CREATE INDEX idx_projects_workspace_id ON public.projects(workspace_id);

-- Task board queries: filter by project + status, sort by position
CREATE INDEX idx_tasks_project_status_position ON public.tasks(project_id, status, position);

-- Task assignment view: find all tasks for a user
CREATE INDEX idx_tasks_assignee_id ON public.tasks(assignee_id) WHERE assignee_id IS NOT NULL;

-- Tasks due soon (for dashboard widgets and notifications)
CREATE INDEX idx_tasks_due_date ON public.tasks(due_date) WHERE due_date IS NOT NULL AND status != 'done';

-- Comment thread loading
CREATE INDEX idx_comments_task_id_created ON public.comments(task_id, created_at);

-- Updated-at columns for sync/polling
CREATE INDEX idx_tasks_updated_at ON public.tasks(updated_at);
```

---

## Design Notes

- **Soft deletes** are not used; `archived` status on projects provides equivalent functionality without query complexity.
- **Task position** uses `REAL` to allow fractional ordering (insert between 1.0 and 2.0 -> 1.5) without rewriting all rows.
- **Timezone** defaults to `Australia/Sydney` since the primary user base is Australian SMBs.
- **Plan-based limits** (e.g., max projects per workspace) should be enforced at the application layer or via database functions, not CHECK constraints.
