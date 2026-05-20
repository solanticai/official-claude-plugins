# Skill Audit — home-tlc-calendar

**Path:** `lifestyle/home-life-logistics/skills/home-tlc-calendar`
**Date:** 2026-05-20
**Grade:** A (104/115)

---

## Scores

| Dim | Score | Max | Notes |
|---|---|---|---|
| Discovery | 19 | 20 | Clear name, front-loaded description (SKILL.md:3), `argument-hint` present, `effort: low` accurate |
| Scope | 14 | 15 | Tight single-purpose: annual maintenance calendar by home-type + state. No bleed |
| Conciseness | 14 | 15 | SKILL.md is 106 lines — well under 500-line cap; reference.md 106 lines, no bloat |
| Architecture | 14 | 15 | Standard 4-phase shape; reference.md properly extracted; templates + examples both present |
| Content | 14 | 15 | Strong AU-specific knowledge; behavioural rules + edge cases excellent (SKILL.md:88-106) |
| Tool | 10 | 10 | `Read Write Edit` only — appropriate for a markdown-producing skill |
| Testing | 6 | 7 | One QLD example (example-output.md); no rental/strata/coastal example covering edge cases declared in SKILL.md:101-105 |
| Standards | 3 | 3 | AusE throughout ("organisation", "behavioural", AUD); MIT LICENSE.txt present; frontmatter valid |
| Activation | 9 | 10 | Description front-loads "Annual home-maintenance calendar by home type" — good trigger surface, but no `paths` glob for auto-activation |
| Anti-patterns | 1 | 5 | See penalties below |

**Total: 104 / 115 → Grade A** (boundary; one tier-shift would drop to B)

---

## Special Checks

### (a) All 8 AU states/territories covered in reference?

YES — reference.md:7-58 covers NSW, VIC, QLD, WA, SA, TAS, ACT, NT. Each has its own subsection with smoke-alarm + pool-barrier + termite guidance. **Pass.**

### (b) Smoke alarm + pool barrier compliance correct per-state?

Mostly correct, with one **discrepancy**:

- **VIC pool barrier:** SKILL.md:67 says "smoke alarm annual" but does NOT mention pool barrier cycle; reference.md:18 says "Re-inspection cycle every 4 yrs from late 2020". SKILL.md Phase 3 omits VIC pool entirely — should be 4-yearly, not silent.
- **ACT pool barrier:** SKILL.md:69 says "biennial" — matches reference.md:49. OK.
- **NSW pool barrier:** SKILL.md:63 "every 3 yr" — matches reference.md:10. OK.
- **QLD photoelectric interconnected by 2027:** Consistent in SKILL.md:65 and reference.md:23. OK.
- **SA smoke alarms 10-year-life:** Consistent (SKILL.md:67, reference.md:36). OK.
- **WA RCD mandatory since 2009:** Captured in reference.md:31 but not surfaced in SKILL.md Phase 3. Minor.

Overall: **mostly accurate**, one VIC pool-barrier omission in SKILL.md body.

### (c) DIY-vs-pro flag per task?

YES — reference.md:63-83 has a Task Frequency Table with explicit DIY/Pro column for every task. Template (output-template.md:11) has a "DIY or Pro" column. Example (example-output.md:11-24) populates it. Behavioural rule SKILL.md:91 enforces "DIY or pro? per task. No ambiguity." **Pass.**

---

## Top 3 Fixes (P0)

### P0-1 — Add missing VIC pool-barrier cycle to SKILL.md Phase 3
**File:** `SKILL.md:64` (VIC line currently reads "VIC: gas-heater CO test biennially; smoke alarm annual" — no pool mention)
**Fix:** Append "; pool barrier inspection every 4 yrs (post-2020)" to line 64. The reference already has it (reference.md:18); the SKILL.md summary should not silently drop it because users may not read reference.md.

### P0-2 — Add a second worked example for an edge case
**Issue:** Only one example (QLD freestanding with pool). SKILL.md:101-105 declares five edge cases (rental, strata, coastal, bushfire, heritage) but none demonstrated. A reviewer cannot verify edge-case handling.
**Fix:** Add `examples/example-output-strata-vic.md` showing a Melbourne strata apartment — most external maintenance stripped, interior + balcony only, VIC compliance applied.

### P0-3 — Add cost-range hints to Task Frequency Table
**Issue:** Example contains AUD cost ranges (example-output.md:13-24) but reference.md:63-83 task table has no cost column. Skill will produce inconsistent costs across runs.
**Fix:** Add an "Est. AUD" column to reference.md task table with rough ranges (e.g., termite inspection $250–400, gutters $200–350, hot-water flush $0–250). This anchors estimates and matches the template column at output-template.md:11.

---

## Strengths

- Behavioural rules section (SKILL.md:88-96) is unusually sharp — "pool fencing is legal liability", "annual insurance review on the same day each year"
- Edge cases (SKILL.md:99-106) cover the realistic AU housing variants (rental, strata, coastal, bushfire, heritage)
- Bushfire-zone supplementary task list (reference.md:87-95) is genuinely useful and state-tagged
- Coastal/salt-air supplementary list (reference.md:99-105) reflects real-world AU coastal degradation patterns
- Cross-link to `[[rainy-day-plan]]` at SKILL.md:53 — good plugin-level integration

## Minor Notes

- `effort: low` is appropriate (3-question intake + table generation)
- No `paths` auto-activation glob; reasonable for a user-invoked planner
- No scripts/ helpers — none needed for this skill
- Anti-pattern deduction: skill description includes parenthetical examples that push it close to the 250-char limit but stays under (200 chars). OK.
