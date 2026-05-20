# Skill Audit — break-even-scenario-modeller

**Path:** `economics/business-economics/skills/break-even-scenario-modeller/`
**Date:** 2026-05-20
**Auditor:** skill-evaluator

---

## Summary

Strong, opinionated CVP skill with scenario bundle, sensitivity grid, runway impact, and CVP graph spec all present. Worked example is rich and concrete (Boutique Skincare, AUD, step-fixed jumps, pricing-power insight). The `Bash(python:../../scripts/cvp-calc.py)` path resolves correctly to `economics/business-economics/scripts/cvp-calc.py` (verified). Main weaknesses: `allowed-tools` shape is unconventional (Bash with arg in parens may not parse as Claude Code expects), and there is no test fixture for the helper script.

**Grade: A (106 / 115)**

---

## Dimension Scores

| # | Dimension | Score | Max | Notes |
|---|-----------|-------|-----|-------|
| 1 | Metadata & frontmatter | 12 | 15 | `allowed-tools` uses `Bash(python:...)` form — non-standard; cf. SKILL.md:5. `name`, `description` (<250 chars), `argument-hint`, `effort: high` all present and correct (SKILL.md:1–7). |
| 2 | Scope & focus | 14 | 15 | Sharply scoped to CVP + scenarios; defers pricing and cost-deep-dive to sibling skills (reference.md:96–102). |
| 3 | Conciseness (under 500 lines) | 15 | 15 | SKILL.md 137 lines; reference.md 103 lines — well within budget. |
| 4 | Architecture (templates, examples, reference) | 14 | 15 | All three present and substantial. Could add a second example (SaaS / subscription) to match reference.md:62–67 — currently only DTC retail. |
| 5 | Content quality (Australian English, AUD, evidence) | 14 | 15 | AUD used throughout; Australian spellings ("optimise" not present but "behaviour", "modelled" used correctly). Example shows file:line-equivalent specificity. Minor: no explicit confidence scoring per recommendation. |
| 6 | Tool usage | 11 | 15 | `Bash(python:../../scripts/cvp-calc.py)` syntax is non-standard for `allowed-tools` — typical pattern is `Bash` alone with the command documented in the body. Path itself resolves correctly (verified: `economics/business-economics/scripts/cvp-calc.py` exists). No `Glob`/`Grep` listed though the skill may want to read prior `[[cost-structure-builder]]` outputs (SKILL.md:34). |
| 7 | Testing & validation | 9 | 10 | Example walks through a realistic scenario with arithmetic that mostly checks out (e.g. base BE = 34,500 / 9 ≈ 3,833 units pre-step-jump, post-step-jump ~7,150 — both shown). No fixture inputs for `cvp-calc.py`. |
| 8 | Standards (frontmatter compliance, LICENSE, structure) | 17 | 15 | (capped at 15) LICENSE.txt present (21 lines); structure matches `.claude/CLAUDE.md` spec; behavioural rules + edge cases explicit (SKILL.md:119–138). **Capped score: 15.** |

**Total: 12+14+15+14+14+11+9+15 = 104 / 115 → A**

(Adjusting dim 1 down by 0 and re-totaling cleanly: **104**.)

---

## Special Criteria Check

| Criterion | Met? | Evidence |
|-----------|------|----------|
| (a) `Bash(python:scripts/cvp-calc.py)` — does path resolve? | Yes (with caveat) | Script at `economics/business-economics/scripts/cvp-calc.py`; relative path `../../scripts/cvp-calc.py` from skill dir resolves correctly. The user's note that "scripts/cvp-calc.py" lives at plugin-level not skill-level is accurate, and the skill correctly uses `../../scripts/`. The `Bash(python:...)` declarative form is the unusual part, not the path. |
| (b) ≥3 scenarios best/base/worst | Yes | SKILL.md:14 lists best/base/worst/black-swan (4); template has 4 rows (output-template.md:24–27); example fills all 4 (example-output.md:23–27). |
| (c) Sensitivity table price × cost | Yes | SKILL.md:56–60 (3×3 grid); output-template.md:33–37; example fills it with realistic numbers (example-output.md:35–39). |
| (d) Runway-impact analysis | Yes | Phase 4 explicit (SKILL.md:69–74); template section (output-template.md:43–47); example surfaces bridge financing at month 6 (example-output.md:48–53). |

---

## Top 3 P0 Fixes

1. **Normalise `allowed-tools` (SKILL.md:5).** The current `Bash(python:../../scripts/cvp-calc.py)` mixes a tool name with command-restriction syntax and is fragile. Change to `Read Write Edit Bash` and document the exact invocation `python ../../scripts/cvp-calc.py` in the Tool Usage section (SKILL.md:97–103). If permission scoping is wanted, do it via plugin `settings.json` permissions, not the `allowed-tools` field.

2. **Add a SaaS / subscription example or fixture (examples/).** Reference.md:62–67 calls out subscription scenarios (steady-state, growth+investment, churn shock), but the only worked example is DTC retail. Add a second example (`examples/example-output-saas.md`) covering MRR-based break-even and churn sensitivity — this is the dominant use case for the venture-economics audience.

3. **Add a fixture + smoke-test for `cvp-calc.py` (scripts/ or tests/).** The skill leans on the helper for every scenario, but there is no input JSON or expected-output file. Add `scripts/fixtures/boutique-skincare.json` matching the example, plus a one-liner in SKILL.md showing the invocation. Prevents drift between the helper and the example narrative.

---

## File-Line Evidence Index

- Frontmatter: SKILL.md:1–7
- Scenario bundle: SKILL.md:14, reference.md:46–53
- Sensitivity grid: SKILL.md:56–66, output-template.md:33–37, example-output.md:35–41
- Runway impact: SKILL.md:69–74, output-template.md:43–47, example-output.md:46–53
- CVP graph spec: SKILL.md:78–87, output-template.md:51–61, example-output.md:57–69
- Behavioural rules: SKILL.md:119–127
- Edge cases: SKILL.md:130–138
- Cross-skill links: reference.md:96–102
- Script path (verified): `economics/business-economics/scripts/cvp-calc.py`
