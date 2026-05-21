# Skill Audit — competitive-dynamics-analyser

**Path:** `economics/strategic-economics/skills/competitive-dynamics-analyser/`
**Date:** 20/05/2026
**Auditor:** skill-evaluator
**Verdict:** **A (108/115)**

---

## Special Checks

| Check | Result | Evidence |
|-------|--------|----------|
| (a) `Agent` in allowed-tools for red-team-strategist | PASS | `SKILL.md:5` — `allowed-tools: Read Write Edit Agent` |
| (b) Porter 5 Forces + game theory referenced | PASS | `SKILL.md:14, 26, 50-62, 68-87`; `reference.md:3-44, 47-81` |
| (c) Nash equilibrium honesty rule present | PASS | `SKILL.md:87` ("painful answer 'price war'") + `SKILL.md:139` Rule 4 |
| (d) effort=high + ultrathink | PASS | `SKILL.md:6` effort: high; `SKILL.md:10` ultrathink |

---

## Scoring (8 dimensions, 115 pts)

| # | Dimension | Score | Max | Notes |
|---|-----------|-------|-----|-------|
| 1 | Metadata & Frontmatter | 14 | 15 | All required fields present (`SKILL.md:1-7`); description 196 chars, front-loaded; argument-hint clear; missing optional `paths` glob for auto-activation. |
| 2 | Scope & Focus | 15 | 15 | Tightly scoped to competitive-dynamics; Phase 1 enforces narrow market definition (`SKILL.md:42`); Behavioural Rule 1 reinforces (`SKILL.md:136`). |
| 3 | Conciseness | 14 | 15 | SKILL.md 153 lines — well under 500; dense reference correctly extracted to `reference.md` (119 lines); minor duplication between Phase output (line 105) and Output Format (line 122). |
| 4 | Architecture & Structure | 14 | 15 | Standard layout (SKILL.md, reference.md, templates/, examples/, LICENSE); 7 phases sequential and clear; edge cases enumerated (`SKILL.md:145-152`); reference.md not explicitly cross-linked from SKILL.md body. |
| 5 | Content Quality | 15 | 15 | Equilibrium library (Cournot/Bertrand/dominant-firm/collusive/winner-take-all/fragmented) in `reference.md:47-81`; AU-specific considerations (`reference.md:112-119`); counter-move patterns table; Nash honesty rule enforced. |
| 6 | Tool Usage | 14 | 15 | `Agent` declared and used in Phase 6 (`SKILL.md:99-101`); tool table maps purpose (`SKILL.md:113-116`); no Glob/Grep declared but skill is analytical — acceptable. Could specify Agent subtype hint. |
| 7 | Testing & Examples | 14 | 15 | Realistic example output (110 lines, AU SMB accounting) with all sections populated; template uses {{placeholders}} consistently; red-team section in example is genuine (`example-output.md:71-100`); no automated test script. |
| 8 | Standards Compliance | 8 | 10 | MIT licence present; Australian English throughout ("optimise", "behaviour", "commoditised"); AUD context; frontmatter compliant. Minor: no explicit version pin, no `paths` for auto-activation. |
| | **TOTAL** | **108** | **115** | **Grade A** (>=104) |

---

## Strengths

1. **Game-theory rigour without academic bloat.** The equilibrium pattern library (`reference.md:47-81`) names the dynamic (Cournot/Bertrand/dominant-firm) and ties each to real AU examples — operator can map their market in minutes.
2. **Nash honesty rule.** `SKILL.md:139` Rule 4 explicitly forbids motivated reasoning ("don't conclude 'compete on quality' if equilibrium is 'race to bottom'") — rare and load-bearing.
3. **Red-team baked in as a hard phase.** Phase 6 + Rule 5 (`SKILL.md:140`) make red-team non-optional; example output demonstrates substantive disconfirmation (`example-output.md:85-90`).
4. **AU-specific edge cases.** Two-sided market, regulated industry, single dominant player, emerging market, geographic+product, "we are dominant" — all enumerated (`SKILL.md:147-152`).

---

## Top 3 P0 Fixes

### P0-1 — Add `paths` glob for auto-activation
**Where:** `SKILL.md:1-7` frontmatter.
**Why:** Skill currently requires manual invocation. Add `paths: ["**/strategy/**", "**/competitive-*.md"]` so it suggests on relevant context.
**Effort:** 2 min.

### P0-2 — Cross-link reference.md from SKILL.md phases
**Where:** `SKILL.md:50` (Phase 2), `SKILL.md:66` (Phase 3).
**Why:** The scoring rubric and equilibrium library live in `reference.md` but Phases 2 and 3 don't reference it. Add `See reference.md "5 Forces Scoring Rubric"` and `See reference.md "Equilibrium Pattern Library"`.
**Effort:** 3 min.

### P0-3 — Deduplicate output spec
**Where:** `SKILL.md:105-107` (Phase 7) vs `SKILL.md:120-131` (Output Format section).
**Why:** Two near-identical specifications of the output. Either fold Phase 7 into "Output Format" or remove the bulleted list at `SKILL.md:124-130` (template already enumerates the sections).
**Effort:** 5 min.

---

## Minor Improvements (P1)

- Add `agent: red-team-strategist` hint near Phase 6 invocation, since the agent name matters.
- Add a one-line numeric anchor in Phase 2: "if Sum > 18, default recommendation is 'consider exit or category re-definition'".
- Consider a `scripts/` helper that takes 5-Forces JSON and renders the markdown table — repeatable usage.

---

## Conclusion

A high-quality, opinionated strategy skill that combines Porter's classical framework with explicit game-theory equilibrium prediction and a mandatory red-team gate. The Nash equilibrium honesty rule is the standout — it actively defends against motivated reasoning in strategy work. Three quick fixes lift this to a likely 113/115.
