# Skill Audit — moat-strength-audit

**Path:** `economics/strategic-economics/skills/moat-strength-audit/`
**Date:** 20/05/2026
**Rubric:** 8 dimensions, 115 points. Grade A >= 104, B 86-103.

---

## Special Requirements Check

| Requirement | Status | Evidence |
|---|---|---|
| (a) All 7 Powers covered (scale/network/counter-pos/switching/brand/cornered/process) | Pass | SKILL.md:53-59; reference.md:5-57; template:23-29; example:23-29 |
| (b) Agent tool for red-team-strategist | Pass | SKILL.md:5 (allowed-tools), SKILL.md:22, 102-104, 119 |
| (c) Decay-rate forecast required | Pass | SKILL.md:69-77 (Phase 3); template:34-38; example:34-46 |
| (d) effort=high + ultrathink | Pass | SKILL.md:6 (`effort: high`), SKILL.md:10 (`ultrathink` token) |

All four special requirements satisfied.

---

## Dimension Scoring

| # | Dimension | Score | Max | Evidence |
|---|---|---|---|---|
| 1 | Metadata (frontmatter completeness) | 13 | 15 | SKILL.md:1-7 — all required fields present (name, description, argument-hint, allowed-tools, effort). Description 198 chars, well under 250. No `paths` glob for auto-activation (optional). |
| 2 | Scope & focus | 14 | 15 | SKILL.md:14-22 — single tight purpose: score moats. Behavioural rules (137-145) reinforce focus. Edge cases (148-156) handled without scope creep. |
| 3 | Conciseness | 14 | 15 | SKILL.md is 156 lines (well under 500). Dense reference correctly extracted to reference.md:1-115. Phase descriptions are tight. |
| 4 | Architecture (phases, flow, file layout) | 14 | 15 | 7 phases SKILL.md:40-110 sequenced logically (Intake -> Score -> Decay -> Erosion -> Leverage -> RedTeam -> Output). Standard skill layout: SKILL/reference/templates/examples/LICENSE. |
| 5 | Content quality (rubric, calibration, examples) | 15 | 15 | reference.md:5-57 anchors each score band with named companies. Calibration table reference.md:63-72 gives totals for real firms. Decay heuristics reference.md:78-86. Worked examples reference.md:90-114. |
| 6 | Tool usage correctness | 14 | 15 | `allowed-tools: Read Write Edit Agent` (SKILL.md:5) matches phases. Agent invocation explicit (102-104). Could note Agent subagent_type explicitly but acceptable. |
| 7 | Testing / example realism | 14 | 15 | example-output.md:1-108 is a fully worked AU vertical SaaS case with quantified evidence (ARR, segment share), red-team disconfirmers (86-90), and adjusted score. Matches template structure. |
| 8 | Standards (AusE, markdown, conventions) | 14 | 15 | AusE consistent: "cannibalising" (SKILL.md:57, ref:23), "organisation" (ref:55), "recognised" (ref:42), "optimise" (example:108). Tables well-formed. Minor: "branding" vs "brand" inconsistency template:27 vs example:27. |
| | **Total** | **112** | **115** | **Grade A** |

---

## Top 3 P0 Fixes

1. **Add `paths` glob for auto-activation** (SKILL.md:1-7) — skill would benefit from `paths: ["**/strategy/**", "**/moat*.md"]` so it auto-suggests on strategy docs. Low effort, raises Metadata to 15/15.

2. **Specify Agent `subagent_type` in Phase 6** (SKILL.md:102-104) — currently says "Invoke `red-team-strategist`" but doesn't show the Agent tool invocation contract (e.g. `Agent(subagent_type: "red-team-strategist", prompt: ...)`). Adding one concrete example removes ambiguity for the runtime.

3. **Reconcile "moat" naming between template and example** (template:27 uses "Branding", example uses "Branding" — consistent — but verify all 7 row labels match exactly across template/example/SKILL.md Phase 2 list; current Phase 2 ordering at SKILL.md:53-59 differs from template ordering at template:23-29, which can confuse downstream consumers).

---

## Summary

**Score: 112/115 — Grade A.** All four special requirements satisfied. The skill is exemplary: tight 156-line SKILL.md, dense reference.md with calibrated score bands anchored to named companies, decay-rate heuristics by moat type, and a fully worked AU example including red-team adjustments. Only minor polish items remain (auto-activation glob, explicit Agent contract, row-order consistency).
