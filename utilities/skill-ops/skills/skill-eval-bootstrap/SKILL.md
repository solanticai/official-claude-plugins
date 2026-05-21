---
name: skill-eval-bootstrap
description: Scaffold a starter evals/suite.yaml for a Claude Code skill. Reads description, examples, and edge-case table to seed activation, functional, and edge-case tests that satisfy the harness's required test-category mix.
argument-hint: [skill-path-or-name]
allowed-tools: Read Write Glob Grep Bash(bash:scripts/*.sh)
effort: medium
---

# Skill Eval Bootstrap

<!-- anthril-output-directive -->
> **Output path directive (canonical — overrides in-body references).**
> All file outputs from this skill MUST be written under `.anthril/scaffolds/`.
> Run `mkdir -p .anthril/scaffolds` before the first `Write` call.
> Primary artefact: `.anthril/scaffolds/skill-eval-bootstrap.md`.
> Do NOT write to the project root or to bare filenames at cwd.
> Lifestyle plugins are exempt from this convention — this skill is not lifestyle.

## User Context

The user wants to scaffold an evaluation suite for a skill:

$ARGUMENTS

Acceptable argument forms — same as `skill-eval-harness`:
- Path to a skill directory
- `<plugin>/<skill>` pair
- Bare skill name (resolved against `<category>/*/skills/`)

## System Prompt

You are a test-suite scaffolder. You read a skill's SKILL.md (description, frontmatter, edge-case table if present) and its examples directory, then generate a `evals/suite.yaml` file that meets `skill-eval-harness`'s required test-category mix:

- ≥ 3 activation-positive cases
- ≥ 2 activation-negative cases
- ≥ 2 edge-case cases
- ≥ 1 functional case if an example exists

You never overwrite an existing suite without explicit confirmation. You also append an empty iteration log if absent.

---

## Phase 1: Resolve target

### Objective
Convert `$ARGUMENTS` into a concrete skill directory.

### Steps
1. Run `bash scripts/resolve-skill.sh "$ARGUMENTS"` → emits `target_dir=` or `error=`.
2. On error, print the message and halt.
3. Confirm `target_dir/SKILL.md` exists.

### Output
`target_dir`, `skill_name`.

---

## Phase 2: Extract triggers and examples

### Objective
Pull seed material from the skill's own files.

### Steps
1. Read SKILL.md frontmatter: `description`, `name`, `argument-hint`, `paths` (if any).
2. Read SKILL.md body — collect the `## User Context` section and any `## Edge Cases` table.
3. List `examples/*.md` — note their filenames; the first one becomes the functional case's expected output.
4. List `scripts/*.sh` — used to detect what `expected_error` codes the skill might emit (grep for `echo "error=...` lines).

### Output
`{description, name, paths[], edge_cases[], examples[], error_codes[]}`.

---

## Phase 3: Generate test cases

### Objective
Compose a complete `test_cases[]` array.

### Steps
1. **Activation-positive (3 cases):**
   - Case 1: a literal trigger from the description's first 80 chars.
   - Case 2: a paraphrase that swaps the leading action verb (e.g. "Audit X" → "Review X" → "Check X").
   - Case 3: if `paths:` is set, a query naming a matching file.
2. **Activation-negative (2 cases):**
   - Case 1: an unrelated coding question.
   - Case 2: a near-miss query — names a related concept the skill is *not* in scope for.
3. **Functional (1 case if `examples/` non-empty):**
   - `user_input` derived from `argument-hint` (e.g. `[skill-path]` → a real path).
   - `expected_outputs[]` — one `file_created` glob matching the example's filename pattern, one `contains` matching a header line from the example.
   - `judge_criteria` — start with `"Australian English used throughout"` and one skill-specific criterion derived from the description.
4. **Edge-case (2 cases):**
   - Case 1: empty `$ARGUMENTS` → `expected_error` from any `error=empty-argument` line in scripts, else `expected_error: "empty-argument"`.
   - Case 2: nonexistent target → `expected_error: "target-not-found"` (or another emitted error code).

### Output
`test_cases[]` ready to render.

---

## Phase 4: Write suite.yaml and iteration-log.md

### Objective
Materialise the suite without clobbering existing work.

### Steps
1. If `target_dir/evals/suite.yaml` exists, print the diff vs the generated suite and ask the user before overwriting. If `$ARGUMENTS` includes `--force`, skip the prompt.
2. Otherwise, create `target_dir/evals/` if missing.
3. Render the template at `templates/suite-skeleton.yaml` with the case array; write to `target_dir/evals/suite.yaml`.
4. If `target_dir/evals/iteration-log.md` is absent, copy from `templates/iteration-log-blank.md`.
5. Print a 4-line summary: skill name, suite path, case count breakdown, next command (`/skill-eval-harness <skill>`).

### Output
`target_dir/evals/suite.yaml` and (if new) `target_dir/evals/iteration-log.md`.

---

## Behavioural Rules

1. **Never overwrite an existing suite.yaml** without `--force` or explicit user confirmation.
2. **Generated cases are seeds, not finals.** The summary tells the user to review and tune `judge_criteria` for their skill.
3. **Australian English** throughout — even in generated case descriptions.
4. **Idempotent**: re-running with `--force` on a freshly generated suite must produce identical content.

---

## Edge Cases

| # | Case | Handling |
|---|---|---|
| E1 | Skill has no `examples/` | Skip functional case generation; suite has 5 cases (3 pos + 2 neg + 2 edge). Print a note recommending the user add an example before serious eval. |
| E2 | `description` is empty | Halt with error; activation cases need it. |
| E3 | `paths:` set with very broad glob (`**/*`) | Still generate the file-mention activation case but flag in the summary that activation tests will be noisy. |
| E4 | Scripts emit no `error=` codes | Default to the standard codes `empty-argument` / `target-not-found` in edge cases. |

---

## Scripts Catalogue

- `resolve-skill.sh` — same resolver shape as the harness's `resolve-suite.sh`, but accepts skills *without* an existing suite (the whole point of bootstrap)
- `extract-triggers.sh` — pull description / name / paths out of frontmatter
- `extract-error-codes.sh` — grep `scripts/*.sh` for `error=<code>` patterns
