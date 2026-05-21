# Skill Audit — smart-supplement-stack

**Path:** `lifestyle/health-wellness/skills/smart-supplement-stack`
**Date:** 2026-05-20
**Auditor:** skill-evaluator

---

## Score: 104 / 115 — Grade A

| Dimension | Score | Notes |
|-----------|-------|-------|
| Discovery (20) | 18 | Strong description + use cases (SKILL.md:3, 18-23). Activation triggers clear. Could add more keyword variants ("vitamins", "stack audit"). |
| Scope (15) | 14 | Tightly bound: stack-build + audit; 6-item cap (SKILL.md:110, 168). Doesn't over-reach into diagnosis. |
| Conciseness (15) | 14 | 181 lines, under cap; reference offloaded properly. Tool table and rules tight. |
| Architecture (15) | 14 | Clean phase split 1-5 (SKILL.md:54-119); reference.md (100 lines) carries quick-reference + interactions matrix + TGA notes. Templates + example present. |
| Content (15) | 14 | Evidence ladder defined (SKILL.md:35-39) and used consistently in reference.md:18-53 and example-output.md:11-19. Doses in mg/g/IU as required. |
| Tool (10) | 10 | Minimal allowed-tools (Read/Write/Edit, SKILL.md:5), correctly scoped — no Bash/Agent bloat. |
| Testing (7) | 6 | Example-output.md realistic and complete (74 lines). Only one example — second persona (e.g. vegan, or pregnant deferral) would strengthen. |
| Standards (3) | 3 | AusE throughout ("optimise", "behaviour"-style spellings — e.g. "specialise"-free but "Behavioural Rules" SKILL.md:160). MIT LICENSE present. |
| Activation (10) | 8 | Front-loaded description with concrete trigger phrases; "argument-hint: [goals-current-stack]" clear (SKILL.md:4). Lacks `paths` glob (acceptable for non-file skill). |
| Anti-patterns (5) | 3 | Minor: SKILL.md:25 references `commands/health-disclaimer.md` which is not part of this skill's directory — broken reference. Also "nicotine" listed as A-grade (reference.md:27) with weak caveat — controversial inclusion. |

---

## Special Checks

**(a) Disclaimer + medication-check at top of template?**
PASS. template/output-template.md:3 has bold disclaimer covering meds, pregnancy/breastfeeding, under-18. Mirrored in example-output.md:3.

**(b) Evidence-grade taxonomy (A/B/C/D) used consistently?**
PASS. Defined SKILL.md:35-39, reference.md:5-10, applied throughout reference.md:18-53 and example tables (example-output.md:11-19, 27-32). Rule "never list D-grade" enforced (SKILL.md:164).

**(c) Pregnancy/breastfeeding/<18 escalation explicit?**
PASS. SKILL.md:63 ("refer to pharmacist or GP; produce conservative output only"), SKILL.md:165 (Behavioural Rule 4), reference.md:71-91 dedicated section, template disclaimer. Edge case 1 (SKILL.md:175) covers it.

**(d) TGA / no-therapeutic-claims compliance evident?**
PASS. SKILL.md:31 cites TGA. SKILL.md:167 Rule 6 ("supports/may help, not treats/cures"). reference.md:95-100 dedicated AU TGA section including AUST L/R, Schedule 4 melatonin note.

---

## Strengths

1. Evidence taxonomy is rigorous, used consistently, and example demonstrates it on a real-looking 9-item stack.
2. Conservative defaults (cap=6, food-first, refer on pregnancy/meds) directly encoded in Behavioural Rules (SKILL.md:160-170).
3. TGA + AusE compliance is the strongest of the lifestyle plugins reviewed — TGA section is concrete (AUST L/R, Schedule 4).
4. Interactions matrix (reference.md:57-67) lists genuinely useful clinical pairs (SSRIs + St John's Wort + 5-HTP, fish oil + warfarin).

---

## Top 3 Fixes (P0)

### Fix 1 — Broken disclaimer reference (SKILL.md:25)

`See \`commands/health-disclaimer.md\`` points to a path that does not exist in this skill's directory (no `commands/` subdirectory; LICENSE/SKILL/reference/templates/examples only). Either inline the disclaimer in SKILL.md or create the referenced file. Severity: medium — disclaimer is the most safety-critical element.

### Fix 2 — Reclassify or remove "Nicotine" from A-grade table (reference.md:27)

Listing nicotine alongside creatine and vitamin D3 as A-grade — even with the addiction caveat — invites misuse and conflicts with the conservative TGA-compliant stance set out in SKILL.md:31, 167. Recommend moving to a separate "Not recommended for general use" note or removing entirely. Severity: high — reputational + safety risk.

### Fix 3 — Add a second example covering a deferral persona (examples/)

Only one example exists (Dan, omnivore lifter — example-output.md). The behavioural rules and edge cases lean heavily on pregnancy / multiple-meds / under-18 deferral pathways (SKILL.md:63, 165, 175-179), but no example demonstrates a conservative read-only audit. Add `example-pregnancy-deferral.md` or `example-polypharmacy-defer.md` so the model has a concrete pattern to imitate. Severity: medium — covers the highest-risk user segments.

---

## Minor Notes

- Phase numbering is correct; sub-phase headers use `### Phase N` (SKILL.md:54, 67, 79, 95, 114) — consider `## Phase` for hierarchy consistency with other skills in the plugin.
- Template "Cycling & Interactions" table (output-template.md:47-49) could include a "GP/Pharmacist flag" column to surface escalations inline.
- `reference.md:38` iron note is well-worded ("Only if blood test confirms deficiency") — good defensive language; consider replicating that pattern for vitamin D ("test serum if possible").
- argument-hint `[goals-current-stack]` is slightly cramped — `[goals + current-stack]` reads better.
