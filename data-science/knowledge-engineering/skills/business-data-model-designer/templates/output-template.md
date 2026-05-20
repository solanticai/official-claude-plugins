## Data Model — [Application Name]

### 1. Entity-Relationship Diagram

```
┌──────────────────┐       ┌──────────────────┐
│   {{entity_a}}   │       │   {{entity_b}}   │
├──────────────────┤       ├──────────────────┤
│ id (uuid, PK)    │──1:N──│ id (uuid, PK)    │
│ name (text)      │       │ {{entity_a}}_id   │
│ created_at       │       │ ...               │
│ updated_at       │       │ created_at        │
└──────────────────┘       └──────────────────┘
```

<!-- Text-based ERD showing all tables, columns, primary keys, and relationships. -->
<!-- Use 1:1, 1:N, N:M notation. Show junction tables for many-to-many. -->

---

### 2. Migration SQL

```sql
-- ============================================================
-- Migration: {{migration_name}}
-- Description: {{what this migration creates}}
-- ============================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enum types
CREATE TYPE {{enum_name}} AS ENUM ('{{value_1}}', '{{value_2}}', '{{value_3}}');

-- Table: {{table_name}}
CREATE TABLE IF NOT EXISTS {{table_name}} (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  {{column_name}} {{column_type}} {{constraints}},
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE {{table_name}} IS '{{table description}}';
COMMENT ON COLUMN {{table_name}}.{{column_name}} IS '{{column description}}';

-- Repeat for each table, ordered by dependency (parent tables first).
```

<!-- Migration must be copy-paste ready and idempotent (IF NOT EXISTS). -->
<!-- Order tables so foreign key references resolve correctly. -->

---

### 3. RLS Policies

```sql
-- Enable RLS on all client-accessible tables
ALTER TABLE {{table_name}} ENABLE ROW LEVEL SECURITY;

-- Policy: {{policy_name}}
-- Purpose: {{what this policy controls}}
CREATE POLICY "{{policy_name}}"
  ON {{table_name}}
  FOR {{SELECT / INSERT / UPDATE / DELETE / ALL}}
  TO authenticated
  USING ({{condition — e.g. user_id = auth.uid()}})
  WITH CHECK ({{condition for writes}});

-- Repeat for each table and operation.
```

<!-- Every table accessible from the client MUST have RLS enabled. -->
<!-- Use SECURITY DEFINER helper functions for complex org-based checks. -->

---

### 4. Performance Indexes

```sql
-- Foreign key indexes (PostgreSQL does not auto-create these)
CREATE INDEX IF NOT EXISTS idx_{{table}}_{{column}}
  ON {{table_name}} ({{column_name}});

-- Query-pattern indexes
CREATE INDEX IF NOT EXISTS idx_{{table}}_{{pattern_name}}
  ON {{table_name}} ({{columns used in frequent queries}});

-- RLS policy indexes (critical for performance)
CREATE INDEX IF NOT EXISTS idx_{{table}}_{{rls_column}}
  ON {{table_name}} ({{column used in RLS USING clause}});
```

<!-- Index all foreign key columns, columns used in RLS policies, and common query filters. -->

---

### 5. Seed Data Specification

```sql
-- Reference/default data for initial deployment

-- {{Enum or reference table description}}
INSERT INTO {{table_name}} (id, {{columns}})
VALUES
  (gen_random_uuid(), '{{value_1}}'),
  (gen_random_uuid(), '{{value_2}}')
ON CONFLICT DO NOTHING;

-- Repeat for each table that requires default data.
```

<!-- Include default roles, statuses, categories, or configuration records. -->
<!-- Use ON CONFLICT DO NOTHING to make seed scripts re-runnable. -->

---

### 6. Schema Documentation

| Table | Purpose | Key Relationships | RLS Strategy |
|-------|---------|-------------------|-------------|
| {{table_name}} | {{what it stores}} | {{FK to parent, referenced by child}} | {{user-owns / org-member / public-read}} |

**Evolution Notes:**
- To add a new entity: {{guidance on extending the schema}}
- To add a new role: {{guidance on role-based access changes}}
- To add a new relationship: {{guidance on junction tables and RLS updates}}

<!-- Summarise the full schema for quick reference. Include guidance for future extensions. -->
