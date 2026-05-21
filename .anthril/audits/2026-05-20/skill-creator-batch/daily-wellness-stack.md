# Skill Audit — daily-wellness-stack

**Path:** `lifestyle/health-wellness/skills/daily-wellness-stack`
**Date:** 2026-05-20
**Score:** 100/115 — **Grade B**

---

## Dimension Scores

| Dimension | Score | Evidence |
|---|---|---|
| Discovery (20) | 18 | Description front-loaded with key use case (SKILL.md:3); `argument-hint` present (SKILL.md:4); four explicit "Use this skill when" bullets (SKILL.md:15-20). |
| Scope (15) | 14 | Explicit lane: "Stay in your lane: hydration, movement-break, sunlight, breath, posture, hygiene" (SKILL.md:30). Defers cold plunges/fasting/supplements to other skills. |
| Conciseness (15) | 14 | 110 lines, well under 500-line budget. No fluff. |
| Architecture (15) | 11 | Phases use H3 (`### Phase 1:` SKILL.md:42, 50, 64, 72) — convention per `.claude/CLAUDE.md` is H2. Inconsistent with phase pattern. |
| Content (15) | 12 | Strong habit bank (SKILL.md:54-58), behavioural rules (94-101), edge cases (104-109). Disclaimer is a *reference* to external `commands/health-disclaimer.md` (SKILL.md:22) rather than inline — fragile if path absent. |
| Tool (10) | 9 | Minimal toolset Read/Write/Edit (SKILL.md:5) — appropriate for a low-effort generative skill. |
| Testing (7) | 5 | Single example present (`examples/example-output.md`); realistic Adelaide persona. No reference.md (not required at this size). |
| Standards (3) | 3 | Australian English present (SKILL.md:32 "Australian English; metric; AEST/AEDT"). LICENSE.txt present. `effort: low` set (SKILL.md:6). |
| Activation (10) | 9 | Strong activation surface — clear differentiator from `[[habit-stacker]]` and explicit companionship statement (SKILL.md:13). |
| Anti-patterns (5) | 5 | No prescriptive medical advice, no maximalism, no scope creep. |

**Total: 100/115 — Grade B**

---

## Special Checks

- **(a) Disclaimer at top of template:** YES — `templates/output-template.md:3` ("General wellness guidance only. Not personal medical or fitness advice."). Also echoed in example-output.md:3.
- **(b) `[[habit-stacker]]` link notation present:** YES — appears at SKILL.md:13, :46, :68, :100, :109. Strong cross-linking.
- **(c) Cap at 5 habits enforced:** YES — behavioural rule "Cap at 5" (SKILL.md:98); template prompt "max 5" (templates/output-template.md:12); SKILL.md:13 states "3–5 tiny, frequent health behaviours".

---

## Top 3 Fixes (P0)

1. **Inline the disclaimer in SKILL.md.** SKILL.md:22 references `commands/health-disclaimer.md` — confirm that file exists in the plugin or inline the disclaimer text directly. A broken reference defeats the "Disclaimer at top" behavioural rule (SKILL.md:96). Recommendation: replace line 22 with the same disclaimer sentence already used in templates/output-template.md:3.

2. **Promote phases to H2 headings.** SKILL.md:42, :50, :64, :72 use `### Phase N:` but `.claude/CLAUDE.md` phase pattern specifies `## Phase N:`. Tooling that parses skill phases by H2 will miss these. Renumber to `## Phase 1: Intake` etc.

3. **Tighten effort signal.** `effort: low` (SKILL.md:6) is consistent with the skill, but no Tool Usage rationale is given for *why* only Read/Write/Edit. Add a one-line note (SKILL.md:88-90) explaining no Bash/Grep needed because skill is purely generative — helps reviewers and downstream skill-evaluator tooling.

---

## Notes

- No reference.md — not needed at 110 lines. Flag is non-blocking.
- Edge cases (SKILL.md:104-109) are unusually well-considered for a low-effort skill — shift workers, travel, burnout recovery, conflict resolution with `[[habit-stacker]]`. This is a quality signal.
- Frontmatter is valid; all required fields present.
