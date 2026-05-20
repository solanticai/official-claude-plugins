# deep-focus-day — Skill Evaluation

**Skill:** deep-focus-day
**Score:** 112 / 115
**Grade:** A
**Date:** 20/05/2026

## Dimension Scores

| # | Dimension | Score | Evidence |
|---|-----------|-------|----------|
| 1 | Discovery & Metadata | 20/20 | Valid frontmatter SKILL.md:1-7; name matches dir; description 162 chars (SKILL.md:3); argument-hint, allowed-tools, effort all present |
| 2 | Scope & Focus | 15/15 | Single purpose (design a deep-focus day); clear use cases SKILL.md:16-22 |
| 3 | Conciseness | 15/15 | SKILL.md is 203 lines (well under 500) |
| 4 | Information Architecture | 15/15 | 5 sequenced phases SKILL.md:49-155; templates/output-template.md and examples/example-output.md both present |
| 5 | Content Quality | 14/15 | $ARGUMENTS used SKILL.md:43; behavioural rules SKILL.md:183-192; edge cases SKILL.md:195-202; output format declared SKILL.md:167-179; realistic example present. Minor: references `reference.md` at SKILL.md:74 but file not present |
| 6 | Tool & Security | 10/10 | allowed-tools granular (Read Write Edit) SKILL.md:5; no secrets |
| 7 | Testing & Examples | 7/7 | example-output.md (77 lines) realistic Sydney PM scenario; matches template structure (archetype, blocks, guardrails, ramp, day-after, auto-reply, calendar block) |
| 8 | Standards Compliance | 3/3 | Australian English (colonised SKILL.md:19, behavioural SKILL.md:183, café example-output.md:17); LICENSE.txt present (21 lines, MIT); no emoji |

## Top 3 Fixes (P0)

1. **Remove or create `reference.md`** — SKILL.md:74 says "see `reference.md` for detail" on archetype selection, but no reference.md exists in the skill directory. Either inline the four-archetype detail or create reference.md.
2. **Tighten Phase 1 AskUserQuestion structure** — SKILL.md:55-60 lists five questions but doesn't specify that they should be asked together in a single AskUserQuestion call (current best practice). Add a note: "ask in a single batched call."
3. **Add explicit allowed-tools entry for AskUserQuestion** — SKILL.md:5 lists only `Read Write Edit`, but Phase 1 (SKILL.md:55) calls `AskUserQuestion`. Add `AskUserQuestion` to allowed-tools or rephrase Phase 1 to use inline prompting.
