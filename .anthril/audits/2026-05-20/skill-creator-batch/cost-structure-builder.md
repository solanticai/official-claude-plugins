# cost-structure-builder — Skill Audit

**Path:** `economics/business-economics/skills/cost-structure-builder/`
**Date:** 20/05/2026
**Grade:** A (105 / 115)

---

## Summary

Tight, well-scoped cost-modelling skill. Frontmatter complete, AU context baked in (super 11.5%, VIC payroll tax 4.85%, GST mentioned in Behavioural Rules), taxonomy is the canonical 4-class (Fixed / Variable / Step-fixed / Semi-variable), and the scale curve covers 1×/2×/5×/10× exactly as required. Example output is realistic and numerically coherent. Minor gaps: GST treatment is asserted in rules but not surfaced as an explicit line/section in the template, and there is no `reference.md` despite cross-references to other skills.

---

## Special Checks

- **(a) Taxonomy F/V/Step-fixed/Semi-variable** — PASS. Defined SKILL.md:44-48; applied in example:12-23.
- **(b) AU GST / payroll-tax** — PARTIAL. Payroll tax called out (SKILL.md:21, behavioural rule 4 at :111, example line :16). GST mentioned in system prompt (:21) and rule 4 (:111) but no dedicated GST row in template or example — easy to overlook in practice.
- **(c) Scale curve 1×/2×/5×/10×** — PASS. Template :42-45, example :58-61.

---

## Scoring

| Dim | Score | Notes |
|---|---|---|
| Discovery (20) | 18 | Description front-loads use case (SKILL.md:3); cross-refs to break-even and unit-economics skills (:13). Could add more keywords for activation. |
| Scope (15) | 15 | Single coherent job — cost structure → waterfall → scale curve. Tight. |
| Conciseness (15) | 15 | 125 lines, well under 500. No bloat. |
| Architecture (15) | 13 | 5-phase pipeline is clean (:31-83). No `reference.md`; the cross-skill links suggest one could host a glossary or scaling-curve heuristics, but skill is small enough to defend the choice. |
| Content (15) | 14 | Excellent behavioural rules (:107-113), good edge cases (:117-124). GST treatment could be more concrete (% rate, registration threshold, capex GST credit). |
| Tool (10) | 10 | `Read Write Edit` only — appropriate (:5). No overreach. |
| Testing (7) | 7 | Strong realistic example with negative operating margin, step-jump table, sensitivity quadrant, recommendations. |
| Standards (3) | 3 | AU English, AUD, kebab-case name, frontmatter compliant. |
| Activation (10) | 6 | Description is descriptive but lacks trigger keywords like "unit economics", "margin analysis", "fixed vs variable". No `paths` glob. |
| Anti-patterns (5) | 4 | One minor: behavioural rule 6 "No projections to 100× without dilution" (:113) — slightly cryptic phrasing for a directive. Otherwise clean. |
| **Total** | **105 / 115** | **Grade A** |

---

## Top 3 P0 Fixes

1. **Add explicit GST row in template + example.** SKILL.md:111 mandates GST inclusion but `templates/output-template.md` has no GST line in either the classification table or the waterfall. Add a row "GST (net effect / payable)" with notes on registration threshold ($75k turnover) and capex input credits. Currently a rule that the output format does not enforce — likely to be skipped in practice.

2. **Strengthen activation surface in description.** SKILL.md:3 reads as a feature list. Front-load triggers: "Use when modelling business cost structure, fixed vs variable cost analysis, contribution margin, or break-even scale curves." Adds "contribution margin" + "break-even" + "cost analysis" as discovery keywords without breaching 250-char limit.

3. **Tighten behavioural rule 6.** SKILL.md:113 "No projections to 100× without dilution" is jargon-y — "dilution" here likely means "non-linear cost dilution" but reads ambiguously alongside the equity sense. Rephrase: "Cap projections at 10× current volume — linear scaling assumptions break beyond that without re-modelling the org structure."

---

## Minor Improvements (P1)

- Consider a brief `reference.md` covering: AU super rate timeline (11.5% → 12% from 1 Jul 2025), state payroll-tax thresholds, GST registration rules. Currently the example hardcodes 11.5% (:13) and VIC 4.85% (:16) without source — would benefit from a lookup.
- Phase 4 (:66) asks for step-jump identification but doesn't tell the model to also compute the *cumulative* added cost — example handles this well (:67-73) but instruction could be sharper.
- `argument-hint: [business-snapshot]` (:4) is vague — could be `[business-model + cost-lines + current-volume + target-volume]` to prompt better intake.

---

## File References

- SKILL.md: 125 lines, frontmatter :1-7, system prompt :17-22, phases :31-83, behavioural rules :107-113, edge cases :117-124
- templates/output-template.md: 69 lines, classification :8-19, waterfall :23-34, scale curve :38-45, step triggers :49-53, sensitivity :57-61
- examples/example-output.md: 96 lines, realistic DTC skincare case, loss-making at 1× converging to $606k/mo profit at 10×
- LICENSE.txt: present
- reference.md: absent (defensible at this size)
