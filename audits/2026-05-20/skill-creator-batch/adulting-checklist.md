# Skill Audit — adulting-checklist

**Path:** `lifestyle/home-life-logistics/skills/adulting-checklist`
**Date:** 2026-05-20
**Grade:** B (95 / 115)

---

## Score Summary

| Dim | Score | Max |
|---|---|---|
| Discovery | 17 | 20 |
| Scope | 13 | 15 |
| Conciseness | 14 | 15 |
| Architecture | 12 | 15 |
| Content | 13 | 15 |
| Tool | 9 | 10 |
| Testing | 6 | 7 |
| Standards | 3 | 3 |
| Activation | 8 | 10 |
| Anti-patterns | 0 (deductions) | -5 |
| **Total** | **95** | **115** |

---

## Per-Dimension Findings

### Discovery (17/20)
- Frontmatter complete with `name`, `description`, `argument-hint`, `allowed-tools`, `effort` (`SKILL.md:1-7`).
- Description front-loaded with quarterly life-admin trigger, under 250 chars (`SKILL.md:3`).
- **Gap:** `argument-hint: [life-stage-and-pillars]` is OK but could be more discoverable (e.g. examples). No `paths` glob for auto-activation.
- No keywords / aliases pulling search traffic ("life admin", "quarterly review").

### Scope (13/15)
- Clean single-purpose skill: quarterly admin sweep. Doesn't bleed into home maintenance (links out via `[[home-tlc-calendar]]` at `SKILL.md:49`) or gifts (`templates/output-template.md:44`).
- **Gap:** Quarter Q1 (Mar) framed as "tax-year wrap-up" is misaligned — AU FY ends 30 June, so the actual wrap-up quarter is Q2 (Jun). See special check below.

### Conciseness (14/15)
- 101 lines total, well under 500 limit (`SKILL.md`).
- No bloat. Behavioural rules and edge cases are tight (`SKILL.md:83-101`).
- Minor: Phase 2 standard sweep could move to `reference.md` to slim further.

### Architecture (12/15)
- 4-phase structure (Intake -> Build -> Calendar -> Output) is sound (`SKILL.md:31-73`).
- **Gap 1:** `SKILL.md:54` references `reference.md` but no such file exists in directory listing. Broken reference — P0.
- **Gap 2:** No `scripts/` directory (acceptable for low-effort skill).
- Template + example both present and well-aligned.

### Content (13/15)
- Strong AU specificity: HECS indexation date (1 June, `templates/output-template.md:25`), super concessional cap ($30k, `examples/example-output.md:13`), 132 011 / 13 28 65 emergency numbers (`templates/output-template.md:76-77`).
- Example is realistic (Patel family, Sydney, dog rego, termite inspection) — `examples/example-output.md:60-68`.
- **Gap:** Doesn't surface ATO myDeductions app, single touch payroll, or ASIC company-officer obligations for self-employed.

### Tool Usage (9/10)
- `allowed-tools: Read Write Edit` — appropriate minimal set (`SKILL.md:5`).
- "Tool Usage" section reiterates (`SKILL.md:79`). Good.

### Testing (6/7)
- Example output is detailed, plausible, and follows template (`examples/example-output.md`).
- **Gap:** Only one example variant (partnered + kids). Missing single, retiree, single-parent variants — directly relevant given life-stage promise.

### Standards (3/3)
- Australian English throughout ("organiser", "optimise" not present but no US spellings detected).
- AUD reference at `SKILL.md:22`.
- LICENSE.txt present.

### Activation (8/10)
- `effort: low` matches a 101-line, write-only skill (`SKILL.md:6`).
- Description triggers on "life admin", "renewals", "quarterly".
- **Gap:** Could add `paths` activation (e.g. `**/adulting*.md`).

### Anti-patterns (0 deductions)
- No SQL/mailbox cruft, no engineering-team residue, no emojis.

---

## Special Checks

**(a) AU FY = 30 June aligned to Q1/Q2?** PARTIAL FAIL.
- `SKILL.md:62-65` labels Q1 (Mar) as "tax-year wrap-up" — but the AU FY hasn't ended yet in March. The actual wrap-up window is April–June (Q2). Template repeats the same framing (`templates/output-template.md:9, 20`). Suggest re-label: Q1 = "pre-EOFY prep (receipts, deductions logging)", Q2 = "EOFY wrap-up + new-FY init".
- Positive: rule "AU FY = June" called out (`SKILL.md:90`); EOFY super top-up by 30/06 listed (`templates/output-template.md:22`); HECS 1-June indexation flagged (`templates/output-template.md:25`).

**(b) Life-stage variants addressed?** PARTIAL.
- All four stages (single / partnered / family / retiree) listed in intake (`SKILL.md:33`) and edge cases (`SKILL.md:96-100`).
- **Only one example variant** (partnered + kids). No retiree, single, single-parent examples.

**(c) Will + EPOA 5-year review surfaced?** PASS.
- Behavioural rule 4: "Wills + EPOA reviewed every 5 years" (`SKILL.md:88`).
- Q3 checklist item with year-5 trigger (`templates/output-template.md:35`).
- Perpetual table row (`templates/output-template.md:68`).
- Example shows year-3 status (`examples/example-output.md:41`).
- Solid coverage.

---

## Top 3 P0 Fixes

1. **Fix broken `reference.md` reference** (`SKILL.md:54`) — either create the file with per-life-stage customisation tables, or remove the line and inline a short table for the four stages.
2. **Realign Q1/Q2 to AU FY** — Q1 (Mar) should be EOFY-prep (logging, last-minute deductions), Q2 (Jun) should be the actual wrap-up + lodgement window. Update `SKILL.md:62-63` and `templates/output-template.md:9, 20` headings.
3. **Add 2 more example outputs** — `examples/single-retiree.md` and `examples/single-parent.md` — to honour the life-stage promise and exercise edge cases at `SKILL.md:99-100`.

---

## Notes

- `reference.md` flagged as missing despite being referenced.
- Skill is well-scoped, AU-localised, and tight; main weaknesses are FY-quarter alignment and example variety.
