# RLS Policies — {{project_name}}

**Date:** {{date_dd_mm_yyyy}}

---

## Access Model

- **Tenancy:** {{single/multi-org/per-user/role-based}}
- **Admin escape:** {{describe}}
- **Audit:** {{required/none}}
- **Read-share scope:** {{describe}}

---

## Pattern per Table

| Table | Pattern | Rationale |
|-------|---------|-----------|
| {{table}} | {{pattern}} | {{why}} |

---

## RLS SQL Bundle

```sql
-- Enable RLS
{{enable_statements}}

-- Helper functions
{{helper_functions}}

-- Policies per table
{{policies}}
```

---

## Admin Escape Pattern

```sql
-- Server-only operations bypass RLS via service_role.
-- service_role must never be exposed to client code.
-- Examples of server-only operations:
--   - Cron jobs / Edge Functions running scheduled work
--   - Admin dashboard backend
--   - Migrations
```

---

## Test Queries

### Positive tests (should succeed)

```sql
-- User X should see their own row
set local role authenticated;
set local "request.jwt.claim.sub" to '{{user_x_uuid}}';
select * from {{table}} where id = '{{row_user_x_owns}}'; -- expect: 1 row
```

### Negative tests (should fail or return empty)

```sql
-- User X should NOT see user Y's row
select * from {{table}} where id = '{{row_user_y_owns}}'; -- expect: 0 rows
```

### Admin tests (service_role bypasses)

```sql
set local role service_role;
select count(*) from {{table}}; -- expect: full count
```

---

## Common Pitfalls Checklist

- ☐ All 4 actions (SELECT, INSERT, UPDATE, DELETE) have explicit policies
- ☐ `with check` matches `using` for INSERT and UPDATE
- ☐ Helper functions use `security definer set search_path = ''`
- ☐ Columns used in RLS filters are indexed
- ☐ No recursive policies (no table referencing itself in `USING`)
- ☐ Service-role usage is server-side only; never in client
- ☐ Soft-delete handled in `USING` clause if applicable
- ☐ Multi-tenant: `org_id` in every policy expression
