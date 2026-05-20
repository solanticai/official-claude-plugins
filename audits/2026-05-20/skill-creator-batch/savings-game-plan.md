# Skill Audit — savings-game-plan

**Path:** `lifestyle/personal-finance/skills/savings-game-plan`
**Date:** 2026-05-20
**Grade:** B (94/115)

---

## Special Checks

| Check | Result | Evidence |
|-------|--------|----------|
| (a) ASIC/general-advice disclaimer at TOP of template | PARTIAL — has "General information only — not personal financial advice" but no ASIC reference or AFSL caveat | `templates/output-template.md:3` |
| (b) AU super concessional cap ($30k current FY) referenced | YES — explicit and current | `SKILL.md:73` ("current $30,000/yr; check ATO for current FY"); example `examples/example-output.md:45` |
| (c) FHSS scheme referenced for house deposit | YES, with caps | `SKILL.md:61, 118` ($50k total / $15k/yr); example walks Mia scenario `examples/example-output.md:25, 42` |
| (d) `AskUserQuestion` in allowed-tools | NO — only `Read Write Edit` | `SKILL.md:5` |

---

## Dimension Scores

### Discovery (20)  — 16/20
- `name`, `description` (<250 char, AUD-anchored), `argument-hint`, `effort: medium` all present (`SKILL.md:1-7`).
- Description front-loads use case well (`SKILL.md:3`).
- Missing keywords/auto-activation; no `paths` field; no explicit trigger hints in description for "savings rate / sinking funds" power terms beyond first line.

### Scope (15)  — 13/15
- Tight single-purpose: design AUD savings rate + buckets + automation (`SKILL.md:9-13`).
- Cleanly references sibling skills `money-map`, `future-me-projection` (`SKILL.md:13`) — no overlap.
- Minor scope creep risk: behavioural rules touch on debt ordering (`SKILL.md:65`) without owning it.

### Conciseness (15)  — 14/15
- 130 lines — well under 500-line cap.
- No bloat; phases are tight; tables compress well.

### Architecture (15)  — 12/15
- Standard structure: SKILL.md, templates/, examples/, LICENSE.txt — present.
- No `reference.md` — acceptable given size, but FHSS rules + concessional cap + preservation-age detail are dense enough to warrant extraction.
- Mermaid in template is a nice touch (`templates/output-template.md:33-40`).
- Disclaimer link `commands/finance-disclaimer.md` (`SKILL.md:15`) — UNVERIFIED reference; broken link risk.

### Content (15)  — 13/15
- Phase logic is solid: target → allocation → automation → milestones (`SKILL.md:35-86`).
- AU specifics accurate: $30k concessional cap, FHSS $50k/$15k caps, brokerages list (`SKILL.md:21, 73, 118`).
- Edge cases (windfall, sole-trader, HECS, preservation age) (`SKILL.md:123-129`).
- Example output is realistic, AUD-denominated, FHSS-anchored (`examples/example-output.md:1-72`).
- Minor: HECS-HELP advice (`SKILL.md:129`) — current FY indexation rules may make voluntary repayment timing-sensitive; oversimplified.

### Tool (10)  — 7/10
- `allowed-tools: Read Write Edit` (`SKILL.md:5`) — appropriate for write-only output skill.
- Phase 1 Intake (`SKILL.md:35-41`) lists 5 questions but skill cannot interactively ask — `AskUserQuestion` should be in allowed-tools OR intake reframed as "assume from $ARGUMENTS or stub with placeholders". This is the central tool mismatch.

### Testing (7)  — 6/7
- One realistic example (Mia, Melbourne, FHSS path) covering the headline scenario (`examples/example-output.md`).
- No edge-case examples (windfall, sole-trader, preservation-age) despite being called out in SKILL.md.

### Standards (3)  — 3/3
- AusE throughout (optimise, behavioural) — `SKILL.md:23, 111`.
- MIT LICENSE present.

### Activation (10)  — 6/10
- Description is solid but no `paths` glob, no keyword field, no obvious trigger phrases for natural-language activation beyond "savings".
- Cross-skill `[[money-map]]` linking is good for discovery within plugin.

### Anti-patterns (5)  — 4/5
- No specific-product prescriptions in SKILL.md (rule at `SKILL.md:115`) — but example output names ING, Pearler, VGS, A200, CommSec etc. (`examples/example-output.md:37-45`). Inconsistency: skill says "categories not brands" yet example uses brands. Minor docking.
- Disclaimer present but weak (no ASIC reference, no AFSL note).

---

## Total: 94/115 → **Grade B**

---

## Top 3 P0 Fixes

1. **Strengthen disclaimer to ASIC-compliant general-advice wording.** Current `templates/output-template.md:3` ("General information only — not personal financial advice") should explicitly state: "This is general information only and does not take your objectives, financial situation or needs into account. Consider seeking advice from an AFSL-licensed adviser." Also verify `commands/finance-disclaimer.md` referenced at `SKILL.md:15` actually exists; if not, inline it.

2. **Resolve tool/intake mismatch.** Phase 1 (`SKILL.md:35-41`) prescribes 5 intake questions but `allowed-tools: Read Write Edit` (`SKILL.md:5`) cannot ask them. Either add `AskUserQuestion` to allowed-tools, or rewrite Phase 1 to "extract from $ARGUMENTS; stub `{{TBD}}` for missing fields and flag at top of output".

3. **Fix brand vs category inconsistency.** Behavioural rule 3 (`SKILL.md:115`) bans brand recommendations, yet `examples/example-output.md:37-45` names ING Savings Maximiser, Pearler, VGS, A200. Either soften the rule to "OK to illustrate with brand placeholders in examples; in production output reference categories" or scrub the example to neutral categories ("a high-interest savings account", "a low-cost broad-market ETF").

---

## Notes

- Mermaid automation diagram is a strong UX touch — keep.
- FHSS handling is the strongest part of this skill; example carries the load.
- Consider adding `reference.md` with: concessional cap history table, FHSS release mechanics, preservation-age table — would future-proof against ATO rate changes without editing SKILL.md.
