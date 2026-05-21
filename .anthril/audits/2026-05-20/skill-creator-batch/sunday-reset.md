# sunday-reset — Skill Evaluation

**Skill:** sunday-reset
**Date:** 20/05/2026
**Score:** 110/115
**Grade:** A

## Dimension Scores

| # | Dimension | Score | Evidence |
|---|-----------|-------|----------|
| 1 | Discovery & Metadata | 20/20 | Valid YAML frontmatter (SKILL.md:1-7); name kebab-case matches dir; description 191 chars (line 3); argument-hint, allowed-tools, effort all present |
| 2 | Scope & Focus | 15/15 | Single purpose — weekly-reset ritual design; clear use-cases listed (SKILL.md:15-22); no scope creep |
| 3 | Conciseness | 15/15 | SKILL.md is 194 lines — well under 500; no dense lookup material that would require reference.md |
| 4 | Information Architecture | 14/15 | 5 phases logically sequenced (SKILL.md:48-143); templates/output-template.md and examples/example-output.md both present; minor: no reference.md (not strictly needed but the prompt library could arguably be extracted) |
| 5 | Content Quality | 15/15 | $ARGUMENTS used (SKILL.md:42); behavioural rules clear (lines 174-183); edge cases listed (lines 186-193); output format declared (lines 158-170); example uses realistic founder persona (example-output.md:1, 57-58) |
| 6 | Tool & Security | 10/10 | allowed-tools is minimal and granular: Read Write Edit (SKILL.md:5); no secret literals |
| 7 | Testing & Examples | 7/7 | example-output.md uses realistic Marcus persona, real dollar figures, real Australian dates (18/05/2026); matches template structure exactly |
| 8 | Standards Compliance | 3/3 | Australian English throughout ("personalised" line 3, "optimise" line 31, "judgement" line 76, "honour" line 192); LICENSE.txt present (MIT); no emoji detected |

**Total: 110/115 — Grade A**

## Top 3 Fixes (P0)

1. **Minor IA polish — consider extracting reflection-prompt library to reference.md.** The 12-prompt library appears in both SKILL.md guidance (line 139), templates/output-template.md (lines 71-82), and examples/example-output.md (lines 71-82). Extract to `reference.md` so SKILL.md and template reference a single source; reduces drift risk if the library grows. (SKILL.md:139; templates/output-template.md:71-82)

2. **Tool table mentions AskUserQuestion in Phase 1 but it is not declared in allowed-tools.** SKILL.md:54 says "Ask … via `AskUserQuestion`" but allowed-tools (SKILL.md:5) lists only `Read Write Edit`. Either add `AskUserQuestion` to allowed-tools or remove the directive and rely on natural conversational intake.

3. **No `paths` auto-activation hint.** Optional but useful — a `paths` glob (e.g. `**/weekly-review*.md`, `**/sunday-reset*.md`) on the frontmatter would let the skill surface automatically when a user opens an existing review template. (SKILL.md:1-7)
