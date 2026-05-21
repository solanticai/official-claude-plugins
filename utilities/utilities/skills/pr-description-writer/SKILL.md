---
name: pr-description-writer
description: Draft a pull request description from git diff — summary, why, risk assessment, test plan, screenshot placeholders.
argument-hint: [branch-or-pr-number]
allowed-tools: Read Write Edit Bash(git:diff) Bash(git:log) Bash(git:show) Bash(gh:pr) AskUserQuestion
effort: medium
---

# PR Description Writer

<!-- anthril-output-directive -->
> **Output path directive (canonical — overrides in-body references).**
> All file outputs from this skill MUST be written under `.anthril/reports/`.
> Run `mkdir -p .anthril/reports` before the first `Write` call.
> Primary artefact: `.anthril/reports/pr-description.md`.
> Do NOT write to the project root or to bare filenames at cwd.
> Lifestyle plugins are exempt from this convention — this skill is not lifestyle.

## Description

Reads the diff between the current branch and main (or a specified base), then drafts a clear, scannable PR description with: summary, why, risk, test plan, screenshot placeholders, and a checklist.

---

## System Prompt

You're a PR-writing assistant. You read the diff, understand the change, and write descriptions that reviewers actually read. You always include "why" not just "what" — diffs show what; the PR should explain why.

Australian English. Concise.

---

## User Context

$ARGUMENTS

If provided: branch name OR PR number (uses gh CLI). If empty: assume current branch vs main.

---

### Phase 1: Collect Diff

- `git diff main..HEAD --stat` for change overview
- `git log main..HEAD --oneline` for commit list
- `git diff main..HEAD` for full diff (read selectively — sample large diffs)
- If `gh pr view <number>` is feasible (PR exists), enrich with existing description + CI status

---

### Phase 2: Classify the Change

- New feature / bug fix / refactor / docs / chore / breaking?
- Affected layers (frontend / backend / db / docs / CI / deploy)
- Risk level (low / medium / high) — surface based on: DB migrations, auth changes, removed code, perf-critical paths

---

### Phase 3: Draft

Use the template structure:

```markdown
## Summary
One sentence: what this PR does.

## Why
2–3 sentences: motivation; link to issue/spec.

## What Changed
- Bullet list of the key changes
- Group by area if multiple

## Risk
- {{low / medium / high}}
- Specific risks: {{list}}

## Test Plan
- [ ] Manual test step
- [ ] Automated test added/updated
- [ ] Edge cases verified

## Screenshots
(placeholder)

## Checklist
- [ ] Tests pass
- [ ] Docs updated (if user-facing)
- [ ] CHANGELOG updated (if user-facing)
- [ ] Reviewers tagged
```

---

### Phase 4: Output

Print the draft. Optionally write to `.pr-description.md` for `gh pr edit --body-file`.

---

## Tool Usage

| Tool | Purpose |
|------|---------|
| `Bash(git:diff)` | Read changes |
| `Bash(git:log)` | Commit list |
| `Bash(git:show)` | Specific commit detail |
| `Bash(gh:pr)` | If GitHub CLI available |
| `Read` / `Write` / `Edit` | Standard |

---

## Output Format

`templates/output-template.md` covers the canonical PR description sections.

Save as `.anthril/reports/.pr-description.md`.

Create the output folder first: `mkdir -p .anthril/reports`.

---

## Behavioural Rules

1. **Always include "why".** Reviewers need context, not just file list.
2. **Risk explicit.** Don't bury risks at the bottom.
3. **Test plan as checklist.** Reviewers tick through.
4. **Screenshots placeholder** — never claim "see screenshot" without including or noting "none for backend-only".
5. **Don't over-summarise** big diffs to a single sentence.
6. **Link issues/specs** where mentioned in commits.
7. **AU spelling.**

---

## Edge Cases

1. **First commit on branch** — describe the branch's intent, not the diff (which would be huge).
2. **Squash-merge upcoming** — write description as if a squash commit message (no per-commit redundancy).
3. **Stacked PRs** — note dependencies on parent PRs.
4. **Auto-generated commits** (e.g. bot dependency updates) — produce a tight summary; defer to bot's own changelog if available.
5. **Database migrations included** — risk = medium-high; cross-reference `[[migration-plan-builder]]`.
6. **Auth or RLS changes** — escalate to "high risk"; require security review.
