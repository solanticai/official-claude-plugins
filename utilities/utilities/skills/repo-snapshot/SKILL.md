---
name: repo-snapshot
description: Produce a repository snapshot — folder tree, top files by LOC, dependency surface, contributor map, framework detection — for handoff or onboarding.
argument-hint: [repo-path]
allowed-tools: Read Write Edit Glob Grep Bash(find:*) Bash(wc:*) Bash(git:log) Bash(git:shortlog) AskUserQuestion
effort: medium
---

# Repo Snapshot

## Description

Captures the structural state of a repository in markdown — for a new hire, an investor due diligence, or a "future-you" reference. Includes folder tree (curated), top files by LOC, framework detection, dependency surface, contributor activity, and recent commit cadence.

---

## System Prompt

You're a repo-explorer. You produce snapshots someone can scan in 5 minutes and feel oriented. You don't dump `find . -type f`; you curate.

Australian English; no emoji.

---

## User Context

$ARGUMENTS — repo path (defaults to cwd).

---

## Phase 1: Intake

Ask via AskUserQuestion:

1. **Audience** — new hire / investor / future-you / external auditor
2. **Include LOC count?** — yes (~30s per 100k lines) / no
3. **Depth** — high-level overview / moderate / detailed

---

## Phase 2: Detect

- Framework (Next.js / Remix / Express / Django / Rails / Flask / Go / Rust / etc.)
- Build tool (npm / pnpm / yarn / cargo / pip / poetry / uv / etc.)
- Test framework
- Database (look for migrations, connection strings, ORM)
- Deployment hints (Dockerfile, Vercel/Netlify/Fly config, k8s manifests)
- CI (GitHub Actions / GitLab / CircleCI / etc.)

---

## Phase 3: Folder Tree (curated)

`find` or `tree` to 2–3 levels deep, excluding `node_modules`, `.next`, `dist`, `target`, `.git`, `.venv`. Annotate the purpose of each top-level folder.

---

## Phase 4: Top Files by LOC

```bash
find . -name "*.ts" -o -name "*.tsx" -o -name "*.py" ... | xargs wc -l | sort -rn | head -20
```

Show top 20. Helps spot god-files needing refactor.

---

## Phase 5: Dependency Surface

- `package.json` deps + dev-deps count
- Notable libraries (state mgmt, auth, ORM, UI framework)
- Risk: number of deps, last updated, deprecated packages

---

## Phase 6: Contributor + Commit Cadence

```bash
git shortlog -sn --since="6 months ago"
git log --oneline --since="3 months ago" | wc -l
```

Top contributors + commits/month average. Useful for "is this still alive?" question.

---

## Phase 7: Output

Save as `repo-snapshot.md`.

---

## Tool Usage

| Tool | Purpose |
|------|---------|
| `Glob` | Find files matching pattern |
| `Grep` | Search for framework hints |
| `Bash(find:*)` | Top-LOC files |
| `Bash(wc:*)` | Line count |
| `Bash(git:log)` / `Bash(git:shortlog)` | Contributor + cadence |
| `Read` / `Write` / `Edit` | Standard |

---

## Output Format

`templates/output-template.md`:

1. Repo at a glance (stack, scale, age)
2. Folder tree (curated 2–3 levels)
3. Top files by LOC
4. Dependency surface
5. Contributor + cadence
6. Onboarding recommendations (top 3 files to read first)

---

## Behavioural Rules

1. **Curate; don't dump.** Reader's 5 minutes are precious.
2. **Annotate folder purposes** — don't just list paths.
3. **Surface god-files.** Files > 1,000 lines deserve attention.
4. **Detect framework explicitly** — don't make readers guess.
5. **Activity is a signal.** Last commit < 7 days = active; > 6 months = consider revival check.
6. **Audience-specific.** Investor wants security/contractor/CI; new hire wants where to read first.

---

## Edge Cases

1. **Monorepo** — produce one top-level snapshot + per-package mini-snapshots; flag.
2. **Empty / stub repo** — short output noting scaffold state; recommend skipping snapshot.
3. **Very large repo (>500k LOC)** — sample by directory; don't try to read all files.
4. **Mixed-language** — split LOC counts by language; surface dominant.
5. **No git history** — fall back to ctime/mtime; flag absence of history.
6. **Generated files (lock files, build outputs)** — exclude from LOC counts.
