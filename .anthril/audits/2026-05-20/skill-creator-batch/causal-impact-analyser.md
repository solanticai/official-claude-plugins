# Skill Audit — causal-impact-analyser

**Path:** `data-science/experimentation/skills/causal-impact-analyser/`
**Date:** 2026-05-20
**Auditor:** skill-evaluator

---

## Score Summary

| Dim | Score | Max |
|-----|-------|-----|
| Discovery | 19 | 20 |
| Scope | 14 | 15 |
| Conciseness | 14 | 15 |
| Architecture | 14 | 15 |
| Content | 15 | 15 |
| Tool | 10 | 10 |
| Testing | 6 | 7 |
| Standards | 3 | 3 |
| Activation | 9 | 10 |
| Anti-patterns | 5 | 5 |
| **TOTAL** | **109** | **115** |

**Grade: A** (≥104)

---

## Dimension Notes

### Discovery (19/20)
- `name`, `description`, `argument-hint`, `effort` all present (SKILL.md:1-7).
- Description front-loads quasi-experimental designs and use case ("when randomised testing is infeasible") and explicitly mentions routing to stats-reviewer — strong activation signal (SKILL.md:3).
- 246 chars, within 250 limit. Could shave a few chars for buffer; minor.

### Scope (14/15)
- Sharp, single-purpose: quasi-experimental causal inference. Clear delineation from `ab-test-designer` (reference.md:8 — "Can you randomise? Yes → Use [[ab-test-designer]] instead").
- Covers DiD, SC, ITS, RDD, IV — appropriate breadth for the discipline (SKILL.md:48-52).

### Conciseness (14/15)
- SKILL.md is 153 lines — well under 500 limit (SKILL.md:1-153).
- Dense reference material correctly extracted to `reference.md` (86 lines).
- Some phase outputs (Phase 4-5) could merge — minor.

### Architecture (14/15)
- Standard structure present: SKILL.md, LICENSE.txt, templates/, examples/, reference.md.
- 7-phase flow is clear (SKILL.md:34-104). Phase 6 invokes stats-reviewer; Phase 7 saves output — clean handoff.
- Could add explicit reference.md link from SKILL.md body; currently implicit.

### Content (15/15)
- Phases are concrete and method-specific (SKILL.md:58-93).
- Behavioural Rules (SKILL.md:133-141) enforce identifying assumption, ≥2 robustness checks, cluster-robust SEs.
- Edge cases listed (SKILL.md:147-152) cover pre-trend failure, small donor pool, RDD manipulation, concurrent intervention, stakeholder bias.
- Reference.md provides per-method validity tests and a sensitivity-analysis menu (reference.md:19-85).

### Tool (10/10)
- `allowed-tools: Read Write Edit Agent` (SKILL.md:5) — **Agent IS present** for stats-reviewer routing. PASS special check (a).
- Tool table in SKILL.md:110-113 documents purpose.
- No unnecessary tools (no Bash/Grep/Glob bloat).

### Testing (6/7)
- Example output (`example-output.md`) is realistic: Sydney CBD parking levy, full DiD spec, 3 validity diagnostics, 4 robustness checks, stats-reviewer block populated.
- Template covers all 9 required sections (output-template.md:1-81).
- Could add a second example demonstrating synthetic control or RDD to show method-routing in practice. -1.

### Standards (3/3)
- Australian English ("organisation", "behaviour", "randomised", "analyse", "favourite") — confirmed throughout (SKILL.md:24; example-output.md:5 uses Australian context — Sydney/Melbourne).
- LICENSE.txt present.
- Frontmatter conforms to project CLAUDE.md spec.

### Activation (9/10)
- Description specifically calls out DiD/SC/ITS/RDD by name (SKILL.md:3) — high triggerability.
- Triggers on intervention/policy/rollout situations. Strong.
- Could add `paths` glob for data/analysis files; minor.

### Anti-patterns (5/5)
- No fabrication of stats; no skipping diagnostics; no implicit assumptions allowed (SKILL.md:135).
- "Don't conflate correlation with causation" enforced (SKILL.md:139).
- Stakeholder-preference bias check present (SKILL.md:152).

---

## Special Checks

| Check | Result | Evidence |
|-------|--------|----------|
| (a) Agent in allowed-tools for stats-reviewer | **PASS** | SKILL.md:5 — `allowed-tools: Read Write Edit Agent`; SKILL.md:98 invokes `stats-reviewer` |
| (b) Identifying assumption explicit + falsifiable | **PASS** | SKILL.md:58-68 dedicated phase; SKILL.md:135 behavioural rule; template line 25-29 |
| (c) ≥ 2 robustness checks required | **PASS** | SKILL.md:77-82, SKILL.md:136 ("≥ 2 robustness checks. Always."); example shows 4 (example-output.md:62-70) |
| (d) effort=max appropriate? | **PASS** | Quasi-experimental design requires extended reasoning across method selection, identifying-assumption framing, multiple diagnostics, and peer-review handoff. `ultrathink` flag (SKILL.md:10) reinforces. Justified. |

---

## Top 3 P0 Fixes

1. **Add reference.md pointer in SKILL.md body.** Phase 5 mentions diagnostics by method but reference.md (lines 19-58) has the comprehensive per-method validity-test catalogue. Add a "See reference.md for the full per-method test list" cross-reference in Phase 5 (around SKILL.md:93) so the analyst pulls in the right tests without re-deriving them.

2. **Add a second example for synthetic control or RDD.** The DiD example is excellent but readers may default to DiD because it's the only worked example. A short SC or RDD example (even 40 lines) would demonstrate method-routing in Phase 2.

3. **Tighten description by ~10 chars to leave buffer under 250.** Current: "Quasi-experimental design and analysis (diff-in-diff, synthetic control, ITS, regression discontinuity) for when randomised testing is infeasible. Routes to stats-reviewer." Consider dropping "and analysis" — implied by the field.

---

## Bottom Line

Strong skill. Method coverage is comprehensive, identifying-assumption and robustness-check enforcement is rigorous, stats-reviewer routing is correctly wired via the Agent tool, and the Sydney parking-levy example demonstrates the workflow end-to-end with Australian context. Minor polish only.
