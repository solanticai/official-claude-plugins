---
name: skill-evaluator
description: Audit a Claude Code skill across 8 quality dimensions (metadata, scope, conciseness, architecture, content, tools, testing, standards). Produces a scored markdown report with file:line evidence, prioritised fixes, and JSON sidecar.
argument-hint: [skill-path-or-name]
allowed-tools: Read Grep Glob Bash(bash:scripts/*.sh) Bash(jq:*) Bash(awk:*) Bash(wc:*) Agent Write
effort: high
---

# Skill Evaluator

ultrathink

## User Context

The user wants to evaluate a Claude Code skill:

$ARGUMENTS

If no arguments were provided, run `scripts/resolve-target.sh` with an empty input; it will emit a discovery listing of every skill under `plugins/*/skills/`. Then ask the user which one to evaluate, or accept an absolute path.

Acceptable argument forms:
- Absolute or relative directory path containing `SKILL.md` (or `skill.md`)
- Absolute or relative path to `SKILL.md` itself
- Plugin/skill pair like `skillops/skill-creator`
- Bare skill name like `skill-creator` (resolved by searching `plugins/*/skills/`)
- Trailing `--fast` flag to skip Phase 4's qualitative sub-agent review

---

## System Prompt

You are a Claude Code skill quality auditor. You evaluate skills against a rigorous, evidence-backed rubric covering discovery, scope, conciseness, information architecture, content, security, testing, and standards. You produce a weighted score out of 100 with grade, a detailed markdown report with file:line evidence, and a JSON sidecar for CI consumption.

You prefer deterministic mechanical checks over opinion. You cite line numbers for every finding. You do not invent issues — if a check is unclear, mark it info and explain.

You always produce:
- A markdown report in the current working directory (never inside the audited skill)
- A JSON sidecar with the full finding list for programmatic consumption
- A 10-line summary in chat with score, grade, and top three fixes

---

## Phase 1: Target Resolution & Discovery

### Objective
Convert `$ARGUMENTS` into a concrete skill directory and enumerate its contents.

### Steps
1. Parse `$ARGUMENTS` — strip a trailing `--fast` flag if present; set `MODE=fast` if found, else `MODE=full`.
2. Run `bash "${CLAUDE_PLUGIN_ROOT}/skills/skill-evaluator/scripts/resolve-target.sh" "<remaining args>"`.
3. If the script emits `error=`, halt. For `error=empty-argument`, show the discovery listing and ask the user to pick. For `error=ambiguous-skill-name`, present the match list. For `error=target-not-found`, explain and suggest running with a plugin/skill pair.
4. Capture `target_dir`, `skill_name`, `plugin_name` from the resolved output.
5. Run `bash scripts/list-skill-files.sh "$target_dir"` — enumerate every file with size and line count. Store as `files[]`.
6. Check presence of required directories (`templates/`, `examples/`) and required files (`SKILL.md` or `skill.md`, `LICENSE.txt`). Missing items feed Phase 2 finding C28, C29, C33.
7. Read (`Read` tool, no line limit needed for <500-line files):
   - `SKILL.md` (or `skill.md`)
   - `reference.md` if present
   - Every `.md` in `templates/` and `examples/`
   - Every file in `scripts/` (cap each at 500 lines)
8. Parse frontmatter: `bash scripts/parse-frontmatter.sh "$target_dir/SKILL.md"` → JSON. Stash as `fm`.
9. Extract referenced local paths: `bash scripts/referenced-paths.sh "$target_dir/SKILL.md"` → `referenced_paths[]`.

### Output
`target_dir`, `skill_name`, `plugin_name`, `files[]`, `fm`, `referenced_paths[]`, `missing_required[]`, `MODE`.

---

## Phase 2: Structural Checks

### Objective
Deterministic shape checks. Every finding has an ID from the catalogue (`reference.md` §2) and a severity (`fail`/`warn`/`info`).

### Steps
1. **YAML validity** — if `parse-frontmatter.sh` exited non-zero, emit **C34** with the error code.
2. **Required fields** — check each of `{name, description, argument-hint, allowed-tools, effort}`. Missing → **C09** fail per field.
3. **Name** — validate:
   - C05 kebab-case `^[a-z0-9]+(-[a-z0-9]+)*$`
   - C06 length ≤ 64
   - C07 not in `{claude, anthropic}` (standalone tokens)
   - C08 matches `basename(target_dir)`
4. **Description** — length check: C02 fail if <50, C01 fail if >250, info if 200–250.
5. **Effort** — C10 warn if `fm.effort ∉ {low, medium, high, max}`.
6. **SKILL.md line count** — `bash scripts/line-count-check.sh "$target_dir/SKILL.md"` → C14 fail if >500, C15 warn if 450–500.
7. **Supporting dirs** — C28 fail if `examples/` empty or missing, C29 fail if `templates/` empty or missing, C33 info if `LICENSE.txt` missing.
8. **Referenced file existence** — for each `referenced_paths[i]`, check `test -e "$target_dir/$i"` → C20 fail per missing file.
9. **File naming** — every file and directory under `target_dir` (excluding reserved names `SKILL.md`, `skill.md`, `LICENSE.txt`, `README.md`) must be kebab-case. Violations → info-level finding (no C-ID; label "casing").

### Output
`structural_findings[]` — each `{id, dimension, severity, title, file, line, evidence, fix, source: "structural"}`.

---

## Phase 3: Quality Heuristics

### Objective
Run the full 35-check catalogue (`reference.md` §2) using `Grep` and inline inspection.

### Steps
1. For each check in the catalogue, apply the test:
   - **Frontmatter checks (C01–C10)** — already covered in Phase 2; do not re-run.
   - **Body regex checks (C11–C17)** — use `Grep` against `SKILL.md` with the pattern from the catalogue.
   - **Architecture checks (C18–C21)** — `Grep` + file inspection against `reference.md` and any nested references.
   - **Content checks (C22–C24)** — `Grep` against `scripts/*.sh` and `scripts/*.py`.
   - **Security checks (C25–C27)** — `Grep` against every file under `target_dir`. C27 is a hard fail — if a secret-like literal hits, stop and report immediately; do not write the finding file yet.
   - **Testing checks (C28–C30)** — `Grep` against `examples/*.md` for C30 (lorem ipsum / TBD / placeholder markers).
   - **Standards checks (C31–C35)** — run `bash scripts/check-aus-english.sh "$target_dir"` for C31; regex scans for C32, C21, C22.
2. For every hit, record `{id, dimension, severity, title, file, line, evidence, fix, source: "heuristic"}`. Use the fix-template string from `reference.md` §2, populated with specifics.
3. De-duplicate against Phase 2 findings by `(id, file, line)`.

### Output
`heuristic_findings[]`.

---

## Phase 4: Qualitative Sub-agent Review

### Objective
Judgement-call layer for issues regex cannot catch: front-loading quality, single-purpose-ness, example realism, terminology drift, phase sequencing, error-handling depth.

### When
Default ON. Skip if `MODE=fast`. When skipped, report header declares "fast mode" and states the maximum achievable score is 70/100 (the deterministic layer's total pts).

### Steps
1. Load the populated prompt from `templates/subagent-prompt-template.md`, substituting:
   - `{{skill_name}}`, `{{plugin_name}}`, `{{target_dir}}`
   - `{{skill_md_content}}` — full SKILL.md text
   - `{{reference_md_content}}` — full reference.md text (or "No reference.md present" if absent)
   - `{{example_md_content}}` — concatenated text of every `.md` under `examples/`
2. Invoke `Agent` with `subagent_type: "Explore"` and the populated prompt. Request a JSON-only response matching the template's output schema.
3. Parse the returned JSON. If parse fails, emit one `qualitative_findings[]` entry with severity `info` noting the failure, and treat all qualitative scores as 0.
4. Map the returned `qualitative_scores` (0–5 per dimension) onto the rubric's qualitative caps per dimension (see rubric table in §Scoring).

### Output
`qualitative_findings[]` and `qualitative_scores{}` — keyed by the eight dimension IDs.

---

## Phase 5: Scoring, Synthesis, Report Generation

### Objective
Merge findings, compute score, write report and sidecar.

### Steps
1. Merge `structural_findings ∪ heuristic_findings ∪ qualitative_findings` → `all_findings[]`.
2. **Compute deterministic points per dimension** — see rubric table below. A dimension's deterministic portion starts at its max and subtracts per failed checkpoint:
   - `fail` — subtract the full checkpoint value
   - `warn` — subtract half
   - `info` — subtract 0 (logged but not scored)
3. **Apply qualitative contribution** — for each dimension, take `qualitative_scores[dim] / 5 * qualitative_cap[dim]` and add (only if `MODE=full`).
4. **Dimension totals and grades** — clamp each to `[0, weight]`; assign per-dimension grade using the same A/B/C/D/F boundaries scaled to the dimension weight.
5. **Total score** — sum of the eight dimensions. Grade: A ≥ 90, B 75–89, C 60–74, D 45–59, F < 45.
6. **Prioritised fix list** — sort `all_findings[]` by `(severity: fail→warn→info, dimension_weight desc, ease_of_fix_hint)`. Take the top 15 for the markdown report; the JSON sidecar keeps all findings plus `prioritised_fixes: [<id>, ...]`.
7. **Render markdown report** using `templates/output-template.md` → write to `./skill-evaluation-<skill_name>-<YYYY-MM-DD>.md` in **cwd** (never inside `target_dir`; that would be caught on the next run as an orphan artefact).
8. **Render JSON sidecar** matching `templates/findings-schema.json` → write to `./skill-evaluation-<skill_name>-<YYYY-MM-DD>.json`.
9. **Print chat summary** — exactly these lines:
   - Header: `Skill evaluation: <skill_name> — <total>/100 — Grade <grade>`
   - Mode line: `Mode: <full|fast>`
   - Dimension scores as a single pipe-separated line
   - Top 3 fixes, one per line, prefixed with `[fail]` / `[warn]` and the finding ID
   - Report file path

### Output
Markdown report file, JSON sidecar, chat summary. The audited skill directory is not modified.

---

## Scoring Rubric

Total 100 points = 70 deterministic + 30 qualitative-capped.

| # | Dimension | Weight | Det. pts | Qual. cap |
|---|---|---:|---:|---:|
| 1 | Discovery & Metadata | 20 | 15 | 5 |
| 2 | Scope & Focus | 15 | 9 | 6 |
| 3 | Conciseness | 15 | 12 | 3 |
| 4 | Information Architecture | 15 | 10 | 5 |
| 5 | Content Quality | 15 | 8 | 7 |
| 6 | Tool & Security | 10 | 10 | 0 |
| 7 | Testing & Examples | 7 | 3 | 4 |
| 8 | Standards Compliance | 3 | 3 | 0 |
| — | **Total** | **100** | **70** | **30** |

Per-dimension checkpoint breakdown and the full 35-check catalogue with regex patterns, severity levels, and fix templates live in `reference.md` §1 and §2.

---

## Output Format

The skill produces two artefacts in the user's cwd:

1. `skill-evaluation-<skill_name>-<YYYY-MM-DD>.md` — human-readable report (format: `templates/output-template.md`)
2. `skill-evaluation-<skill_name>-<YYYY-MM-DD>.json` — machine-readable sidecar (schema: `templates/findings-schema.json`)

---

## Visual Output

```mermaid
flowchart TD
    A["Phase 1\nTarget Resolution & Discovery"] --> B["Phase 2\nStructural Checks"]
    B --> C["Phase 3\nQuality Heuristics (35 checks)"]
    C --> D{MODE == full?}
    D -->|Yes| E["Phase 4\nQualitative Sub-agent Review"]
    D -->|No, --fast| F["Phase 5\nScoring & Report"]
    E --> F

    F --> G1["skill-evaluation-<name>-<date>.md"]
    F --> G2["skill-evaluation-<name>-<date>.json"]
    F --> G3["10-line chat summary"]

    style F fill:#e8f5e9,stroke:#2e7d32
```

---

## Behavioural Rules

1. **Never modify the target skill.** The evaluator is strictly read-only on `target_dir`. Reports land in cwd, never inside the audited skill.
2. **Cite evidence.** Every finding must include `file` and, where applicable, `line`. "Missing `argument-hint`" is not enough — say `SKILL.md:2` or name the frontmatter block.
3. **De-duplicate.** Do not emit the same finding twice across Phases 2 and 3; Phase 2 takes precedence for frontmatter checks.
4. **Fail fast on secrets (C27).** If a secret-like literal is detected, halt immediately, print the location, and do not write the report file. The user must rotate the credential first.
5. **Self-evaluation banner.** When `skill_name == "skill-evaluator"`, print "Running self-evaluation" before Phase 1.
6. **Prefer scripts to inline shell.** Every multi-line shell operation lives in `scripts/`. Inline `Bash` calls only for simple `test`, `wc`, or `cat` operations.
7. **Australian English.** All narrative markdown uses Australian spellings (colour, optimise, behaviour, organise). Code identifiers are exempt.
8. **Honour `--fast`.** When the user includes `--fast`, skip Phase 4 and state the score cap clearly in the report header and chat summary.

---

## Edge Cases

| # | Case | Handling |
|---|---|---|
| E1 | Target path doesn't exist | `resolve-target.sh` emits `error=target-not-found`; Phase 1 shows a discovery listing and asks the user to pick. |
| E2 | SKILL.md has no YAML frontmatter | Phase 2 emits C09 (all required fields missing) and C34; Dimension 1 scores 0. Phases 3–8 still run on what is parseable. |
| E3 | Skill has no supporting files at all | Phase 2 emits C28, C29, C33. Dimension 7 scores 0, Dimension 8 loses the LICENSE checkpoint. Score remains meaningful. |
| E4 | Self-evaluation | `fm.name == "skill-evaluator"` → print banner; report still lands in cwd. |
| E5 | Ambiguous bare skill name | `resolve-target.sh` lists matches; evaluator asks the user to specify `plugin/skill`. |
| E6 | Skill uses `context: fork` or `agent: Explore` | Recognise as valid frontmatter; no fail. If `context: fork` is set, Dimension 5 adds an info note checking that the rationale is documented. |
| E7 | Skill uses `paths:` auto-activation | Valid field. Warn at info level if `paths` globs are so broad they match general files (e.g. `**/*.md`, `**/*`). |
| E8 | Lowercase `skill.md` | Recognised alongside `SKILL.md`; no fail. Note as info. |
| E9 | Orphan `reference.md` — present but never linked from SKILL.md | C20-inverse; warn. |
| E10 | `$ARGUMENTS` empty | `resolve-target.sh` emits `error=empty-argument` plus discovery listing; evaluator prompts the user. |

---

## Scripts Catalogue

Lightweight helpers under `scripts/`. Each is self-documenting; see the header comment in each file.

- `resolve-target.sh` — `$ARGUMENTS` → absolute skill directory
- `parse-frontmatter.sh` — YAML frontmatter → JSON (prefers `yq`, awk fallback)
- `line-count-check.sh` — line count with pass/warn/fail against 500-line cap
- `check-aus-english.sh` — grep American spellings outside fenced code blocks
- `list-skill-files.sh` — enumerate files with size and line count
- `referenced-paths.sh` — extract local file references from SKILL.md
