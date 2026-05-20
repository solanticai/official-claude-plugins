# Skill Audit — doc-link-validator

**Path:** `utilities/utilities/skills/doc-link-validator/`
**Date:** 20/05/2026
**Rubric:** 8 dims / 115 pts

---

## Scores

| Dim | Score | Notes |
|-----|-------|-------|
| Metadata (15) | 13 | Frontmatter valid; `name`, `description` (148 chars), `argument-hint`, `allowed-tools`, `effort: low` all present (SKILL.md:1-7). Description is front-loaded with use case. Minor: `effort: low` is defensible (script does the heavy lifting) but borderline — link triage across thousands of files could warrant `medium`. |
| Scope (15) | 14 | Tight, single-purpose: validate markdown links. Edge cases listed (SKILL.md:102-109) cover anchor-only skipping, auth-protected sites, localhost, GitHub branch URLs. No scope drift. |
| Conciseness (15) | 14 | 110 lines — well under 500. No reference.md needed (rubric, classification, edge cases all fit). Phase structure compressed but readable. |
| Architecture (15) | 12 | Phases 1-4 (SKILL.md:31-66) cover run → classify → suggest → output. **Issue:** `allowed-tools` declares `Bash(python:scripts/link-check.py)` (SKILL.md:5) but the script lives at the **plugin-level** `utilities/utilities/scripts/link-check.py`, not at a skill-relative `scripts/` path. The relative invocation in Phase 1 (`python scripts/link-check.py`) will fail unless CWD is the plugin root, which is not stated. P0. |
| Content quality (15) | 14 | 404 vs 403/405 distinction is explicit and repeated (SKILL.md:19, 44-46, 93, template line 40, example line 48). Archive.org fallback called out (SKILL.md:58, 95) and demonstrated in example (line 39). Rate-limit respect mentioned (SKILL.md:97). Classification buckets are sensible. |
| Tools (10) | 8 | `allowed-tools` restricts Bash to one script (good least-privilege). Missing `Grep`/`Glob` would help the "basename search" suggestion step (Phase 3, SKILL.md:58) — currently no declared way to search the repo for the moved file. P1. |
| Testing / examples (15) | 13 | `examples/example-output.md` is realistic, varied (6 internal + 4 external + 12 suspect + 3 transient), shows archive.org replacement (line 39), OWASP version-bump suggestion (line 40), case-mismatch on Linux (line 28). Template (`templates/output-template.md`) matches example structure 1:1. No reference.md — correctly flagged as not needed. |
| Standards (15) | 13 | AU English: "behaviour" (SKILL.md:91), "Behavioural Rules" used. No emoji. LICENSE.txt present (MIT). Markdown-first output. Minor: "aggressive-scan" hyphenation is awkward (SKILL.md:97); date format `dd_mm_yyyy` in template (line 3) matches AU convention. |

**Total: 101 / 115 → B (high, 3 pts off A).**

---

## Top 3 P0 / P1 Fixes

1. **(P0) Script path mismatch.** `allowed-tools: Bash(python:scripts/link-check.py)` (SKILL.md:5) and Phase 1 invocation `python scripts/link-check.py` (SKILL.md:34) imply a skill-local `scripts/` dir, but the script lives at the plugin's `utilities/utilities/scripts/link-check.py`. Either (a) update the invocation to `python "${CLAUDE_PLUGIN_ROOT}/scripts/link-check.py"` and the allowed-tools matcher to match, or (b) symlink/copy the script under the skill directory. Currently the skill will fail at Phase 1 unless the user happens to run from the plugin root.

2. **(P1) No tool for basename search.** Phase 3 (SKILL.md:58) says "search for the file by basename; suggest closest path" for broken internal links — but `allowed-tools` (SKILL.md:5) only lists `Read Write Edit Bash(python:...)`. There is no `Grep` or `Glob`. Add `Glob` so the suggestion engine can actually find moved files. Without it, every "Suggested replacement" in the internal-links table is guesswork.

3. **(P1) Archive.org lookup not automated.** Behavioural rule 3 (SKILL.md:95) and the example (line 39) suggest checking archive.org for replacements, but there is no helper, no `WebFetch` in `allowed-tools`, and the link-check.py script does not query the Wayback Machine API. Either add `WebFetch` (or extend the script with a `--check-archive` flag hitting `http://archive.org/wayback/available?url=...`) so the suggestion column is actually populated, or downgrade the example's archive.org replacements to "consider checking archive.org" advice.

---

## Other observations

- Anchor-only link skipping (SKILL.md:108) is consistent with script behaviour (link-check.py:50).
- "Verify manually" bucket is well-justified — npm/Medium/AWS are classic HEAD-refusers, accurately reflected in example (lines 52-54).
- Rate-limit guidance (SKILL.md:97) is concrete (8 workers, matches script default at link-check.py:17).
- No CSV path is templated into the report — example doesn't reference `link-check-results.csv` artefact; consider noting it in template footer for auditability.
