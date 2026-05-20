# Skill Audit — repo-snapshot

**Path:** `utilities/utilities/skills/repo-snapshot/`
**Date:** 20/05/2026
**Rubric:** 8 dims / 115 pts. A >=104, B 86-103.

---

## Score: 99 / 115 — Grade B

| # | Dimension | Score | Notes |
|---|-----------|-------|-------|
| 1 | Metadata & Frontmatter (15) | 14 | Valid YAML, kebab name, description front-loaded with use case, argument-hint present, scoped Bash tools, `effort: medium`. Description is 167 chars — well under 250 (SKILL.md:3). Minor: no `paths` glob for auto-activation on `.git/` or `package.json`. |
| 2 | Scope & Purpose (15) | 14 | Crisp single purpose: produce 5-min scannable snapshot. Audience-tuned (new-hire/investor/future-you/auditor) explicitly mapped (SKILL.md:31-35; reference.md:82-109). No scope creep. |
| 3 | Conciseness (10) | 10 | SKILL.md 137 lines (well under 500-line cap). Dense reference material correctly extracted to reference.md (123 lines). Clean separation. |
| 4 | Architecture (15) | 13 | 7 phases + reference.md + template + example. Sensible flow Intake -> Detect -> Tree -> LOC -> Deps -> Cadence -> Output. Minor: Phase 7 "Output" is just one line "Save as repo-snapshot.md" (SKILL.md:87-89) — could specify location convention (cwd vs `.claude/snapshots/`). |
| 5 | Content Quality (20) | 17 | Strong framework-detection heuristics table covering 17 frameworks + lock-file -> tool map + 9 test-framework rows (reference.md:5-55). Bus-factor risk list is well-curated (reference.md:113-123). LOC commands include proper prune for node_modules/.venv/vendor/target (reference.md:62-76). Gap: no guidance on handling Windows/PowerShell — `xargs wc -l` assumes POSIX. |
| 6 | Tool Usage (10) | 9 | `allowed-tools` properly scoped: `Bash(find:*) Bash(wc:*) Bash(git:log) Bash(git:shortlog)` (SKILL.md:5). Excellent narrow scoping — no blanket `Bash`. Tool-usage table at SKILL.md:95-102 documents purpose. Minor: `git:log` and `git:shortlog` use colon syntax — convention in this repo is typically `Bash(git:*)` but the granular form is acceptable and safer. |
| 7 | Testing & Examples (15) | 12 | Example uses THIS very anthril repo (examples/example-output.md:1) — realistic, dogfooded, audience tagged "new-hire (engineering)". Template has all section placeholders. Gap: only one example — could benefit from a second example for investor/DD audience to demonstrate audience-tuning, since that's a headline feature. Risk: example LOC numbers ("~3,200", "~85k") appear estimated rather than computed (example-output.md:19, 61) — undermines the "evidence-backed" claim. |
| 8 | Standards Conformance (15) | 10 | Australian English mostly honoured (no emoji, "Behavioural Rules" at SKILL.md:119, "organisation"-style spellings absent so neutral). LICENSE.txt present. **Deviation from CLAUDE.md template:** missing `## User Context` placement before `## System Prompt` (actual order at SKILL.md:17-27 has System Prompt before User Context — opposite to the documented body order in CLAUDE.md). Phases use `### Phase N` (h3) instead of `## Phase N` (h2) as documented in CLAUDE.md phase pattern. No `## Phase N ### Objective ### Steps ### Output` substructure used. |

---

## Special-criteria check

(a) **Framework-detection heuristics** — strong. 17 frameworks + 9 build tools + 9 test frameworks across reference.md:5-55. Covers JS/TS, Python (poetry/uv/hatch/pipenv), Rust, Go, PHP, Ruby, Java, Expo. Result: PASS.

(b) **Scoped Bash permissions** — `Bash(find:*) Bash(wc:*) Bash(git:log) Bash(git:shortlog)` (SKILL.md:5). Narrow + auditable. Result: PASS.

(c) **Audience-tuned output** — Phase 1 asks audience via AskUserQuestion (SKILL.md:33-35); reference.md:82-109 maps 4 audiences to distinct section emphasis; template line 4 captures audience; "Onboarding Recommendations" section keys off audience (template:63). Result: PASS.

(d) **Realistic example uses this anthril repo** — example-output.md:1 titled "official-claude-plugins"; folder tree matches actual categories (data-science / economics / engineering / lifestyle / marketing / seo / smb / utilities); references real artefacts (CLAUDE.md, marketplace.json, check-versions.mjs, fleet-judge.md). Result: PASS — but numeric figures look estimated rather than measured (see Dim 7).

---

## Top 3 P0 fixes

1. **Realign body structure to CLAUDE.md spec** (Dim 8). Reorder to: Title -> User Context -> System Prompt -> Phases. Promote phases to `## Phase N` (h2) with `### Objective / ### Steps / ### Output` substructure. Current `### Phase` (h3) breaks navigation in tooling that keys on h2 phase boundaries. File: SKILL.md:17-89.

2. **Add measurement instructions for example accuracy** (Dim 7). The example's LOC figures ("~3,200", "~85k") and commit cadence ("~60-80/month") are visibly approximate. Add a Phase 4.5 step requiring `wc -l` output to be captured verbatim, and re-run on this repo to ground-truth the example. Otherwise the dogfooded example contradicts the "Evidence-backed" project standard from CLAUDE.md.

3. **Add Windows/PowerShell fallback for LOC commands** (Dim 5). All `find ... | xargs wc -l` recipes (SKILL.md:60-62, reference.md:62-76) assume POSIX. Project repo lives on Windows (gitStatus shows `C:\Development\...`). Add a parallel PowerShell snippet using `Get-ChildItem -Recurse | Measure-Object -Line` OR document the Bash-tool requirement explicitly so cross-platform users aren't blocked.

---

## Minor follow-ups (P1)

- Add a second example targeting "investor/DD" audience to evidence the audience-tuning differentiator.
- Specify output file location convention in Phase 7 (`repo-snapshot.md` in cwd vs `.claude/snapshots/`).
- Consider `paths` frontmatter glob (`**/.git/HEAD`, `**/package.json`) for auto-activation.
- Phase 1 effort note "~30s per 100k lines" — verify or remove; unsubstantiated.

---

## Files reviewed

- `utilities/utilities/skills/repo-snapshot/SKILL.md` (137 lines)
- `utilities/utilities/skills/repo-snapshot/reference.md` (123 lines)
- `utilities/utilities/skills/repo-snapshot/templates/output-template.md` (76 lines)
- `utilities/utilities/skills/repo-snapshot/examples/example-output.md` (106 lines)
- `utilities/utilities/skills/repo-snapshot/LICENSE.txt` (21 lines, MIT)
