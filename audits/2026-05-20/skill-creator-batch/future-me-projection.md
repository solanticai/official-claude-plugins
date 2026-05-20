# Skill Audit — future-me-projection

**Path:** `lifestyle/personal-finance/skills/future-me-projection`
**Date:** 2026-05-20
**Auditor:** skill-evaluator (batch)

## Final Score: 106 / 115 — Grade A

| Dimension | Score | Max |
|---|---|---|
| Discovery (metadata, name, description, triggers) | 19 | 20 |
| Scope (single purpose, bounded) | 14 | 15 |
| Conciseness (under 500 lines, dense ref split) | 15 | 15 |
| Architecture (phases, output, template/example) | 14 | 15 |
| Content (accuracy, AU super, drawdown math) | 14 | 15 |
| Tool usage (allowed-tools correctness) | 9 | 10 |
| Testing (example realism + reproducibility) | 6 | 7 |
| Standards (AusE, MIT, frontmatter) | 3 | 3 |
| Activation (argument-hint, $ARGUMENTS, intake) | 9 | 10 |
| Anti-patterns (no single-point, disclaimer, referral) | 3 | 5 |

---

## Special Checks

| Check | Result | Evidence |
|---|---|---|
| (a) ASIC disclaimer at top of output? | PARTIAL | Template line 3 has "General information only ... AFSL-licensed adviser" but no explicit ASIC RG 146/255 reference. SKILL.md L23 references external disclaimer file. |
| (b) projection-analyst agent invocation documented in Phase 5? | YES | SKILL.md L93-95 — agent path, effort, model specified. Agent file exists at `lifestyle/personal-finance/agents/projection-analyst.md`. |
| (c) Sequence-of-returns risk addressed? | YES — strong | Dedicated Phase 4 (SKILL.md L82-90), template section (L57-71), worked example (example-output.md L58-72, L77-79), reference (reference.md L65-68). |
| (d) `Agent` + `Bash(python:scripts/...)` in allowed-tools? | YES | SKILL.md L5: `allowed-tools: Read Write Edit Bash(python:scripts/retirement-projection.py) Agent`. Note: scoped `Bash(python:...)` form is unconventional — typical pattern is `Bash` alone. |

---

## Dimension Notes

### Discovery (19/20)
- Frontmatter complete, kebab-case name matches dir (L2).
- Description 196 chars, front-loads use case + agent mention (L3).
- `argument-hint: [age-balance-contributions]` clear (L4).
- `effort: high` appropriate for projection + agent invocation (L6).
- Minor: no `keywords`/`paths` for auto-activation; description could surface "FIRE" earlier.

### Scope (14/15)
- Single clear purpose: long-horizon retirement projection.
- Edge-cases enumerated (L136-143) including already-retired, pre-retiree, HNW.
- Slight scope creep with drawdown-rate sustainability and contribution-cap advice mixed in — acceptable given the planner persona.

### Conciseness (15/15)
- SKILL.md 143 lines (well under 500).
- Dense AU super rules + drawdown frameworks correctly extracted to `reference.md` (95 lines).
- Template 92 lines, example 118 lines — appropriately sized.

### Architecture (14/15)
- 6-phase workflow (L45-110): Intake → Projection → Sensitivity → Sequence-Risk → Agent → Output.
- Template + example both present and aligned.
- Minor: Phase 2 "Run the Projection (script)" assumes script exists but no input/output schema documented in SKILL.md (script does exist at `scripts/retirement-projection.py`).

### Content (14/15)
- AU-specific accuracy: $30k concessional, $1.9M TBC, Div 293, downsizer all correct in reference.md (L8-46).
- Drawdown frameworks: Trinity + Guyton-Klinger guard-rails correctly described (reference.md L51-62).
- Real vs nominal split enforced behaviourally (L126-128).
- Minor: SG rate "11.5%, rising to 12% on 01/07/2025" (reference.md L9) — by 2026 FY this should read "currently 12%".

### Tool usage (9/10)
- `Bash(python:scripts/retirement-projection.py)` is precisely scoped (good security posture) but unusual syntax — verify harness accepts this form. Most plugins use `Bash` then rely on permissions config.
- `Agent` correctly included for projection-analyst call.

### Testing (6/7)
- Example output (Nick, 38, Sydney) is realistic, fully populated, internally consistent.
- Numbers in sensitivity table (example L36-39) are plausible against base scenario.
- Minor: no unit-test/snapshot for the python script referenced.

### Standards (3/3)
- AusE: "optimise", "behaviour" — narrative is AusE; "salary sacrifice" / "concessional" correct AU terms.
- LICENSE.txt present.
- Frontmatter valid YAML.

### Activation (9/10)
- `$ARGUMENTS` used (L39), with fallback intake (L41).
- 6-question intake well-structured (L45-52).
- Argument-hint could be more guidance-rich (e.g., `[age,balance,contribution-rate]`).

### Anti-patterns (3/5)
- Behavioural Rules (L124-133) explicitly forbid single-point projections and require disclaimer + final referral — excellent.
- Concessional + TBC cap awareness baked into rules.
- DEDUCTION: disclaimer is light on ASIC-specific framing ("general advice warning"); referral language present but not legally framed as "general advice only".
- DEDUCTION: example-output.md duplicates the "Suggested questions for a licensed adviser" section twice (L96-102 within analyst notes, then L106-112 at end) — likely template drift.

---

## Top 3 Fixes (P0)

1. **Strengthen disclaimer to ASIC general-advice form.** Template L3 should read along the lines of: *"General advice only — this is not personal financial advice under the Corporations Act. It does not take into account your objectives, financial situation, or needs. Consider obtaining personal advice from an AFSL-licensed adviser before acting."* Then mirror in SKILL.md L23 and L132.

2. **Update SG rate reference for 2026 FY.** `reference.md` L9: change "currently 11.5%, rising to 12% on 01/07/2025" to "12% (from 01/07/2025)". Stale guidance erodes trust in the rest of the AU-super content.

3. **Resolve duplicate "Suggested questions" block in example-output.md.** Lines 96-102 (inside Analyst Notes) and 106-112 (standalone section) are near-duplicates. Either remove one or have the agent populate a distinct "personalised questions" list separate from the template's generic list — and clarify the contract in Phase 5.

## Nice-to-Have (P1)

- Document the `retirement-projection.py` input/output schema in SKILL.md Phase 2.
- Add `keywords: [retirement, super, FIRE, drawdown, sequence-risk]` to frontmatter for discovery.
- Consider snapshot test or fixture for the python script so worked example numbers can be regenerated.
- Confirm `Bash(python:scripts/...)` allow-tools syntax is honoured by the current Claude Code harness; fall back to `Bash` + settings.json permission if not.
