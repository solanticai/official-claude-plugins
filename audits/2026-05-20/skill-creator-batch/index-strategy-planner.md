# Skill Audit — index-strategy-planner

**Path:** `engineering/database-design/skills/index-strategy-planner`
**Date:** 20/05/2026
**Auditor:** skill-evaluator

---

## Scorecard (115 pts)

| # | Dimension | Score | Max | Notes |
|---|-----------|------:|----:|-------|
| 1 | Metadata & Frontmatter | 14 | 15 | Valid frontmatter (SKILL.md:1-7); name/description/argument-hint/allowed-tools/effort all present; description 174 chars and front-loaded. Missing optional `paths` for auto-activation. |
| 2 | Scope & Focus | 14 | 15 | Tight focus on Postgres index strategy; six phases (Intake -> Diagnose -> Recommend -> Cost -> Drop -> Output) all on-topic. No scope drift. |
| 3 | Conciseness | 14 | 15 | SKILL.md 135 lines, well under 500. Dense reference correctly split to `reference.md`. Tiny duplication: index-type list at SKILL.md:58-66 partially mirrors reference.md:5-22 (could be one source). |
| 4 | Architecture | 14 | 15 | Standard layout (SKILL/reference/templates/examples/LICENSE). `reference.md` linked from Phase 3 (SKILL.md:53). Templates use `{{placeholders}}` correctly. |
| 5 | Content Quality | 15 | 15 | All four specials satisfied: (a) decision tree reference.md:5-22; (b) CONCURRENTLY rule SKILL.md:87, 118 + every example DDL uses it; (c) write-amp surfaced SKILL.md:74, 119, reference.md:115-126, example:44-54; (d) FK indexing reminder SKILL.md:134 + reference.md:153-165. Composite ordering (reference.md:98-111) and jsonb_path_ops (reference.md:67-80) included. |
| 6 | Tool Usage | 14 | 15 | `allowed-tools: Read Write Edit` matches the read-paste-write workflow (SKILL.md:99). No Bash/Grep needed since the user pastes EXPLAIN output. Could optionally include `Glob` for scanning existing migrations, but defensible omission. |
| 7 | Testing & Examples | 14 | 15 | Example (example-output.md) is realistic: five queries spanning B-tree partial, covering, BRIN+partial combo, GIN jsonb_path_ops, expression unique. Drop list with rationale. Verification queries included. No second example for a different scale/domain. |
| 8 | Standards Compliance | 14 | 15 | Australian English ("optimise", "behavioural" SKILL.md:115). MIT LICENSE present. Output saved as `index-strategy.md` (SKILL.md:93). Date format `dd/mm/yyyy` (example:3). Minor: template placeholder `{{date_dd_mm_yyyy}}` (output-template.md:3) and `{{n× speedup}}` use ASCII × — fine but inconsistent with placeholder style elsewhere. |
| **Total** | | **113** | **115** | **Grade A** |

---

## Special-Requirements Check

| Requirement | Status | Evidence |
|-------------|:------:|----------|
| (a) Index-type decision tree | PASS | reference.md:5-22 — complete tree covering equality, range, ORDER BY, LIKE prefix/suffix, full-text, JSONB, array, geometric, BRIN, expression, PK |
| (b) CONCURRENTLY rule for prod | PASS | SKILL.md:87 (drop), SKILL.md:118 (behavioural rule #2), example-output.md:23-27,36-38 (all DDL uses CONCURRENTLY) |
| (c) Write-amplification surfaced | PASS | Dedicated Phase 4 (SKILL.md:69-76), behavioural rule #3 (SKILL.md:119), reference.md:115-126 with concrete %, cost summary column in template (output-template.md:33-39) and example (example-output.md:44-54) |
| (d) FK columns indexed reminder | PASS | SKILL.md:134 (edge case #6) + reference.md:153-165 with cascading-delete rationale and DDL example |

---

## Strengths

- Phase 5 "Indexes to Drop" is rare and valuable — most index skills only add, never remove
- Cost Summary table forces explicit accounting of storage + write-amp before approval
- Sequencing section (drops first, partial before covering, ANALYZE, verify) is operationally sound
- Example demonstrates BRIN + partial-btree combo on the same column — sophisticated pattern most skills miss
- jsonb_path_ops vs jsonb_ops trade-off documented (reference.md:67-80)
- HOT-update nuance noted (reference.md:121) — write-amp is 0% when updated col isn't indexed

---

## Weaknesses

- No mention of `pg_stat_statements` setup steps (just assumed available)
- Composite-index "Left, Equality, Range" rule lives only in reference.md:98-111; not in SKILL.md edge cases despite being the #1 ordering mistake
- Drop list in example (example-output.md:33-39) includes "Defer drop until composite usage confirmed" — good caution, but the row is technically not a drop, mixing categories
- No guidance on `lock_timeout` / `statement_timeout` to wrap CONCURRENTLY operations (which still take ACCESS EXCLUSIVE briefly)
- No mention of `REINDEX CONCURRENTLY` for bloat remediation
- Estimated impact column uses fuzzy "50-200×" without showing how to verify — could direct user to compare actual vs planned rows in EXPLAIN ANALYZE

---

## Top 3 P0 Fixes

1. **Add `lock_timeout` guidance to CONCURRENTLY rule (SKILL.md:118).** `CREATE INDEX CONCURRENTLY` still grabs a brief lock and waits for in-flight transactions; in busy prod this can stall. Recommend `set lock_timeout = '5s';` before each CONCURRENTLY statement, and document the failure-and-cleanup path (the leftover INVALID index needs DROP INDEX CONCURRENTLY).

2. **Promote composite-column ordering rule from reference.md:98-111 to SKILL.md edge cases.** "Leftmost = equality, range = last" is the most common index-design mistake; burying it in reference.md means a hurried operator skips it. Add as a one-liner in the SKILL.md Behavioural Rules or Edge Cases block.

3. **Add a second, smaller-scale example.** Current example (example-output.md) is a multi-table 8M-row workload. A second example covering a low-write 50k-row table where the answer is "do nothing, seq scan is fine" would reinforce edge case #1 (SKILL.md:129) and prevent over-indexing on small tables — currently only stated as a rule, never demonstrated.

---

## Verdict

**Grade A (113/115).** Production-ready Postgres index-strategy skill. All four special requirements satisfied with strong evidence. Phase 5 (drop unused) and explicit write-amp accounting put it above typical index-tuning prompts. Address the three P0 fixes (lock_timeout, composite ordering promotion, second example) and it's effectively gold-standard.
