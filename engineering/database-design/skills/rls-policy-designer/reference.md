# RLS Policy Designer — Reference Material

## RLS Pattern Library

### 1. Tenant-isolated (most common B2B SaaS)

```sql
create policy "tenant_isolated" on {{table}}
  for {{action}} to authenticated
  using (org_id = auth.current_org_id())
  with check (org_id = auth.current_org_id());
```

### 2. Owner-only

```sql
create policy "owner_only" on {{table}}
  for {{action}} to authenticated
  using (owner_id = auth.uid())
  with check (owner_id = auth.uid());
```

### 3. Role-based within tenant

```sql
create policy "role_based" on {{table}}
  for select to authenticated
  using (
    org_id = auth.current_org_id()
    and (auth.is_admin_or_owner() or owner_id = auth.uid())
  );
```

### 4. Collaborator-shared (via pivot)

```sql
create policy "shared" on {{table}}
  for select to authenticated
  using (
    exists (
      select 1 from collaborators
      where collaborators.resource_id = {{table}}.id
        and collaborators.user_id = auth.uid()
    )
  );
```

### 5. Audit-table (append-only)

```sql
-- Only INSERT and SELECT (admin) policies; no UPDATE / DELETE for authenticated
create policy "audit_insert" on audit_log
  for insert to authenticated
  with check (org_id = auth.current_org_id());

create policy "audit_select_admin" on audit_log
  for select to authenticated
  using (
    org_id = auth.current_org_id()
    and auth.is_admin_or_owner()
  );
-- No UPDATE / DELETE policies = no authenticated UPDATE/DELETE possible
```

### 6. Soft-delete-aware

```sql
create policy "active_only" on {{table}}
  for select to authenticated
  using (
    org_id = auth.current_org_id()
    and deleted_at is null
  );
```

### 7. Public read with private write

```sql
create policy "public_read" on {{table}}
  for select to anon
  using (visibility = 'public' and deleted_at is null);

create policy "owner_write" on {{table}}
  for {insert, update, delete} to authenticated
  using (owner_id = auth.uid())
  with check (owner_id = auth.uid());
```

### 8. Reference data (admin-controlled)

```sql
create policy "reference_read" on {{table}}
  for select to authenticated
  using (true);

-- No insert/update/delete via client; only via migration or service_role
```

### 9. Time-bounded access (e.g. trial)

```sql
create policy "active_trial" on {{table}}
  for select to authenticated
  using (
    org_id = auth.current_org_id()
    and exists (
      select 1 from subscriptions
      where subscriptions.org_id = {{table}}.org_id
        and subscriptions.status = 'active'
        and subscriptions.expires_at > now()
    )
  );
```

### 10. Inherited via parent (mirror parent's access)

```sql
create policy "inherit_from_parent" on child
  for select to authenticated
  using (
    exists (
      select 1 from parent
      where parent.id = child.parent_id
        and parent.org_id = auth.current_org_id()
    )
  );
```

### 11. Geographic restriction (rare)

```sql
create policy "region_restrict" on {{table}}
  for select to authenticated
  using (
    region = (auth.jwt() ->> 'region')
    or auth.is_admin_or_owner()
  );
```

### 12. Premium-tier-only

```sql
create policy "premium_feature" on premium_data
  for select to authenticated
  using (
    org_id = auth.current_org_id()
    and exists (
      select 1 from subscriptions
      where subscriptions.org_id = premium_data.org_id
        and subscriptions.tier in ('pro', 'enterprise')
    )
  );
```

### 13. Quota-limited

Combine RLS with a check function:

```sql
create policy "within_quota" on {{table}}
  for insert to authenticated
  with check (
    org_id = auth.current_org_id()
    and (select count(*) from {{table}} where org_id = auth.current_org_id()) < quota_limit()
  );
```

### 14. Mutually-exclusive role (e.g. either patient OR provider)

```sql
create policy "role_segregated" on {{table}}
  for select to authenticated
  using (
    (patient_id = auth.uid() and auth.current_role() = 'patient')
    or (provider_id = auth.uid() and auth.current_role() = 'provider')
  );
```

### 15. Field-level redaction (column-based)

Use a `security definer` view rather than RLS for column-level redaction:

```sql
create or replace view {{table}}_safe as
select id, public_field, redacted_field as null
from {{table}};
```

---

## Common Pitfalls

1. **Recursive RLS** — table A's policy queries table A → infinite recursion. Break with a security-definer function.
2. **Performance trap** — RLS-filter columns not indexed; queries scan tens of millions of rows.
3. **Service-role leaked to client** — bypasses all RLS; classic security incident.
4. **Anonymous role policies missing** — endpoint expects anon access but only `authenticated` policies exist → permission denied.
5. **`with check` and `using` mismatch** — INSERT succeeds but the same row immediately fails SELECT next page.
6. **JWT claim missing** — auth.current_org_id() returns null; default policies allow nothing OR (worse) allow everything depending on coalesce.
7. **Forgetting `for delete` policy** — DELETE silently fails or allows anyone with WRITE access.
8. **Not handling soft-delete in USING** — soft-deleted rows still visible to users.

---

## Performance Tips

- Index every column that appears in RLS `USING` or `WITH CHECK`
- For tenant-isolated tables: composite index `(org_id, [other filter cols])`
- Use `security definer set search_path = ''` to make helper functions IMMUTABLE-fast
- Avoid `exists(...)` subqueries in RLS where a direct FK check works
- Monitor query plans on the most-trafficked tables; RLS can turn O(log n) into O(n)
