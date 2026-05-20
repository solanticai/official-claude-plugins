# Audit — supabase-schema-bootstrap

**Date:** 20/05/2026
**Path:** `engineering/database-design/skills/supabase-schema-bootstrap`
**Files reviewed:** SKILL.md (163 lines), templates/output-template.md (116 lines), examples/example-output.md (263 lines), LICENSE.txt. No `reference.md` — not required at this size; SKILL.md is well under 500 lines.

---

## Scores (115 pts total)

| # | Dimension | Score | Notes |
|---|-----------|-------|-------|
| 1 | Metadata & Frontmatter (10) | 9 | Valid YAML, kebab name, description 244 chars front-loaded, `effort: high`, `argument-hint` present (SKILL.md:1-7). Missing `allowed-tools: ... Bash` though Phase 4 implies CLI commands — minor. |
| 2 | Scope & Purpose (15) | 14 | Clear: new-project bootstrap; explicit guard for inheriting projects (SKILL.md:157). Wraps sibling skills cleanly. |
| 3 | Conciseness (10) | 10 | 163 lines, no fluff, no over-explanation. |
| 4 | Architecture / Phase Flow (15) | 14 | Six phases, sequential, each with purpose. Phase 6 is thin (just "save as schema-bootstrap.md") — could merge into Phase 5. |
| 5 | Content Quality & Correctness (25) | 22 | See special-criteria table below. Strong on conventions; one notable gap on numeric for money in template. |
| 6 | Tool Usage (10) | 8 | Declares Read/Write/Edit (SKILL.md:5, 123). Mentions `supabase` CLI commands without listing Bash — runtime mismatch. |
| 7 | Testing / Examples (15) | 13 | Example is realistic and detailed (jobs/quotes AU SaaS). RLS policies truncated with pointer to sibling skill (example:238-239) — acceptable given wrapper intent but loses self-containment. |
| 8 | Standards (AusE, markdown, evidence) (15) | 14 | AusE confirmed ("organisation", "behavioural", "ap-southeast-2"). Markdown clean. Date format dd/mm/yyyy in example. |

**Total: 104 / 115 → Grade A (just over the A threshold).**

---

## Special-Criteria Check

| Criterion | Status | Evidence |
|-----------|--------|----------|
| (a) RLS enabled for every table | PASS | SKILL.md:144 ("Every table has RLS enabled. No exceptions"); example:229-236 alters all 8 tables. |
| (b) `updated_at` + trigger pattern | PASS | SKILL.md:145, helper fn at template:61-67 and example:86-92; triggers attached example:210-214. Caveat: `line_items`, `attachments`, `audit_log` omit `updated_at` (example:161-189) — defensible (append-only / immutable) but not called out. |
| (c) FK columns indexed | PASS | SKILL.md:146; example indexes cover users.org_id, customers.org_id, jobs.org_id, jobs.owner_id, jobs.customer_id (MISSING), quotes.job_id, line_items.quote_id, attachments.job_id, attachments.uploader_id (MISSING), audit_log.org_id, audit_log.user_id (MISSING) (example:194-205). Three FKs lack indexes — partial pass. |
| (d) `gen_random_uuid()` / pgcrypto | PASS | Extension created template:57, example:80; PKs use `gen_random_uuid()` throughout (example:113, 131, 141, 152, 162, 172, 181). |
| (e) `timestamptz` UTC | PASS | All timestamps `timestamptz default now()` (example:116-117, 126, 137, 147, 157, 168, 177, 188). SKILL.md:148 mandates UTC. |
| (f) `numeric` for money | PASS | `total_aud numeric(12,2)`, `unit_price_aud numeric(12,2)` (example:155, 166-167). Rule stated SKILL.md:149. Template skeleton (template:53-95) does not mention money columns — minor template gap. |

---

## Strengths

- Wrapper pattern is honest: defers RLS/indexes/ERD detail to sibling skills via `[[…]]` references rather than duplicating.
- `auth.current_org_id()` / `auth.is_admin_or_owner()` helpers (example:94-107) with `security definer` + `set search_path = ''` follow Supabase hardening guidance.
- AU data-sovereignty signalled (region note, ABN field, AUD-suffixed money columns).
- Advisor-checks phase converts skill output into a Supabase Studio verification flow.

## Weaknesses

- RLS policies themselves are truncated in the example (example:238-239) — a bootstrap output that ships truncated policies is not directly applicable; readers must cross-reference rls-policy-designer.
- Three FK columns lack indexes in the example (`jobs.customer_id`, `attachments.uploader_id`, `audit_log.user_id`) despite the rule on SKILL.md:146.
- `Bash` not declared in `allowed-tools` though `supabase advisors list`, `supabase db push`, `supabase gen types` are surfaced as user actions (Phase 5, Companion Files).
- Phase 6 ("Output: save as schema-bootstrap.md") is one line — should fold into Phase 5 or expand with naming/location convention.

---

## Top 3 P0 Fixes

1. **Complete the RLS policy block in the example** (example:238-239) — at minimum show the tenant-isolation + role-based + audit-log-insert policies inline rather than pointing out-of-skill. Bootstrap output must be self-applicable.
2. **Index all FK columns in the example** — add `jobs_customer_id_idx`, `attachments_uploader_id_idx`, `audit_log_user_id_idx` (example:194-205) to honour SKILL.md:146.
3. **Add `Bash` to `allowed-tools`** (SKILL.md:5) or explicitly mark the `supabase ...` CLI commands as user-side instructions, removing the runtime/declaration mismatch.

---

## Minor / Nice-to-Have

- Document why `line_items` / `attachments` / `audit_log` omit `updated_at` (immutability) — add a one-line behavioural note near SKILL.md:145.
- Add a money-column example (`numeric(p,s)`) to the bootstrap SQL skeleton in `templates/output-template.md` so the rule is enforced by the template, not only the example.
- Phase 6 could fold into Phase 5 and gain a deterministic filename convention.
- Consider noting `pg_stat_statements` requires Supabase project-level enablement (it is preinstalled but not always exposed) at example:81.
