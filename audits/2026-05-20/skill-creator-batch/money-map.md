# money-map — Skill Evaluation

**Path:** `lifestyle/personal-finance/skills/money-map`
**Date:** 2026-05-20

## Scores

| Dim | Pts | Score | Evidence |
|-----|-----|-------|----------|
| Discovery | 20 | 18 | Frontmatter complete (SKILL.md:1-7); description front-loaded with framework + AU context, 207 chars; argument-hint present. Missing `paths` for auto-activation. |
| Scope | 15 | 14 | Tight scope: budget + bank routing + sinking funds. Edge cases enumerated (SKILL.md:145-152). Refers to sibling `debt-knockout-plan` (SKILL.md:148) without overlap. |
| Conciseness | 15 | 15 | SKILL.md 153 lines (well under 500); reference.md 82 lines holds dense AU bank tables; template 91 lines; example 92 lines. Strong separation. |
| Architecture | 15 | 14 | Standard layout (SKILL.md / reference.md / templates/ / examples/ / LICENSE.txt). 5 distinct phases (SKILL.md:43-106). Disclaimer reference at plugin level (SKILL.md:21) — resolves to `lifestyle/personal-finance/commands/finance-disclaimer.md` (confirmed). |
| Content | 15 | 14 | AU-specific: HECS indexation 1 June (SKILL.md:150), Centrelink concessions (SKILL.md:149), bank product list (SKILL.md:27, reference.md:7-14), CTP/rego sinking funds (SKILL.md:98-99). Australian English ("optimisation" SKILL.md:152, "categorise" SKILL.md:67). FY context light — no explicit 30 June / EOFY framing despite tax discussion. |
| Tool | 10 | 6 | **P0 issue:** Phase 1 mandates AskUserQuestion (SKILL.md:43) but allowed-tools is `Read Write Edit` only (SKILL.md:5). AskUserQuestion missing. |
| Testing | 7 | 6 | One worked example provided (examples/example-output.md, 92 lines). Single scenario only — no irregular-income or sole-trader example despite Phase 2 covering them (SKILL.md:59-63). |
| Standards | 3 | 3 | LICENSE.txt present; AusE throughout; MIT-compatible. |
| Activation | 10 | 8 | Clear trigger keywords ("budget", "pay-day", "AUD", "AU bank"). No `paths` glob for auto-activation on `*budget*.md`. |
| Anti-patterns | 5 | 4 | Rule "No specific product recommendations" (SKILL.md:140) somewhat contradicted by reference.md:7-14 which lists named banks with feature endorsements ("Best UX"). Minor tension. |

**Total: 102/115 — Grade B (just under A threshold of 104)**

## Special Checks

- **(a) ASIC disclaimer at top of template:** PASS — template line 3: "General information only — not personal financial advice. Consult a licensed adviser." Not explicitly labelled "ASIC" but content aligns with ASIC MoneySmart phrasing.
- **(b) AskUserQuestion in allowed-tools:** FAIL — Phase 1 references "(5 questions via AskUserQuestion)" (SKILL.md:43) but allowed-tools (SKILL.md:5) only declares `Read Write Edit`. Skill will fail to elicit intake if invoked strictly.
- **(c) AU bank refs / FY context:** PARTIAL — bank refs strong (ING/Up/Macquarie/86 400/CommBank/NAB/ANZ/Westpac, SKILL.md:27). FY context thin — HECS indexation date mentioned (SKILL.md:150) but no 30 June EOFY review trigger, no super contribution caps timing, no PAYG variation reference.
- **(d) commands/finance-disclaimer.md reference:** RESOLVABLE — file exists at `lifestyle/personal-finance/commands/finance-disclaimer.md` (plugin-level, not skill-level). Reference path in SKILL.md:21 reads "commands/finance-disclaimer.md" which is correctly plugin-relative. Acceptable but worth noting the path is ambiguous without explicit plugin-root prefix.

## Top 3 Fixes (P0)

1. **Add `AskUserQuestion` to allowed-tools** — SKILL.md:5. Current `allowed-tools: Read Write Edit` is missing the tool Phase 1 explicitly requires (SKILL.md:43). Without this, intake silently degrades to free-text. Change to `Read Write Edit AskUserQuestion`.

2. **Add a second worked example for irregular-income / sole-trader scenario** — `examples/` currently holds only one example-output.md (92 lines). SKILL.md:59-63 promises profit-first for sole-traders and SKILL.md:147 specifies a different review cadence; neither path is demonstrated. Add `examples/example-output-sole-trader.md` showing 3-month income smoothing and quarterly review.

3. **Add EOFY / super-cap context to Phase 5 and template** — SKILL.md:95-106 covers monthly review but doesn't trigger an EOFY (30 June) annual review for: concessional super cap utilisation, deduction batching, PAYG instalment variation, HECS indexation pre-1-June consideration. Template (output-template.md:84-90) checklist is monthly-only — add an annual section.

## Minor / P1

- Add `paths` frontmatter for auto-activation (e.g., `*budget*.md`, `*money-map*`).
- Resolve product-recommendation tension: rule at SKILL.md:140 vs ranked bank list at reference.md:9 ("Best UX"). Either soften reference.md to descriptive-only, or relax the rule to "no endorsements, features only".
- Disclaimer reference SKILL.md:21 should clarify plugin-root resolution (e.g., "see plugin-level `commands/finance-disclaimer.md`") to avoid skill-level path confusion.
