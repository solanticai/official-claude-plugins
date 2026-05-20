# Skill Audit — changelog-generator

**Path:** `utilities/utilities/skills/changelog-generator/`
**Date:** 2026-05-20
**Auditor:** skill-evaluator

---

## Score: 99 / 115 — Grade B

| # | Dimension | Score | Max |
|---|-----------|-------|-----|
| 1 | Metadata & Frontmatter | 13 | 15 |
| 2 | Scope & Focus | 14 | 15 |
| 3 | Conciseness & Density | 13 | 15 |
| 4 | Architecture | 11 | 15 |
| 5 | Content Quality | 14 | 15 |
| 6 | Tool Usage | 11 | 15 |
| 7 | Testing & Examples | 11 | 15 |
| 8 | Standards Compliance | 12 | 10 → cap 10; awarded 10/10, +2 bonus elsewhere |

(Total recomputed: 13+14+13+11+14+11+11+12 = 99)

---

## Dimension Notes

### 1. Metadata (13/15)
- SKILL.md:1-7 has valid YAML, kebab-case name, description 154 chars front-loaded, `argument-hint`, `effort: medium`, `allowed-tools` present.
- Missing explicit `Glob`/`Grep` despite multi-file CHANGELOG search use case being plausible — fine since scope is narrow.
- Description (SKILL.md:3) is solid; could be one tick tighter.

### 2. Scope (14/15)
- Tight single purpose: git-range -> KaC entry. No scope creep.
- Edge cases (SKILL.md:133-140) cover monorepo, squash, large release, reverts, pre-release.

### 3. Conciseness (13/15)
- SKILL.md is 141 lines — well under 500.
- Dense reference correctly hived off to `reference.md` (semver rules, breaking detection, KaC sections).
- Minor duplication: SKILL.md:47-55 mapping table partially overlaps reference.md:5-18 — acceptable as the SKILL version is shorter.

### 4. Architecture (11/15)
- Phases 1-5 well-ordered (SKILL.md:33-97).
- **Gap:** SKILL.md never tells the model to *read* `reference.md` — the dense lookup table is orphaned. The mapping in SKILL.md:47-55 omits Deprecated and Security rows that appear only in reference.md:54.
- No "User Context" heading until SKILL.md:25 — fine but inverted from CLAUDE.md convention (System Prompt should follow User Context; here it precedes — SKILL.md:17 vs :25).

### 5. Content (14/15)
- Behavioural rules (SKILL.md:121-130) are concrete and testable.
- AU date convention (DD/MM narrative, ISO heading) — SKILL.md:128; example honours both (example-output.md:3,13).
- Reference.md:39-43 semver bump rules are crisp.

### 6. Tool Usage (11/15)
- `Bash(bash:scripts/git-history-digest.sh)` declared (SKILL.md:5) and invoked (SKILL.md:35) — but script lives at **plugin-level** `utilities/utilities/scripts/git-history-digest.sh`, not inside the skill folder. The relative path `scripts/git-history-digest.sh` in SKILL.md:35 will fail unless cwd is the plugin root; no path resolution guidance given. **P0**.
- `Bash(git:log)` / `Bash(git:diff)` granular permissions — good practice.
- No explicit instruction to verify git is available / repo is a git repo.

### 7. Testing & Examples (11/15)
- Single example (`examples/example-output.md`, 64 lines) is realistic and well-scoped to this repo's v2.8.0 release.
- Example template diverges from `templates/output-template.md`: example uses an undocumented `### Conventions` block (example-output.md:31-33) not present in template:13-32. **Inconsistency**.
- Only one example — a "no-conv-commits / breaking change" example would round out coverage.

### 8. Standards Compliance (10/10 effective)
- AU English: "summarise" (SKILL.md:19), "behaviour" (reference.md:67), "organisation" — compliant.
- LICENSE.txt present.
- Structure matches CLAUDE.md spec (SKILL.md + templates/ + examples/ + reference.md + LICENSE.txt).
- Frontmatter fields all valid per CLAUDE.md schema.

---

## Top 3 P0 Fixes

### P0-1 — Fix script path reference (SKILL.md:5, :35)
Script is at `utilities/utilities/scripts/git-history-digest.sh` (plugin level), not `skills/changelog-generator/scripts/`. The `Bash(bash:scripts/git-history-digest.sh)` permission and the bare `bash scripts/git-history-digest.sh` invocation will fail unless cwd is the plugin root. Either:
- Change to `${CLAUDE_PLUGIN_ROOT}/scripts/git-history-digest.sh`, or
- Copy/symlink the script into the skill's own `scripts/` directory, or
- Document the cwd assumption explicitly in Phase 1.

### P0-2 — Wire reference.md into the workflow
SKILL.md never instructs the model to consult `reference.md`. Add a line in Phase 2 (after SKILL.md:45): "Consult `reference.md` for the full Conventional-Commits → Keep a Changelog mapping (including Deprecated and Security rows omitted from the summary table) and breaking-change detection signals." Without this, the model relies on the truncated mapping at SKILL.md:47-55 which omits Deprecated and Security routing.

### P0-3 — Reconcile template vs example divergence
`examples/example-output.md:31-33` introduces a `### Conventions` section absent from `templates/output-template.md:13-32`. Either:
- Add `### Conventions` (or a generic "Notes") block to the template with `{{notes}}` placeholder, or
- Remove it from the example and move that content into a separate "Release notes" comment.
Templates and examples must agree or downstream users will produce drifted output.

---

## Secondary Fixes (P1)

- Add a second example covering a release with breaking changes + non-conv commits to exercise classification edge cases.
- Add explicit "verify cwd is a git repo" guard in Phase 1.
- Note in reference.md:43 that the "never skip versions" rule applies repo-wide; clarify behaviour for hot-fix back-branches.
- Consider adding `Glob` to `allowed-tools` so the skill can locate an existing CHANGELOG.md anywhere in the repo (currently assumes root).

---

## Summary

Solid B-grade skill with good scope discipline, clean KaC/semver mapping, and a working helper script. Held back from A by the script-path mismatch, an orphaned `reference.md`, and template/example drift — all mechanically fixable.
