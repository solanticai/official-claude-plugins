# Skill Audit — debt-knockout-plan

**Path:** `lifestyle/personal-finance/skills/debt-knockout-plan/`
**Date:** 2026-05-20
**Rubric:** 8 dims + Activation + Anti-patterns, /115

---

## Score Summary

| Dim | Pts | Score |
|-----|-----|-------|
| Discovery / Frontmatter | 20 | 17 |
| Scope / Boundaries | 15 | 14 |
| Conciseness | 15 | 14 |
| Architecture | 15 | 13 |
| Content Quality | 15 | 14 |
| Tool Usage | 10 | 9 |
| Testing / Examples | 7 | 6 |
| Standards (AusE, MIT) | 3 | 3 |
| Activation triggers | 10 | 8 |
| Anti-patterns avoided | 5 | 5 |
| **Total** | **115** | **103** |

**Grade: B (103/115)** — one point shy of A.

---

## Special Checks

| Check | Result | Evidence |
|-------|--------|----------|
| (a) ASIC disclaimer at top? | Partial — referenced not inlined | SKILL.md:15 references `commands/finance-disclaimer.md`; template:3 only shows generic "general information only" line, no ASIC/AFSL/Corporations Act wording. Example-output.md:3 same. |
| (b) NDH 1800 007 007 referenced? | Yes | SKILL.md:126; template:57; example:70 |
| (c) HECS-HELP separation called out? | Yes | SKILL.md:45–46, 123; edge case at SKILL.md:137 |
| (d) `Bash(python:...)` in allowed-tools? | Yes | SKILL.md:5 — `Bash(python:scripts/debt-payoff-calc.py)` |

---

## Scoring Detail

### Discovery / Frontmatter (17/20)
- Valid YAML, all required fields present (SKILL.md:1–7).
- `description` is 187 chars, front-loaded with "Compare avalanche vs snowball" — good.
- `argument-hint: [debt-list-csv]` matches Phase 1 expectations.
- `effort: medium` reasonable.
- **−3:** No `paths` glob for auto-activation on debt CSVs or `debts.csv`-like patterns; no `keywords` cue surfaced in description for BNPL / refinance / consolidation triggers.

### Scope / Boundaries (14/15)
- Clear non-goals: no moralising, no new-debt-without-flag, HECS-HELP separated, no BNPL consolidation (SKILL.md:78, 119–127).
- Hardship refer-out path explicit (NDH + Moneysmart).
- **−1:** ATO debt edge case (line 135) says "call the ATO" but doesn't draw a hard "this skill does not produce ATO payment-plan content" line.

### Conciseness (14/15)
- 139 lines, well under 500.
- Tables used appropriately; no padding.
- **−1:** Phase 5 "Output" duplicates the template structure — could be one line "render `templates/output-template.md`".

### Architecture (13/15)
- 5 phases, sequential, each with clear deliverable.
- Cross-skill link `[[money-map]]` for extra-capacity input (SKILL.md:51) — good integration.
- No `reference.md` — and arguably not needed at this length; not flagged.
- **−2:** Disclaimer is referenced by relative path `commands/finance-disclaimer.md` (SKILL.md:15) — Claude has no built-in mechanism to expand a slash-command reference inline. Template emits only the short disclaimer (template:3), so the full ASIC/AFSL block from finance-disclaimer.md:13–17 never reaches output.

### Content Quality (14/15)
- AU-specific: Afterpay/Zip, HECS-HELP indexed-not-interest, ATO debt, mortgage redraw/offset, Moneysmart, NDH.
- Behavioural staircase + celebration-under-$100 is a strong, distinctive feature.
- Refinance scan correctly flags revert-rate trap and unsecured→secured conversion.
- Example uses real AU lenders (Westpac, CommBank, MyState, Toyota Finance) with plausible APRs.
- **−1:** No mention of Australian Financial Complaints Authority (AFCA) for unresolved hardship disputes.

### Tool Usage (9/10)
- `Bash(python:scripts/debt-payoff-calc.py)` properly scoped (SKILL.md:5).
- Tool usage table (SKILL.md:111–115) maps tools to purpose.
- **−1:** Doesn't include `Glob` despite skill plausibly needing to discover an existing money-map output to pull extra-capacity from.

### Testing / Examples (6/7)
- Example (82 lines) is realistic: Riley, Brisbane, sole income, real lenders, plausible rates, with-BT staircase variant.
- Numbers internally consistent (totals, weighted APR, payoff math).
- **−1:** Only one example; no edge-case example (e.g., HECS-only, or all-arrears).

### Standards (3/3)
- AusE throughout ("non-judgemental", "behavioural", "optimise").
- LICENSE.txt present (MIT assumed — not opened but file exists).
- Plugin manifest conventions followed.

### Activation triggers (8/10)
- Description front-loads "avalanche vs snowball" — strong trigger.
- **−2:** No mention of common user phrasings ("pay off credit card", "consolidate debt", "BNPL stack") that would help auto-activation.

### Anti-patterns avoided (5/5)
- No moralising language.
- Disclaimer rule embedded as behavioural rule #1.
- Explicit refer-out for arrears.
- Explicit warning on unsecured→secured conversion.

---

## Top 3 P0 Fixes

1. **Inline the ASIC disclaimer block in the template** (template:3 and example-output.md:3). The current short line "General information only — not personal financial advice" omits the *Corporations Act 2001* / AFSL / authorised-representative wording from `commands/finance-disclaimer.md:13–17`. Claude will not expand the `commands/finance-disclaimer.md` reference automatically — every output ships under-disclosed. Fix: copy the full block into `templates/output-template.md` between the title and "Debt Inventory" section, then update example accordingly.

2. **Add `paths` glob + activation keywords to frontmatter** (SKILL.md:1–7). Add `paths: ["**/debts.csv", "**/debt-list.*"]` and surface trigger words ("consolidate", "BNPL", "balance transfer", "credit card debt") in description. Currently the skill only activates on explicit name match.

3. **Add a second example covering an edge case** (examples/). Either an all-HECS-HELP "no action" output or an in-arrears "refer to NDH first" output. The single Riley example doesn't exercise the documented edge cases at SKILL.md:131–138 — particularly the hardship refer-out, which is the highest-stakes behavioural rule in the skill.

---

## Notes

- `reference.md` absent — acceptable given SKILL.md is only 139 lines; flagging not required.
- `scripts/debt-payoff-calc.py` lives at plugin-level `lifestyle/personal-finance/scripts/`, not skill-level, which matches the pattern used by `retirement-projection.py` for `future-me-projection`. Consistent.
- Disclaimer-by-reference pattern is used by all 5 personal-finance skills — fix should be applied plugin-wide, not just here.
