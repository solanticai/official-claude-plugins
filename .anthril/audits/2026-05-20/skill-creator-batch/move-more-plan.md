# Skill Audit — move-more-plan

**Path:** `lifestyle/health-wellness/skills/move-more-plan`
**Date:** 2026-05-20

## Scoring

| Dimension | Score | Notes |
|---|---|---|
| Discovery (20) | 17 | Frontmatter complete (SKILL.md:1-7). Description 188 chars, front-loaded. `argument-hint` present. `effort: high` matches scope. Keywords absent but not required. |
| Scope (15) | 13 | Single coherent purpose — N-week training program. Phases 1-5 sequential, no overlap. Goal taxonomy clear (SKILL.md:51-52). |
| Conciseness (15) | 14 | SKILL.md 163 lines, well under 500. Dense material correctly extracted to reference.md (periodisation, volume heuristics). |
| Architecture (15) | 13 | Standard structure present: SKILL.md, reference.md, templates/, examples/, LICENSE.txt. Five phases clean. Behavioural rules + edge cases at bottom. No scripts/ — not needed. |
| Content (15) | 13 | Evidence-fluent persona (SKILL.md:29). Substitution table, deload triggers, periodisation models in reference.md. Example output realistic and complete (example-output.md:1-100). Australian English used (periodisation, optimise). |
| Tool (10) | 5 | **Mismatch.** SKILL.md:43 instructs "run Phase 1 (4 questions via AskUserQuestion)" but `allowed-tools: Read Write Edit` (line 5) omits AskUserQuestion. Skill cannot execute its own intake instruction. |
| Testing (7) | 5 | One example, good fidelity. No second example for novice/bodyweight tier despite skill claiming to cover that path (SKILL.md:65, reference.md:5-14). |
| Standards (3) | 3 | LICENSE.txt present. AusE throughout. Kebab-case name matches dir. |
| Activation (10) | 9 | Description front-loads "N-week strength, endurance, or hybrid training program". "Use this skill when" block (SKILL.md:16-22) gives strong triggers. |
| Anti-patterns (5) | 5 | No vague language, no overclaiming, AEP referral mandated for clinical edge cases, no body-shaming rule (SKILL.md:150). |
| **TOTAL** | **97/115** | **Grade B** |

## Special Checks

**(a) Disclaimer at top of template?** Yes — output-template.md:3 places disclaimer immediately under H1, before any program content. Example output mirrors this (example-output.md:3). Behavioural rule 1 (SKILL.md:144) reinforces.

**(b) AskUserQuestion in allowed-tools when Phase 1 mentions it?** **No — fail.** SKILL.md:43 explicitly says "run Phase 1 (4 questions via AskUserQuestion)" but allowed-tools is `Read Write Edit` only (SKILL.md:5). This is a hard inconsistency.

**(c) Edge cases cover pregnancy / injury / pre-existing condition appropriately?** Mostly yes. Pregnancy: SKILL.md:157 ("refer to women's-health physio + AEP; do not prescribe") — appropriate. Injury/surgery: SKILL.md:158 — appropriate. Phase 1 flag (SKILL.md:54) catches injury, pain, post-surgery, 6-week deconditioning, pregnancy. **Gap:** no explicit pre-existing chronic condition handler (cardiac, diabetes, hypertension, metabolic). Behavioural rule 8 mentions "chronic condition → refer" but edge case list does not enumerate. Postpartum mentioned in template disclaimer but not in edge case list as distinct from pregnancy.

## Top 3 Fixes (P0)

1. **Add `AskUserQuestion` to `allowed-tools`** (SKILL.md:5). Phase 1 (SKILL.md:43) cannot execute its prescribed intake otherwise. Change to: `allowed-tools: Read Write Edit AskUserQuestion`.

2. **Add an explicit "pre-existing chronic condition" edge case** (SKILL.md:155-162). Insert a 7th edge case covering cardiac, hypertension, diabetes, metabolic conditions, post-cancer-treatment — refer to GP + AEP, do not prescribe load progression without clearance. Also add postpartum as a distinct entry from pregnancy (different return-to-load considerations).

3. **Add a second example** under `examples/` for a novice + bodyweight + 3-sessions/wk scenario. The current example (example-output.md) is intermediate + home gym + hybrid — it does not exercise the bodyweight substitution table (reference.md:5-14) or the novice linear progression template (SKILL.md:61). A second example would also validate that the same template structure scales down cleanly.

## Minor Observations

- Template "Sessions per week" placeholder reuses `{{n}}` (output-template.md:11) — same token as length; should be `{{sessions}}`.
- "Reference Material" section (SKILL.md:102-111) duplicates content already in reference.md without adding navigation value; could be one line: "See `reference.md` for exercise library, substitution table, deload triggers, volume heuristics, periodisation models."
- Behavioural rule 4 ("Deload every 4–6 weeks. Not optional.") slightly conflicts with template showing deloads at fixed weeks 4/8/12 (output-template.md:60-62) — clarify whether window is fixed or auto-triggered by reference.md:60-68 signals.
- No `keywords` in frontmatter; not required by project standards but would aid discoverability for "training program", "strength program", "hybrid runner".
