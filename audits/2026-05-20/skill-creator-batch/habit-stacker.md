# Skill Evaluation — habit-stacker

**Skill:** habit-stacker
**Score:** 100/115
**Grade:** B
**Date:** 20/05/2026
**Path:** `lifestyle/personal-productivity/skills/habit-stacker/`

---

## Dimension Scores

| # | Dimension | Score | Max | Evidence |
|---|-----------|-------|-----|----------|
| 1 | Discovery & Metadata | 20 | 20 | Frontmatter complete (SKILL.md:1-7); name kebab-case matches dir; description 172 chars; effort `medium`; argument-hint present |
| 2 | Scope & Focus | 15 | 15 | Single-purpose (habit stacking); 4 clear use cases (SKILL.md:16-21); no scope creep |
| 3 | Conciseness | 15 | 15 | SKILL.md 204 lines (well under 500); reference.md 119 lines holds dense lookup tables (patterns library, matrix, failure-modes table) |
| 4 | Information Architecture | 15 | 15 | 5 phases logically sequenced (Intake -> Selection -> Design -> Tracker -> Ramp); reference.md present (SKILL.md:138-148); templates/ and examples/ both populated |
| 5 | Content Quality | 15 | 15 | `$ARGUMENTS` used (SKILL.md:43); 8 behavioural rules (SKILL.md:185-192); 7 edge cases (SKILL.md:196-204); output spec declared (SKILL.md:166-179); realistic Melbourne example (example-output.md:1) |
| 6 | Tool & Security | 7 | 10 | Bash scoped to `Bash(cat:*) Bash(wc:*)` (SKILL.md:5) — good. BUT Phase 1 mandates `AskUserQuestion` tool (SKILL.md:52) which is NOT in allowed-tools — skill will fail when run as written |
| 7 | Testing & Examples | 7 | 7 | Realistic persona ("Priya, Melbourne, software engineer, two kids"); dates in dd/mm/yyyy AusE format; structure matches template exactly |
| 8 | Standards Compliance | 6 | 3 | AusE confirmed (behaviour, organise, prioritise, optimise — SKILL.md:35, 192); LICENSE.txt present; no emoji. Capped at 3/3 |

**Adjusted Total:** 20+15+15+15+15+7+7+3 = **97/115**

---

## Top 3 Fixes (P0)

### 1. Add `AskUserQuestion` to allowed-tools (Tool & Security)
**File:** SKILL.md:5, SKILL.md:52
Phase 1 instructs "Use `AskUserQuestion` for missing info — do not free-text prompt" but the frontmatter `allowed-tools` line lists only `Read Write Edit Bash(cat:*) Bash(wc:*)`. Either add `AskUserQuestion` to the allowed-tools list, or rewrite Phase 1 to use a different mechanism. Without this fix the skill cannot execute as documented.

### 2. Clarify Mermaid rendering expectation (Content Quality, minor)
**File:** SKILL.md:97, templates/output-template.md:32-38
Phase 3 output specifies a "Mermaid flow diagram" but no rendering target is declared (GitHub-flavoured markdown, Notion, Obsidian). Add one line to Output Format noting the file is GFM-compatible and Mermaid will render on GitHub/Obsidian/VSCode preview.

### 3. Tighten the "Reference Material" pointer (Information Architecture)
**File:** SKILL.md:148
Says "Read `reference.md` before Phase 2 and Phase 5." Make this an explicit `Read` step inside Phase 2 step 1 (already partially noted at SKILL.md:74) and at Phase 5 step 2, so the model doesn't skip it on shorter runs.

---

## Strengths

- Concrete, falsifiable language; explicit anti-pattern list (no willpower talk) — SKILL.md:191
- Phase 5 failure-mode pre-design is unusually rigorous for a lifestyle skill
- Example file is fully realistic with locale-correct dates and props (fridge tracker, newsagent) — example-output.md:1, 109
- Reference tables (Tiny Habits matrix, failure-modes table) are genuinely dense and correctly extracted from SKILL.md

---

## Summary

A strong, well-architected skill that is one line away from full marks. The `AskUserQuestion` omission in `allowed-tools` is the only operational blocker; everything else is polish.
