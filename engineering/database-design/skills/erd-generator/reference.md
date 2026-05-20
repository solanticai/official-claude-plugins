# ERD Generator — Reference Material

## Mermaid ERD Syntax Cheatsheet

### Relationship lines

| Symbol | Meaning |
|--------|---------|
| `|o--|` | exactly one to zero-or-one |
| `||--|` | exactly one to exactly one |
| `||--o{` | exactly one to zero-or-many |
| `||--|{` | exactly one to one-or-many |
| `}o--o{` | zero-or-many to zero-or-many |
| `}|--|{` | one-or-many to one-or-many |

### Entity block

```mermaid
ENTITY {
  type column_name PK     # primary key
  type column_name FK     # foreign key
  type column_name UK     # unique
  type column_name "annotation"
}
```

---

## DBML Syntax (dbdiagram.io)

### Table

```dbml
Table users {
  id uuid [pk, default: `gen_random_uuid()`]
  email text [unique, not null]
  age int [note: 'years since birth']
}
```

### References (FK)

```dbml
Ref: users.org_id > orgs.id
Ref: users.org_id > orgs.id [delete: cascade]
Ref: posts.author_id > users.id [delete: set null]
```

### Composite key

```dbml
Table memberships {
  user_id uuid
  team_id uuid
  Indexes {
    (user_id, team_id) [pk]
  }
}
```

### Enums

```dbml
Enum role {
  owner
  admin
  member
}

Table users {
  role role [not null]
}
```

---

## Cardinality Quick Reference

| Pattern | Example | Cardinality |
|---------|---------|-------------|
| User has many tasks; task belongs to one user | classic FK | 1:N |
| User has one profile; profile belongs to one user | profile FK with unique | 1:1 |
| Student has many courses; course has many students | via enrollments table | M:N (junction) |
| Org has many users; user belongs to one org (tenant) | scoped FK | 1:N (with mandatory) |
| Comment can reply to another comment | self-referential FK | 1:N (self) |

---

## ON DELETE Behaviour

| Action | When to use |
|--------|-------------|
| `CASCADE` | Child cannot exist without parent (line_items without quote; users without org if hard-delete) |
| `RESTRICT` | Protective; force user to delete child explicitly first (orders if you don't want accidental loss) |
| `SET NULL` | Child can survive parent (orphan-OK), e.g. assigned_user_id set null if user deleted |
| `SET DEFAULT` | Rarely used; child gets a default replacement |
| `NO ACTION` | Default; behaves like RESTRICT but defers to end of statement |

---

## Soft-delete Pattern

```sql
-- Add to any table that needs retention / audit
alter table {{table}} add column deleted_at timestamptz;
create index {{table}}_active_idx on {{table}} (deleted_at) where deleted_at is null;
```

- Use partial index on `where deleted_at is null` for "active rows" queries
- Combine with RLS: `using (deleted_at is null)` so soft-deleted rows are invisible by default
- Don't combine ON DELETE CASCADE with soft-delete — pick one model per relationship

---

## Multi-tenant Patterns

| Pattern | When to use |
|---------|-------------|
| `org_id` on every business table | Standard for B2B SaaS; pairs with RLS using `org_id = (auth.jwt() -> 'org_id')::uuid` |
| Single shared `org_id` partitioning | When tenants are very different sizes; consider table partitioning on org_id |
| Separate schema per tenant | High-isolation requirement (B2G, healthcare); higher operational cost |
| Separate DB per tenant | Maximum isolation; very high cost; rarely worth it for SMB SaaS |
