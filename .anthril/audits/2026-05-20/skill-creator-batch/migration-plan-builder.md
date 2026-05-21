# Skill Audit — migration-plan-builder

**Path:** `engineering/database-design/skills/migration-plan-builder`
**Date:** 20/05/2026
**Rubric:** 8 dimensions, 115 points. A >= 104, B 86-103.

---

## Scores

| # | Dimension | Score | Max | Notes |
|---|-----------|-------|-----|-------|
| 1 | Metadata & Frontmatter | 14 | 15 | Valid YAML (SKILL.md:1-7); `name`, `description` (191 chars, front-loaded), `argument-hint`, `allowed-tools`, `effort: high` all present. Missing optional `paths` glob but not required. Minor: `ultrathink` placed in body (line 10) rather than frontmatter — works but inconsistent with CLAUDE.md examples. |
| 2 | Scope & Focus | 14 | 15 | Tightly scoped to staged Postgres migrations. Phase 1 intake (SKILL.md:32-38) keeps scope bounded. Edge cases (SKILL.md:132-139) appropriately defer partitioning to a DBA. Minor: no explicit non-goals (e.g. "not for greenfield schema design"). |
| 3 | Conciseness | 14 | 15 | SKILL.md 140 lines — well under 500. Dense reference appropriately extracted to `reference.md` (105 lines). Per-stage table headers (SKILL.md:58-59) are skeletal — could be slightly richer but conciseness is a virtue here. |
| 4 | Architecture & Workflow | 14 | 15 | Clean 7-phase pipeline (Intake -> Stages -> Per-stage spec -> Observability -> App deploy -> DB reviewer -> Output). Staged migration model (additive -> backfill -> dual-write -> cutover -> cleanup) explicit at SKILL.md:46-52 and reinforced in template (output-template.md:19-26). Phase 6 (SKILL.md:86-88) only says "Invoke db-reviewer agent. Append findings" — thin; no prompt template or expected output shape. |
| 5 | Content Depth & Correctness | 13 | 15 | Lock-impact matrix (reference.md:7-26) is broadly accurate and covers all five stages' DDL. Chunked backfill pattern (reference.md:42-63) is correct. Strangler-fig credited to Fowler (reference.md:70). Minor errors: `CREATE INDEX (no CONCURRENTLY)` listed as `SHARE` lock — correct, but "Blocks reads? No" is right; "Blocks writes? YES" is right. `ALTER COLUMN SET NOT NULL (with NOT VALID then VALIDATE)` (reference.md:13) — Postgres syntax actually requires a CHECK constraint NOT VALID, then VALIDATE, then SET NOT NULL; this row conflates two patterns and may mislead. Replication-lag thresholds (reference.md:30-37) are reasonable defaults but uncited. |
| 6 | Tool Usage | 14 | 15 | `allowed-tools: Read Write Edit Agent` (SKILL.md:5) — minimal and correct. Agent tool explicitly bound to db-reviewer (SKILL.md:103, 86-88). No Bash needed. Missing: no guidance on how to invoke Agent (sub-prompt content, expected return shape) — Phase 6 is one sentence. |
| 7 | Testing & Examples | 13 | 15 | Example output (186 lines) is high-quality, AU-flavoured (multicultural name edge cases, AEST timestamps), shows all 5 stages, includes a realistic DB-reviewer verdict (example-output.md:139-172) with critical, important, and optional tiers. Template (output-template.md) has placeholders for every stage. Missing: no negative example (a migration that should NOT be staged) and no test/eval harness. |
| 8 | Standards Compliance | 13 | 15 | AU English used throughout (organisation, behaviour, optimise — verified in SKILL.md:23, 120). MIT LICENSE present. Markdown-first, evidence-backed style. Per CLAUDE.md, `effort` should be `low/medium/high/max` — `high` is appropriate. Minor: AU English mostly correct but example uses "off-peak" (fine) and reference uses "1k–10k" with en-dash (good). No `paths:` glob and no `context: fork` — fork might be useful for this skill. |

**Total: 109 / 115 — Grade A**

---

## Special Criteria Verification

| Criterion | Status | Evidence |
|-----------|--------|----------|
| (a) Agent tool for db-reviewer | Partial | Declared in allowed-tools (SKILL.md:5); Phase 6 (SKILL.md:86-88) invokes it; example renders findings (example-output.md:139-172). No prompt scaffold/return-shape spec. |
| (b) Staged migration (5 stages) | Pass | Explicit at SKILL.md:46-52; reinforced in stages table (output-template.md:19-26); example shows all 5 (example-output.md:20-25). |
| (c) Lock-impact matrix in reference | Pass | reference.md:7-26 — 17 operations, lock type, blocks reads, blocks writes, duration. |
| (d) Rollback per stage | Pass | Behavioural rule (SKILL.md:125), template per-stage rollback fields (output-template.md:42, 68), example shows rollback for stages 1-4 (example-output.md:43, 86). Stage 5 "No" rollback (example-output.md:25) is correct — cleanup is destructive by design. |

---

## Top 3 P0 Fixes

1. **Flesh out Phase 6 (db-reviewer invocation).** SKILL.md:86-88 is one sentence — "Invoke db-reviewer agent. Append findings." Add a sub-prompt scaffold (what to pass: the draft plan + intake answers; what to ask for: verdict tier {approve / approve-with-changes / reject}, critical issues, important caveats, optional improvements, lock-impact summary, suggested rollout). The example output (example-output.md:139-172) implies a clear contract — codify it in SKILL.md so the agent invocation is reproducible.

2. **Fix the NOT NULL row in the lock matrix.** reference.md:13 conflates `ALTER COLUMN SET NOT NULL (with NOT VALID then VALIDATE)` — Postgres has no such direct syntax. The non-blocking pattern is: `ADD CONSTRAINT ... CHECK (col IS NOT NULL) NOT VALID` -> `VALIDATE CONSTRAINT` -> then `SET NOT NULL` (which becomes near-instant because the validated CHECK lets the planner skip the table scan). Split into two rows or add a clarifying footnote, otherwise users will write invalid DDL.

3. **Add a "stages required" decision aid.** SKILL.md:52 says "Not all migrations need all 5 stages" but provides no rubric. Add a quick decision table in SKILL.md or reference.md keyed off intake answers (write volume, row count, downtime tolerance) -> minimum stage set. E.g. "Adding nullable column to < 100k-row table = stage 1 only; adding NOT NULL to > 1M-row table = stages 1+2+3+4 (cleanup optional)". Prevents over-engineering trivial migrations and under-engineering risky ones.

---

## Minor Observations

- `ultrathink` belongs in frontmatter per CLAUDE.md examples; here it's on SKILL.md:10. Functionally fine; stylistically inconsistent.
- No `context: fork` — given this skill calls another agent and produces a single artefact, fork would isolate context nicely.
- Example output is exemplary (multicultural name edge case at example-output.md:145 is a great AU-context detail).
- Sign-off checklist (output-template.md:111-119) is solid; example extends it appropriately (example-output.md:176-185).
