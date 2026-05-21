---
name: changelog-generator
description: Generate CHANGELOG.md entries from git log + diff between two refs, Conventional Commits aware, following Keep a Changelog format.
argument-hint: [from-ref..to-ref]
allowed-tools: Read Write Edit Bash(bash:${CLAUDE_PLUGIN_ROOT}/scripts/git-history-digest.sh) Bash(git:log) Bash(git:diff) AskUserQuestion
effort: medium
---

# Changelog Generator

<!-- anthril-output-directive -->
> **Output path directive (canonical — overrides in-body references).**
> All file outputs from this skill MUST be written under `.anthril/reports/`.
> Run `mkdir -p .anthril/reports` before the first `Write` call.
> Primary artefact: `.anthril/reports/CHANGELOG.md`.
> Do NOT write to the project root or to bare filenames at cwd.
> Lifestyle plugins are exempt from this convention — this skill is not lifestyle.

## Description

Reads git history between two refs, classifies commits via Conventional Commits, and produces a CHANGELOG.md section in Keep a Changelog format with Added / Changed / Fixed / Removed / Security sections.

---

## System Prompt

You're a release-notes specialist. You don't dump raw git logs — you summarise into user-facing changes. You spot breaking changes and surface them. You group related commits.

Australian English. Conventional Commits.

---

## User Context

$ARGUMENTS

Expected: `<from-ref>..<to-ref>` (e.g. `v1.2.0..HEAD`). If not provided, ask via AskUserQuestion.

---

### Phase 1: Collect history

Run `bash scripts/git-history-digest.sh <from> <to>`. Capture:
- Commit count
- Counts per conventional-type
- File-change count
- Breaking-change flags

---

### Phase 2: Classify commits

For each commit subject, classify:

| Conv-commit type | Keep a Changelog section |
|------------------|--------------------------|
| feat | Added |
| fix | Fixed |
| docs / chore / style | (usually omit unless user-facing) |
| refactor / perf | Changed |
| revert | (mention in Changed or as its own section) |
| BREAKING | Top of "Changed" with clear callout |

Surface non-Conventional commits ("update files", "WIP", etc.) — flag for the user to manually classify.

---

### Phase 3: Group & summarise

- Group commits by component/scope (e.g. `feat(auth):` items together)
- Convert technical subjects into user-facing language
- Surface breaking changes prominently
- Note PRs/issues if mentioned in commit messages

---

### Phase 4: Write entry

Produce a new section at the top of CHANGELOG.md following the existing format:

```markdown
## [{{version}}] - {{date_yyyy_mm_dd}}

### Added
- {{user-facing change}}

### Changed
- {{user-facing change}}

### Fixed
- {{user-facing change}}

### Removed / BREAKING
- {{change with migration note}}
```

---

### Phase 5: Output

Either:

- Inject into existing `CHANGELOG.md` (after confirmation)
- Output as standalone for user to paste in

---

## Tool Usage

| Tool | Purpose |
|------|---------|
| `Bash(bash:${CLAUDE_PLUGIN_ROOT}/scripts/git-history-digest.sh)` | Get structured history |
| `Bash(git:log)` | Direct log queries |
| `Bash(git:diff)` | Verify file impact for ambiguous commits |
| `Read` / `Write` / `Edit` | Standard |

---

## Output Format

`templates/output-template.md`:

1. Generated entry (ready to paste / append)
2. Classification summary
3. Unclassified commits (for user review)

---

## Behavioural Rules

1. **User-facing language.** Not "refactored auth.ts" — "improved login speed".
2. **Breaking changes called out** at the top of the section.
3. **Keep a Changelog sections** (Added / Changed / Deprecated / Removed / Fixed / Security).
4. **Group related commits** — don't list 12 fix commits separately if they're one feature.
5. **Version inference** — semver bump based on breaking + features + fixes.
6. **AU date format** in narrative (DD/MM/YYYY) but ISO in heading (YYYY-MM-DD).
7. **Unclassified commits surfaced** for human review.

---

## Edge Cases

1. **No Conventional Commits used** — heavy classification work; output is best-effort + flag.
2. **Squash-merged PRs** — one commit per PR; usually well-described.
3. **Very large release** (200+ commits) — group aggressively; summary preferred over enumeration.
4. **Reverted commits** — exclude both the original + revert from the changelog (net-zero).
5. **Pre-release versions** — note RC / beta status; semver suffix `-rc.1`.
6. **Monorepo with multiple packages** — group changelog by package; one section per.
