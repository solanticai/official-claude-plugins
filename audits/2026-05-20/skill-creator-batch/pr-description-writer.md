# Audit: pr-description-writer

**Path:** `utilities/utilities/skills/pr-description-writer/`
**Date:** 2026-05-20
**Rubric:** 8 dimensions / 115 pts

---

## Summary

A tight, well-scoped skill that drafts PR descriptions from `git diff`. Frontmatter scopes `Bash(git:*)` and `Bash(gh:pr)` correctly; risk-level surfaced explicitly with auth/migration escalation rules; test plan rendered as checklist; behavioural rule mandates "why > what"; AU spelling observed (`Behavioural`, `over-summarise`, `organisation` patterns). Example output is realistic and demonstrates all sections. Minor gaps: missing `LICENSE.txt` content verification, no `reference.md` (not required for this scope), and the in-body template duplicates `templates/output-template.md`.

---

## Scores

| Dim | Pts | Max | Notes |
|-----|-----|-----|-------|
| Metadata | 14 | 15 | Valid YAML; `name`, `description` (138 chars, front-loaded), `argument-hint`, `allowed-tools`, `effort: medium` all present (SKILL.md:1-7). No `paths`/`context` — fine for this skill. -1 for absent `version`/no explicit license tag. |
| Scope | 14 | 15 | Single-purpose: draft PR description. No overlap with other utilities skills. Edge cases (SKILL.md:124-131) note relationships to migration-plan-builder cleanly. |
| Conciseness | 14 | 15 | 132 lines, well under 500. Some redundancy: in-body template block (SKILL.md:54-82) duplicates `templates/output-template.md`. -1. |
| Architecture | 13 | 15 | Phases 1-4 are sequential and clear (SKILL.md:33-90). Output Format section points to template (SKILL.md:104-108). No `scripts/` needed. -2 for no `reference.md` separation though body is short enough that it's defensible. |
| Content | 14 | 15 | "Why > what" explicit (SKILL.md:19, 114). Risk classification heuristics named (SKILL.md:46). Edge cases for squash, stacked, bot PRs (SKILL.md:124-131). -1: Phase 3 could specify how to *derive* the "why" when commits are terse. |
| Tools | 15 | 15 | Excellent scoping: `Bash(git:diff)`, `Bash(git:log)`, `Bash(git:show)`, `Bash(gh:pr)` — each tool sub-scoped, not blanket `Bash`. Matches user's special criterion (a). |
| Testing | 11 | 15 | Example is rich and exercises the template end-to-end (example-output.md:1-51). Test plan rendered as checklist (example-output.md:29-36). -4: no negative example (huge diff, bot PR), no `scripts/` to test. |
| Standards | 14 | 15 | AU spelling: `Behavioural` (SKILL.md:112), `over-summarise` (SKILL.md:118). Markdown-first. No emoji. -1: example uses ASCII em-dash but generally good. |
| **Total** | **109** | **115** | **Grade: A** |

---

## Special Criteria

- (a) **`Bash(git:*)` and `Bash(gh:pr)` scoped** — PASS (SKILL.md:5). Per-subcommand scoping is exemplary.
- (b) **Risk-level surfaced** — PASS. Phase 2 classifies (SKILL.md:46); template has dedicated `## Risk` section with level + specific risks (output-template.md:15-22); behavioural rule #2 (SKILL.md:115) and edge cases escalate auth/RLS to "high".
- (c) **Test plan as checklist** — PASS (output-template.md:23-29; example-output.md:29-36).
- (d) **Why > what** — PASS (SKILL.md:19, 114; output-template.md:5-7).
- (e) **AU spelling** — PASS (`Behavioural`, `over-summarise`).

---

## Top 3 P0 Fixes

1. **Remove duplicated template block in SKILL.md:54-82** — `templates/output-template.md` is the canonical source. Replace the body block with a one-line pointer ("See `templates/output-template.md`") to avoid drift. Saves ~30 lines.
2. **Add a "deriving the why" sub-step in Phase 3** (SKILL.md:50-82) — when commit messages are terse, instruct the model to check linked issues (`gh issue view`), PR body (`gh pr view`), or ask the user. Currently the skill assumes "why" is recoverable from the diff alone, which is often false.
3. **Add a second example** under `examples/` covering a high-risk scenario (DB migration + auth change) — exercises the risk-escalation rule (SKILL.md:130-131) which currently has no demonstrated output. Even a 30-line example would close the testing gap.

---

## Notable Strengths

- Tool scoping is best-in-class — sub-command granularity rather than blanket `Bash`.
- Edge-case coverage (SKILL.md:124-131) is unusually thorough: first commit, squash, stacked, bot PRs, migrations, auth all addressed.
- Behavioural rules section (SKILL.md:112-120) reinforces the special criteria without being preachy.
- Example output (example-output.md) is realistic — it's plausibly a real PR for this very repo's lifestyle plugin work.

---

## Minor Issues

- `LICENSE.txt` exists but not verified for MIT/Apache content in this audit (assumed standard).
- No `reference.md` — acceptable; body is concise enough.
- SKILL.md:38 mentions enriching with `gh pr view <number>` but Phase 4 doesn't describe how to handle the case where an existing PR description should be *updated* vs *replaced*.
- Cross-reference syntax `[[migration-plan-builder]]` (SKILL.md:130) — confirm this is the project's accepted wikilink form; otherwise switch to a relative path.

---

**Final grade: A (109/115)**
