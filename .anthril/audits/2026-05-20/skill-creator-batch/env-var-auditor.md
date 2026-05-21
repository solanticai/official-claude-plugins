# Skill Evaluation — env-var-auditor

**Path:** `utilities/utilities/skills/env-var-auditor`
**Date:** 20/05/2026
**Rubric:** 8 dimensions, 115 pts total

---

## Scores

| Dim | Dimension | Score | Notes |
|-----|-----------|------:|-------|
| 1 | Metadata & Frontmatter | 14/15 | All required fields present (SKILL.md:1-7). `effort: low` arguably under-rated for a multi-language scan; could be `medium`. Description 134 chars, front-loaded. |
| 2 | Scope & Focus | 14/15 | Tight scope: drift vs declarations vs code refs vs security. No scope creep. |
| 3 | Conciseness | 14/15 | 131 lines, well under 500. Phases are crisp. Tool Usage table slightly redundant with frontmatter (SKILL.md:87-95). |
| 4 | Architecture & Structure | 13/15 | Directory complete: SKILL.md, templates/, examples/, LICENSE. No `reference.md`; not needed at this size. Phase pattern (1-5) followed though shorter than canonical Objective/Steps/Output structure (CLAUDE.md phase pattern). |
| 5 | Content Quality | 13/15 | Strong behavioural rules (114-119) + edge cases (123-130) including monorepo, deploy-only vars, dynamic names, false positives. Example output (lines 1-65) realistic with file:line refs. |
| 6 | Tool Configuration | 14/15 | `allowed-tools: Read Write Edit Grep Glob Bash(test:*) Bash(cat:*)` (SKILL.md:5). Grep + Glob present as required. Bash scoped narrowly. `Agent` not listed; not needed. |
| 7 | Testing & Examples | 12/15 | One example output, no example .env.example input shown. Template placeholders (output-template.md:1-57) align with example. Missing a second contrasting example (e.g. monorepo or "clean repo" case). |
| 8 | Standards Compliance | 13/15 | Australian English ("Behavioural", "behaviour" implicit), no emoji, MIT LICENSE present. Output filename `env-var-audit.md` (SKILL.md:83) reasonable. Date format dd/mm/yyyy in template (output-template.md:3) — AU compliant. |

**Total: 107 / 115 — Grade A**

---

## Special Criteria

**(a) Never log actual values** — PASS. Behavioural Rule 1 (SKILL.md:114) "Never log the actual values. Especially anything that looks like a secret." Reinforced in Edge Case 2 (SKILL.md:126) "do not output any values; recommend git history scrub". Example output never prints values, only var names.

**(b) Grep/Glob in allowed-tools** — PASS. Both listed (SKILL.md:5).

**(c) Language coverage Node/Python/Go/Rust/Shell** — PASS. All five covered explicitly (SKILL.md:51-55). Includes import.meta.env and Deno.env.get variants for Node.

**(d) Security-flag pattern (*_SECRET/_KEY/_TOKEN)** — PASS. Pattern listed in Phase 4 (SKILL.md:77) and example flags STRIPE_WEBHOOK_SECRET + RESEND_API_KEY (example-output.md:54-55). Template includes Security Flags section.

---

## Top 3 P0 Fixes

1. **Add a second example** — current `examples/` has only one output (Next.js + Supabase). Add a contrasting case such as a monorepo with multiple `.env.example` files or a Python/Go service to demonstrate the language-coverage promise and the monorepo edge case (SKILL.md:125).

2. **Show how dynamic var names are surfaced in output** — Edge Case 5 (SKILL.md:129) says to flag `process.env[someVariable]` for manual review, but the output template has no section for this. Add a "Manual Review Required" table to `templates/output-template.md` so the rule has somewhere to land.

3. **Reconsider `effort: low`** — auditing a polyglot repo with Grep across five languages plus secret-pattern matching is closer to `medium`. Bump to `medium` (SKILL.md:6) to set correct user expectation on runtime.

---

## Minor Notes

- Tool Usage table (SKILL.md:87-95) duplicates frontmatter `allowed-tools`; consider removing or keeping only purpose column.
- Phase headings use `### Phase N` (SKILL.md:36, 47, 61, 72, 81) but no `## Phase N` parent — minor inconsistency with CLAUDE.md canonical phase pattern (Objective/Steps/Output triplet).
- No `reference.md` — appropriate given 131-line size; flag is N/A.
- "Surface secret-detection patterns if anything looks committed (`*.env` in git)" (SKILL.md:118) — could reference `git log --all -- *.env` as the concrete check.
