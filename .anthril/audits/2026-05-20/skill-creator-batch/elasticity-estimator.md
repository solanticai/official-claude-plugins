# Skill Audit — elasticity-estimator

**Path:** `economics/strategic-economics/skills/elasticity-estimator`
**Date:** 20/05/2026
**Rubric:** 8 dimensions, 115 pts total. A ≥ 104, B 86–103.

---

## Summary

Strong, methodologically honest skill that genuinely matches estimation method to data context. Decision tree (SKILL.md:50-58) covers historical / survey (PSM, Gabor-Granger, conjoint) / experimental / quasi cleanly. Hypothetical-bias caveat is present (SKILL.md:82, 115). Cross-links to `ab-test-designer`, `causal-impact-analyser`, `pricing-architecture-designer`, `experiment-readout-builder`, `break-even-scenario-modeller`. Missing only a direct `[[ab-test-designer]]` reference in the SKILL.md decision tree (example references it at week 1; SKILL.md does not). No `reference.md` — not needed at current density. Grade: A (105).

---

## Scores

| # | Dimension | Max | Score | Notes (file:line) |
|---|-----------|-----|-------|-------------------|
| 1 | Metadata & frontmatter | 10 | 10 | Valid YAML; description 215 chars; `effort: high`; kebab-case (SKILL.md:1-7). |
| 2 | Scope & description fit | 15 | 14 | Description front-loads method selection + N (SKILL.md:3). Slightly understates quasi-experimental scope. |
| 3 | Conciseness | 15 | 15 | 130 lines; well under 500. No bloat. |
| 4 | Architecture & phases | 15 | 14 | Five phases, clean flow (SKILL.md:38-88). Phase 3 spec terse; could template per-method N formulas. |
| 5 | Content quality | 20 | 18 | Decision tree is correct and honest (SKILL.md:50-58); behavioural rules call out hypothetical bias + endogeneity + pre-registration (SKILL.md:111-119); edge cases cover marketplace/bundle/promo/subscription (SKILL.md:122-129). Missing: link to `ab-test-designer` from the experimental branch of decision tree itself. |
| 6 | Tool usage | 10 | 10 | `Read Write Edit` only — appropriate (SKILL.md:5, 94). |
| 7 | Testing / examples | 15 | 14 | Example (B2B SaaS A/B price test) is realistic, well-specified, has SRM checks, 90-day post-window, references `ab-test-designer`, `experiment-readout-builder`, `pricing-architecture-designer` (example-output.md:41, 46). Only one example — survey-method or historical-regression example would strengthen coverage. |
| 8 | Standards & conventions | 15 | 14 | Australian English + AUD declared (SKILL.md:29); AU-specific caveat re sample representativeness (SKILL.md:118). Date format DD/MM/YYYY in example. Minor: `What to Do With the Result` block duplicated between template and example (template.md:62-67 vs example.md:74-79). |
| **Total** | | **115** | **109** | Grade: **A** |

---

## Special Checks

- **(a) Method-selection decision tree** — PRESENT and well-formed (SKILL.md:50-58). Covers historical regression, PSM, Gabor-Granger, conjoint, A/B experimental, quasi-experimental. Each has a clear trigger condition.
- **(b) Hypothetical-bias caveat for surveys** — PRESENT in both behavioural rules (SKILL.md:115 — "People overstate WTP by ~30–50%") and Phase 4 caveats (SKILL.md:82).
- **(c) Link to ab-test-designer for experimental** — PARTIAL. Referenced in example-output.md:41 ("use `[[ab-test-designer]]`") but NOT in SKILL.md decision-tree row for A/B (SKILL.md:56). Add the wikilink to the decision tree so users hit the cross-skill route from the recommendation directly.

---

## Top 3 P0 Fixes

1. **Add `[[ab-test-designer]]` wikilink to the A/B branch of the decision tree** (SKILL.md:56). Currently only the example surfaces the handoff — the SKILL itself should route. Change line to: `- **A/B price testing** — can experimentally vary price for new users → gold standard; design via [[ab-test-designer]]`.
2. **Add a per-method Required-N quick-reference** to Phase 3 (SKILL.md:64-71). Example: PSM ≥ 200, Gabor-Granger ≥ 150, conjoint ≥ 500, historical ≥ 24 monthly obs with ≥ 3 price levels, A/B per power calc. Currently the user has to derive N each time; the rubric requires N to be specified but the skill gives no anchor numbers.
3. **Add a non-experimental example** (historical regression on retail SKU data, or Van Westendorp survey for a pre-revenue product). The lone A/B example may anchor users toward experimental even when their data context calls for something else — the skill's core value is honest method-matching, so the example library should reflect that diversity.

---

## Notes

- No `reference.md`; not needed at current size (130 lines).
- LICENSE.txt present (assumed MIT — not re-read).
- `pricing-architecture-designer` and `break-even-scenario-modeller` cross-links are good but those skills should be verified to exist in the same plugin (out of scope for this audit).
