# Skill Audit — rainy-day-plan

**Path:** `lifestyle/personal-finance/skills/rainy-day-plan`
**Date:** 2026-05-20
**Grade:** A (108 / 115)

---

## Scores

| Dim | Score | Evidence |
|---|---|---|
| Discovery (20) | 19 | SKILL.md:3 description front-loads "Size a 6-month emergency buffer, audit insurance gaps (life/TPD/income/trauma), and build a layoff/illness/family-event playbook for AU households" — strong triggers; argument-hint:5 present; allowed-tools:5 minimal-correct. Minor: keywords for resilience/redundancy not explicit. |
| Scope (15) | 14 | Tight scope: buffer + insurance + 5 playbooks. SKILL.md:33-89 phases are bounded. Edge cases listed:122-128. No scope creep into investing/budgeting. |
| Conciseness (15) | 14 | SKILL.md 129 lines, well under 500. reference.md 109 lines holds the dense lookup. Tables compact. |
| Architecture (15) | 15 | Full canonical layout: SKILL.md + reference.md + templates/ + examples/ + LICENSE.txt. Reference extraction done well (Centrelink + hardship pathways pushed out of SKILL). |
| Content (15) | 14 | Concrete AU numbers, hotlines, channels, formulas (10× income, 75% IP). reference.md:1-108 covers definitions (own-vs-any occupation, MLS thresholds, PSI). Minor: no super early-release detail beyond mention example-output.md:56. |
| Tool (10) | 10 | allowed-tools `Read Write Edit` (SKILL.md:5) — minimal & correct; no over-grant. |
| Testing (7) | 6 | One realistic example (Hannah & Lucas, single-income, dependants) example-output.md:1-107 covers buffer sizing, gap analysis, 5 playbooks, top-3 actions. Only one example — a second persona (sole-trader or post-separation) would lift score. |
| Standards (3) | 3 | Australian English throughout (organisation, optimise n/a, "Centrelink", "super"). AUD. |
| Activation (10) | 9 | Description specifies AU + use case + concrete deliverables. argument-hint `[household-snapshot]` clear. Minor: no `paths` glob for auto-activation on finance files. |
| Anti-patterns (5) | 4 | No fearmongering (SKILL.md:118). Refer-to-adviser baked in (SKILL.md:113). Slight: SKILL.md:15 disclaimer-by-reference to `commands/finance-disclaimer.md` — that path is external to skill; template:3 inlines a fallback disclaimer so it's safe in practice. |

**Total: 108 / 115 → A**

---

## Special Checks

| Check | Result | Evidence |
|---|---|---|
| (a) ASIC disclaimer at top of template | PARTIAL | templates/output-template.md:3 says *"General information only — not personal financial advice. For insurance decisions, consult a licensed adviser."* Disclaimer is present and at top, but does not name ASIC / Moneysmart explicitly. SKILL.md:24 references ASIC/Moneysmart but the template does not. |
| (b) NDH 1800 007 007 + Lifeline 13 11 14 + 1800RESPECT 1800 737 732 in output | PASS | template:75 NDH, :79 Lifeline, :80 1800RESPECT; example mirrors at :98,:102,:103. |
| (c) Insurance gap rules (life/TPD/income/trauma) covered | PASS | SKILL.md:65-68 table; reference.md:5-33 detailed definitions including own-vs-any occupation, waiting/benefit periods, indemnity vs agreed value. |
| (d) Family-violence-aware language | PASS | SKILL.md:128 edge case for family violence with 1800RESPECT; example-output.md:77-79 separation playbook includes moving funds to sole-name and beneficiary updates; template:80 lists 1800RESPECT. Language is supportive, non-judgemental. |

---

## Top 3 Fixes (P0)

1. **Inline the full ASIC/Moneysmart disclaimer in the template** — templates/output-template.md:3 currently says "general information only" but does not name ASIC, Moneysmart, or note that insurance advice is regulated. SKILL.md:15 defers to `commands/finance-disclaimer.md` which lives outside the skill and may not be present when the skill ships standalone. Replace template:3 with the full canonical disclaimer (ASIC, AFSL/credit-licence note, Moneysmart referral) and drop the external reference from SKILL.md:15.

2. **Add a second example for a different persona** — examples/ contains only Hannah & Lucas (dual-adult, single-income, dependants). Add `example-sole-trader.md` covering 6–9 month buffer, IP outside super, PSI — these are flagged in SKILL.md:124-126 and reference.md but not demonstrated. Lifts Testing 6 → 7.

3. **Add `paths` glob for auto-activation** — SKILL.md frontmatter has no `paths` field. Add e.g. `paths: ["**/finances/**/*.md", "**/budget*.md"]` so the skill activates when a user opens a finance worksheet. Lifts Activation 9 → 10 and improves discoverability.

---

## Notes

- Strong skill overall; the AU-context depth (Centrelink, ATO, AFCA, lender hardship, super early-release) is genuinely useful and rarely seen.
- Behavioural rules (SKILL.md:111-118) are well-considered: friction the buffer, mental-health support mandatory, no fearmongering.
- The single biggest gap / least-cost fix framing (SKILL.md:73) forces an actionable verdict rather than a list of concerns — good design.
