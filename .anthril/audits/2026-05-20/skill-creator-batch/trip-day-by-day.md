# Skill Audit — trip-day-by-day

**Path:** `lifestyle/home-life-logistics/skills/trip-day-by-day`
**Date:** 2026-05-20
**Auditor:** skill-evaluator (batch)

## Score Summary

| Dim | Pts | Score |
|-----|-----|-------|
| Discovery (description quality, triggers, name) | 20 | 18 |
| Scope (single clear purpose, no overlap) | 15 | 14 |
| Conciseness (SKILL.md length, dense ref) | 15 | 14 |
| Architecture (file structure, split SKILL/ref) | 15 | 14 |
| Content (phases, rules, edge cases, examples) | 15 | 14 |
| Tool config (allowed-tools right-sized) | 10 | 10 |
| Testing (example realistic + complete) | 7 | 7 |
| Standards (frontmatter, AusE, MIT) | 3 | 3 |
| Activation (clear triggers / argument-hint) | 10 | 9 |
| Anti-patterns avoided | 5 | 5 |
| **TOTAL** | **115** | **108** |

**Grade: A** (>=104)

## Special Checks

- **(a) Smartraveller AU reference present?** YES — SKILL.md:85, 120; reference.md:46-50; template:53; example:67, 100.
- **(b) Walking-cap split SKILL vs reference?** APPROPRIATE — SKILL.md:66 gives brief default (8/4/6/5); reference.md:3-15 has full table (7 rows + uphill 30% adjustment). Clean split.
- **(c) Must-book lead-times diverse?** YES — reference.md:29-39 covers Tokyo (teamLab, Ghibli), Rome (Vatican), Paris (Eiffel/Louvre), Spain (Alhambra), London (West End), Iceland (tours), Disney. 8 distinct destinations across 4 continents (minor: Oceania/SE Asia absent).

## Dimension Notes

### Discovery 18/20
- name (SKILL.md:2) clear, kebab-case
- description (SKILL.md:3) under 250 chars, front-loaded with "Build a multi-day travel itinerary" — strong
- Minor: no explicit trigger keywords like "vacation/holiday" — could broaden activation

### Scope 14/15
- Single purpose: day-by-day itinerary with logistics
- No overlap with other lifestyle skills observed
- Edge cases (SKILL.md:124-131) keep scope tight via constraints

### Conciseness 14/15
- SKILL.md = 132 lines, well under 500
- Dense data (walking caps full table, must-book table, AU resources, pacing rules) correctly extracted to reference.md (63 lines)
- Slight redundancy: walking caps appear in both files (SKILL.md:66 abbreviated, reference.md:3-15 full) — acceptable as the SKILL.md version is summary

### Architecture 14/15
- Has SKILL.md, reference.md, templates/, examples/, LICENSE.txt — matches CLAUDE.md spec
- No scripts/ but not required

### Content 14/15
- 5 phases (intake → logistics → day-by-day → packing → risk) — logical
- Behavioural rules (SKILL.md:112-121) crisp, opinionated
- Edge cases cover multi-gen, solo, bleisure, first-international, altitude, pilgrimage
- Template (output-template.md) maps cleanly to phases
- Example (example-output.md) is a full Tokyo+Kyoto family-of-4 plan, 100 lines, realistic

### Tool Config 10/10
- `Read Write Edit` only (SKILL.md:5, 92) — minimal & appropriate for a writing skill

### Testing 7/7
- example-output.md realistic: dates, specific tickets, walking-km column populated, weather backups, AU emergency contacts

### Standards 3/3
- Frontmatter valid (name/description/argument-hint/allowed-tools/effort)
- AusE ("favourite", "colour", "organisation"-style spellings) — example uses "favourite" at SKILL.md:69
- AUD referenced (SKILL.md:23)
- MIT license present

### Activation 9/10
- argument-hint `[destination-dates-party]` clear
- $ARGUMENTS used (SKILL.md:29)
- Could add `paths:` glob for auto-activation on travel docs but optional

### Anti-patterns 5/5
- No bloated SKILL.md, no over-permissioned tools, no unrelated content, no missing template, no fictional citations

## Top 3 Fixes (P0)

1. **Lost-passport phone number inconsistency.** Template:77 lists "DFAT/consular emergency 1300 555 135" but reference.md:48 and example:99 use "+61 2 6261 3305". The 1300 number is the in-Australia consular line; from overseas the +61 2 number is correct. Pick one canonical entry; cross-reference both numbers and label by location.

2. **Walking-cap value mismatch between files.** SKILL.md:66 says "8 km adults" but reference.md:6-7 differentiates "fit adults 12 km" / "mixed-fitness 8 km". SKILL.md should either match reference.md's split or explicitly say "see reference.md for full ranges" to prevent drift.

3. **Must-book table missing Oceania/SE Asia tier.** reference.md:29-39 covers Europe/Japan/USA/Iceland but omits Bali (Komodo tours), Vietnam (Ha Long), Australia (Uluru sunset, Great Barrier Reef pontoons). Add 2-3 rows so the Smartraveller AU framing matches AU travellers' most common destinations.

## Minor Suggestions

- Add `paths:` glob (e.g. `**/trip*.md`, `**/itinerary*.md`) for auto-activation.
- Phase 1 (SKILL.md:33-40) asks 4 questions in one block — could mark "ask one at a time" if running interactively.
- Consider an `argument-hint` example: `argument-hint: [e.g. "Tokyo+Kyoto, Sep 15-24, family of 4 (kids 5 & 8)"]`.
