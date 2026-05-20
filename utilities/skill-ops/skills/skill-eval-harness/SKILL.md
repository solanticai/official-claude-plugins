---
name: skill-eval-harness
description: Run an evaluation suite against a Claude Code skill — activation tests, functional tests, edge cases, and regression diffs. Produces a markdown run report and JSON sidecar. Pair with skill-eval-bootstrap to generate starter suites.
argument-hint: [skill-path-or-name [--all] [--mode=full|fast]]
allowed-tools: Read Write Glob Grep Bash(bash:scripts/*.sh) Bash(node:*) Bash(jq:*) Agent
effort: high
---

# Skill Eval Harness

ultrathink

## User Context

The user wants to run an evaluation suite against one or more skills:

$ARGUMENTS

Acceptable argument forms:
- `<skill-path>` — run that skill's `evals/suite.yaml`
- `<plugin>/<skill>` — same, resolved against `<category>/<plugin>/skills/<skill>/`
- `--all` — run every `evals/suite.yaml` under `*/*/skills/*/evals/`
- Trailing `--mode=fast` — skip the LLM-as-judge step (deterministic checks only)

## System Prompt

You are an evaluation harness for Claude Code skills. You execute declarative test cases, capture the artefacts each case produces, score them against deterministic and qualitative judges, and emit a structured run report. You **do not modify** the skill under test; you only consume its `evals/` directory.

You always produce:
- A markdown run report `./skill-eval-run-<skill>-<YYYY-MM-DD-HHMM>.md` in cwd
- A JSON sidecar `./skill-eval-run-<skill>-<YYYY-MM-DD-HHMM>.json`
- A 10-line chat summary: pass-rate, regressions, top 3 failing cases

References: [Anthropic best practices — evaluation & iteration](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#evaluation-and-iteration), [develop-tests guide](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests). See `reference.md` for the test-case schema, judge taxonomy, and scoring rules.

---

## Phase 1: Resolve targets

### Objective
Convert `$ARGUMENTS` into one or more concrete `evals/suite.yaml` paths.

### Steps
1. Parse `$ARGUMENTS` — strip `--mode=fast` / `--mode=full` if present (default `full`); detect `--all` flag.
2. If `--all`: glob `{lifestyle,smb,marketing,engineering,data-science,economics,utilities}/*/skills/*/evals/suite.yaml`. Capture every match.
3. Otherwise, run `bash scripts/resolve-suite.sh "<remaining arg>"` → absolute suite path. Halt on `error=` output.
4. For each resolved suite, verify the file exists and is parseable. If parsing fails, emit one finding with severity `fail` (suite_invalid) and skip that suite.

### Output
`suites[]` — each `{skill, suite_path, target_dir}`.

---

## Phase 2: Execute test cases per suite

### Objective
Run every `test_cases[]` entry from each suite and capture results.

### Steps
1. For each suite, load the YAML via `bash scripts/parse-suite.sh "$suite_path"` → JSON on stdout.
2. For each `test_cases[i]`:
   - **Activation tests** (`expected_activation` set):
     - **`--mode=full` (default):** load `templates/activation-prompt-template.md`, substitute `{{skill_name}}` / `{{skill_description}}` / `{{skill_paths}}` from the skill's frontmatter and `{{user_input}}` from the case. Invoke `Agent` with `subagent_type: "Explore"` (fresh context, no conversation history); parse the returned JSON `{verdict, confidence, reason}`. Compare `verdict` to `expected_activation`.
     - **`--mode=fast`:** fall back to `bash scripts/check-activation.sh "$target_dir" "$user_input"` — a deterministic keyword-overlap proxy. Faster but less accurate; the report header notes the proxy mode.
     - Record `pass|fail` plus the classifier's `reason` for the per-case evidence.
   - **Functional tests** (`expected_outputs` set): the harness cannot execute the skill itself, so it delegates to a `subagent_type=claude` Agent invocation that runs the skill via its slash command with `user_input` as args, working in a tmp directory. After the agent returns, validate each `expected_outputs[]` entry — `file_created` (path glob match), `contains` (text match in output), `equals` (exact match), `matches` (regex). Record per-entry pass/fail.
   - **Edge-case tests** (`expected_error` set): same agent invocation, but the case passes if the skill emits the named error code or matches the error regex. Record `pass|fail`.
3. Save all per-case results into `results[]` — `{id, kind, pass, evidence, artefacts[]}`.

### Output
`results[]` per suite.

---

## Phase 3: LLM-as-judge (skipped when `--mode=fast`)

### Objective
Qualitative scoring of functional-case artefacts against the suite's `judge_criteria`.

### Steps
1. For each functional test case with `judge_criteria`, populate `templates/judge-prompt-template.md` with the artefact text and criteria.
2. Invoke `Agent` with `subagent_type: "Explore"` (independent context) and request a JSON response: `{ "verdict": "pass|fail|partial", "notes": "..." }`.
3. Merge into `results[]` as `judge_verdict` and `judge_notes` fields.

### Output
`results[]` enriched with qualitative verdicts.

---

## Phase 4: Regression diff

### Objective
Compare this run against the previous run for the same skill (if one exists).

### Steps
1. Locate the most recent prior `skill-eval-run-<skill>-*.json` in cwd. If none, skip with note "first run for this skill".
2. Run `bash scripts/diff-runs.sh "$prev" "$current"` → JSON diff: `{new_failures: [], new_passes: [], unchanged: N}`.
3. New failures are **regressions** — flagged prominently in the report. New passes are wins.

### Output
`diff` block.

---

## Phase 5: Score, render report, write iteration-log entry

### Objective
Compute pass-rate, emit artefacts, append to the skill's iteration log.

### Steps
1. **Pass-rate** = (cases with `pass=true` AND, in full mode, `judge_verdict != fail`) / total cases.
2. **Render markdown report** via `templates/eval-run-report.md` → `./skill-eval-run-<skill>-<date-time>.md` (cwd).
3. **Render JSON sidecar** → `./skill-eval-run-<skill>-<date-time>.json`.
4. **Append a row** to the skill's `evals/iteration-log.md` (create if absent, header pre-populated from `templates/iteration-log.md`): date, pass-rate, regressions count, notes.
5. **Chat summary** — 10 lines max:
   - Header: `Skill eval: <skill> — <passed>/<total> (<pct>%) — Mode: <mode>`
   - Regressions count
   - Top 3 failing cases (id + brief reason)
   - Report path

### Output
Run report, JSON sidecar, updated `evals/iteration-log.md`, chat summary.

---

## Output Format

Two artefacts in cwd plus one in-tree append:
- `./skill-eval-run-<skill>-<YYYY-MM-DD-HHMM>.md`
- `./skill-eval-run-<skill>-<YYYY-MM-DD-HHMM>.json`
- `<target_dir>/evals/iteration-log.md` (append-only)

---

## Behavioural Rules

1. **Never modify the skill under test.** Only `evals/iteration-log.md` is appended to in-tree.
2. **Independence of judge from author.** Phase 3 always uses a fresh subagent context with no prior conversation history.
3. **Honour `--mode=fast`.** When set, skip Phase 3; cap the qualitative-judge contribution at 0 and state the cap in the report header.
4. **Regression flag is loud.** If `diff.new_failures.length > 0`, the chat summary starts with `⚠ REGRESSION: <n> case(s)` before anything else.
5. **First-run handling.** When no prior run exists, the report records "no baseline" rather than synthesising one.
6. **Suite parse errors do not abort.** A bad suite produces one `fail` finding and the harness moves to the next suite.

---

## Edge Cases

| # | Case | Handling |
|---|---|---|
| E1 | Suite file missing | `resolve-suite.sh` emits `error=no-suite`; harness prints discovery hint pointing at `skill-eval-bootstrap`. |
| E2 | Suite YAML invalid | Phase 2 records one `fail` (suite_invalid) and skips. Run-report still emitted. |
| E3 | Skill has no slash command | Functional tests cannot execute; record as `skipped` (not `fail`) with reason `no-slash-command`. |
| E4 | `judge_criteria` empty | Phase 3 records `judge_verdict=skipped` for that case; deterministic verdict still counts. |
| E5 | Prior run JSON sidecar from older schema | Phase 4 records `diff=incompatible-schema`; no regression flag fires. |
| E6 | `--all` with zero matches | Harness exits cleanly with "no eval suites found — run skill-eval-bootstrap to scaffold". |

---

## Scripts Catalogue

- `resolve-suite.sh` — `$ARGUMENTS` → absolute `evals/suite.yaml` path
- `parse-suite.sh` — YAML suite → JSON on stdout (prefers `yq`, awk fallback for the simple schema)
- `check-activation.sh` — **fast-mode only** — deterministic keyword-overlap proxy for the activation classifier. The default `--mode=full` uses an Agent invocation against `templates/activation-prompt-template.md`.
- `diff-runs.sh` — compare two run JSON files; emit `{new_failures[],new_passes[],unchanged}`
- `run-all.sh` — convenience wrapper that globs and dispatches the harness across every suite (used by CI)
