# Skill Audit — rls-policy-designer

**Date:** 20/05/2026
**Path:** `engineering/database-design/skills/rls-policy-designer/`
**Auditor:** skill-evaluator

---

## Summary

| Dimension | Score | Max |
|---|---|---|
| 1. Metadata & Frontmatter | 13 | 15 |
| 2. Scope & Focus | 14 | 15 |
| 3. Conciseness | 14 | 15 |
| 4. Architecture & Files | 14 | 15 |
| 5. Content Quality | 15 | 15 |
| 6. Tools & Permissions | 9 | 10 |
| 7. Testing/Examples | 14 | 15 |
| 8. Standards (AusE, conventions) | 14 | 15 |
| **Total** | **107** | **115** |
| **Grade** | **A** | |

---

## Special Criteria Check

| Criterion | Status | Evidence |
|---|---|---|
| (a) All 4 actions covered (SELECT/INSERT/UPDATE/DELETE) | PASS | `SKILL.md:72,130`; `example-output.md:110-157` shows all 4 on `customers` and `jobs` |
| (b) `security definer set search_path = ''` | PASS | `SKILL.md:82-83,86,132`; `example-output.md:49-77` (3 helper fns) |
| (c) Test queries (positive/negative/admin) | PASS | `SKILL.md:93-97`; `example-output.md:229-258` covers all 3 |
| (d) RLS-filter columns indexed | PASS | `SKILL.md:134` rule + `reference.md:206-207`; `example-output.md:192-201` ships 8 indexes |

All four special criteria pass with documented enforcement and concrete examples.

---

## Dimension Notes

### 1. Metadata & Frontmatter (13/15)
- `name`, `description` (197 chars, front-loaded), `argument-hint`, `allowed-tools`, `effort: high` all present (`SKILL.md:1-7`).
- Minor: `description` reads well but could mention Postgres/Supabase explicitly within first 80 chars for retrieval; "RLS policy bundle" is jargon-leading. -2.

### 2. Scope & Focus (14/15)
- Tightly scoped to RLS bundle generation; 6 sequential phases, no scope creep (`SKILL.md:34-104`).
- Edge cases enumerated (`SKILL.md:140-147`). -1 for slight overlap with general schema design (reference patterns 12-13 stray into business logic).

### 3. Conciseness (14/15)
- SKILL.md is 148 lines (well under 500-line cap).
- Dense reference (211 lines) correctly extracted to `reference.md`. -1: phase 4 example function duplicated in example-output.md (minor).

### 4. Architecture & Files (14/15)
- All required files present: `SKILL.md`, `LICENSE.txt` (21 lines), `templates/output-template.md` (89 lines), `examples/example-output.md` (272 lines), `reference.md`.
- -1: no `scripts/` (acceptable — skill is generative).

### 5. Content Quality (15/15)
- 15 patterns in reference (`reference.md:5-187`), 8 pitfalls (`reference.md:191-200`), performance tips (`reference.md:204-211`).
- Behavioural rules are sharp and non-negotiable (`SKILL.md:128-137`).
- Example demonstrates role-based + tenant-isolated + inherited + audit patterns in one cohesive bundle.

### 6. Tools & Permissions (9/10)
- `allowed-tools: Read Write Edit` — minimal and correct (`SKILL.md:5`).
- -1: phase 1 calls `AskUserQuestion` (`SKILL.md:34`) but it isn't in `allowed-tools`.

### 7. Testing/Examples (14/15)
- Test SQL covers positive/negative/admin with realistic JWT claim injection (`example-output.md:231-258`).
- -1: no negative test for INSERT/UPDATE/DELETE blocked-write attempts (only SELECT visibility tested).

### 8. Standards (14/15)
- Australian English: "behaviour" (`SKILL.md:128`), "denormalisation" (`reference.md:165` — note: actually US "denormalisation" is acceptable AusE).
- snake_case identifiers throughout.
- -1: `reference.md:184-186` field-level view example has a SQL syntax error (`redacted_field as null` is invalid; should be `null as redacted_field`).

---

## Top 3 P0 Fixes

1. **Add `AskUserQuestion` to `allowed-tools`** in `SKILL.md:5` — phase 1 explicitly invokes it (`SKILL.md:34`) but the frontmatter only lists `Read Write Edit`. Without this the skill will error at runtime.
2. **Fix invalid SQL in field-level redaction pattern** at `reference.md:185` — change `redacted_field as null` to `null::text as redacted_field` (column-alias direction is reversed; will fail parse).
3. **Add a negative write test** to `templates/output-template.md:64-68` and `example-output.md:242-251` — currently only SELECT visibility is verified; cross-tenant INSERT/UPDATE/DELETE attempts must be proven to fail with `with check` violations (highest-value RLS regression catch).

---

## Verdict

Grade **A (107/115)**. Production-ready Supabase RLS skill with thorough pattern library, enforced security-definer hardening, and runnable test scaffolding. Three small fixes would push to 112+.
