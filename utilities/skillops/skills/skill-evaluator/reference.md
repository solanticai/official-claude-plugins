# Skill Evaluator — Reference

Dense material extracted from `SKILL.md` to keep it under the 500-line cap. Three sections:

1. [Scoring rubric](#1-scoring-rubric) — per-dimension checkpoint breakdown and score computation.
2. [Heuristic check catalogue](#2-heuristic-check-catalogue) — all 35 deterministic checks with patterns, severities, and fix templates.
3. [Grade boundaries, dimension weighting rationale, and edge-case notes](#3-grade-boundaries-weighting-rationale-and-edge-case-notes).

---

## 1. Scoring rubric

Total score = Σ per-dimension deterministic points + Σ per-dimension qualitative contribution (full mode only).

### Dimension 1 — Discovery & Metadata (weight 20 = 15 det + 5 qual)

Five deterministic checkpoints worth 3 pts each:

| ID | Checkpoint | Pts | Failure cost |
|---|---|---:|---:|
| D1.1 | Required frontmatter fields all present (`name`, `description`, `argument-hint`, `allowed-tools`, `effort`) | 3 | −3 per missing field, up to −3 total |
| D1.2 | `description` length 50–250 chars | 3 | fail → −3; 200–250 info (no cost) |
| D1.3 | `name` kebab-case, ≤ 64 chars, not reserved, matches dir | 3 | fail → −3 |
| D1.4 | `argument-hint` present, bracketed, non-trivial | 3 | missing → −3; `[args]` → −1.5 (warn) |
| D1.5 | `effort` is a valid value (`low`/`medium`/`high`/`max`) | 3 | invalid → −1.5 (warn) |

Qualitative contribution: up to 5 pts, mapped from the sub-agent's `discovery_metadata` score (0–5 → 0–5 pts).

### Dimension 2 — Scope & Focus (weight 15 = 9 det + 6 qual)

Three checkpoints worth 3 pts each:

| ID | Checkpoint | Pts |
|---|---|---:|
| D2.1 | Title H1 contains a single action verb, no `and` conjunction | 3 |
| D2.2 | Description names ≤ 3 primary outputs (comma + "and" count < 4) | 3 |
| D2.3 | `$ARGUMENTS` used in the body (user-input driven) | 3 |

Qualitative contribution: up to 6 pts, mapped from `scope_focus` score. This dimension leans qualitative because single-purpose-ness and actionability need human judgement.

### Dimension 3 — Conciseness (weight 15 = 12 det + 3 qual)

Four checkpoints worth 3 pts each:

| ID | Checkpoint | Pts |
|---|---|---:|
| D3.1 | SKILL.md ≤ 500 lines | 3 — fail if >500, warn if 450–500 |
| D3.2 | No duplicate H2/H3 headings between SKILL.md and reference.md | 3 |
| D3.3 | No generic "what is a skill" preamble at H2 level | 3 |
| D3.4 | `reference.md` present iff SKILL.md > 350 lines OR dense tables detected | 3 |

Qualitative: up to 3 pts from `conciseness` (over-explanation detection).

### Dimension 4 — Information Architecture (weight 15 = 10 det + 5 qual)

Five checkpoints worth 2 pts each:

| ID | Checkpoint | Pts |
|---|---|---:|
| D4.1 | `reference.md` has a table of contents if > 200 lines | 2 |
| D4.2 | Heading depth in reference.md ≤ 3 (no H4+) | 2 |
| D4.3 | Every `reference.md` section referenced at least once from SKILL.md | 2 |
| D4.4 | Links use relative forward-slash paths | 2 |
| D4.5 | No circular references between reference.md and SKILL.md | 2 |

Qualitative: up to 5 pts from `information_architecture` (navigability).

### Dimension 5 — Content Quality (weight 15 = 8 det + 7 qual)

Four checkpoints worth 2 pts each:

| ID | Checkpoint | Pts |
|---|---|---:|
| D5.1 | At least one Phase has explicit Inputs and Outputs spelled out | 2 |
| D5.2 | Every `scripts/*.sh` has a shebang on line 1 | 2 |
| D5.3 | Every bash script uses `set -euo pipefail` (or equivalent) | 2 |
| D5.4 | Magic numbers in scripts have a comment within 3 lines | 2 |

Qualitative: up to 7 pts — highest qualitative cap in the rubric. Terminology consistency, phase sequencing, and error handling all feed here.

### Dimension 6 — Tool & Security (weight 10 = 10 det)

Five checkpoints worth 2 pts each. Fully deterministic.

| ID | Checkpoint | Pts |
|---|---|---:|
| D6.1 | `allowed-tools` declared in frontmatter | 2 |
| D6.2 | No unscoped `Bash(*)` or bare `Bash` without a justification note | 2 |
| D6.3 | MCP tools use the `mcp__<server>__<tool>` prefix | 2 |
| D6.4 | No secret-like literals anywhere in the skill files | 2 — fail costs the full 2 |
| D6.5 | External dependencies (`yq`, `jq`, `psql`, `gh`, `node`, etc.) are documented | 2 |

### Dimension 7 — Testing & Examples (weight 7 = 3 det + 4 qual)

Three checkpoints worth 1 pt each:

| ID | Checkpoint | Pts |
|---|---|---:|
| D7.1 | `examples/` has ≥ 1 `.md` | 1 |
| D7.2 | `templates/` has ≥ 1 file | 1 |
| D7.3 | No lorem-ipsum / TODO / TBD in examples | 1 |

Qualitative: up to 4 pts from `testing_examples` (example realism).

### Dimension 8 — Standards Compliance (weight 3 = 3 det)

Six checkpoints worth 0.5 pt each:

| ID | Checkpoint | Pts |
|---|---|---:|
| D8.1 | Valid YAML frontmatter (parseable) | 0.5 |
| D8.2 | Forward slashes in paths throughout | 0.5 |
| D8.3 | Australian English spellings in narrative | 0.5 |
| D8.4 | `LICENSE.txt` present | 0.5 |
| D8.5 | No time-bound statements ("before August 2025", etc.) | 0.5 |
| D8.6 | File and directory names are kebab-case | 0.5 |

### Grade mapping

Applied to the total score AND to each per-dimension score (scaled to the dimension's weight):

| Grade | Range (% of weight) |
|---|---|
| A | ≥ 90% |
| B | 75–89% |
| C | 60–74% |
| D | 45–59% |
| F | < 45% |

---

## 2. Heuristic check catalogue

35 checks. Each row: **ID** · **Dimension** · **Severity** · **Test** · **Fix template**.

Severities: `fail` (hard failure, deducts full checkpoint value), `warn` (half deduction), `info` (logged, no deduction).

| ID | Dim | Sev | Test | Fix template |
|---|---:|---|---|---|
| **C01** | 1 | fail | `len(fm.description) > 250` | Trim description to ≤ 250 chars; front-load the action verb and primary output. |
| **C02** | 1 | fail | `len(fm.description) < 50` | Expand description to 50–250 chars: action verb + use case + primary output. |
| **C03** | 1 | warn | `fm.description` matches `/\b(I|me|my|we|our)\b/i` | Rewrite in third-person imperative voice ("Audit…", "Produces…"). |
| **C04** | 1 | warn | First 100 chars of `fm.description` lack an action verb from `{audit, create, generate, review, analyse, produce, build, scan, extract, convert, migrate, refactor, evaluate, score}` | Lead the description with a concrete action verb. |
| **C05** | 1 | fail | `fm.name` fails `/^[a-z0-9]+(-[a-z0-9]+)*$/` | Rename the directory and `name` field to kebab-case. |
| **C06** | 1 | fail | `len(fm.name) > 64` | Shorten `name` to ≤ 64 characters. |
| **C07** | 1 | fail | `fm.name` is `claude` or `anthropic`, or contains as a standalone kebab token | Pick a domain-specific name. |
| **C08** | 1 | fail | `fm.name != basename(target_dir)` | Align the `name` field with the directory name. |
| **C09** | 1 | fail | Any of `{name, description, argument-hint, allowed-tools, effort}` missing from frontmatter | Add the missing field. |
| **C10** | 1 | warn | `fm.effort ∉ {low, medium, high, max}` | Use a standard effort level. |
| **C11** | 2 | warn | No occurrence of `$ARGUMENTS` in SKILL.md body | Accept user input via `$ARGUMENTS` somewhere in the body. |
| **C12** | 2 | warn | H1 title contains ` and ` | Consider splitting into two skills, or rename around a single concept. |
| **C13** | 2 | info | Count of `,` + ` and ` in `fm.description` ≥ 4 | Description names many outputs — consider whether the skill is single-purpose. |
| **C14** | 3 | fail | `wc -l SKILL.md > 500` | Extract dense content to `reference.md`. |
| **C15** | 3 | warn | `450 < wc -l SKILL.md ≤ 500` | Approaching the 500-line cap — plan extraction before it fails. |
| **C16** | 3 | info | Any H2 matching `/what is a skill\|about this document/i` | Remove generic preamble — readers know the format. |
| **C17** | 3 | warn | Non-empty intersection of H2/H3 heading text between SKILL.md and reference.md | Keep each heading canonical in exactly one file. |
| **C18** | 4 | warn | reference.md > 200 lines AND no `## Table of Contents` or `- [text](#anchor)` block in the first 40 lines | Add a table of contents to the top of reference.md. |
| **C19** | 4 | warn | Any `####` or deeper heading in reference.md | Flatten heading depth to ≤ 3. |
| **C20** | 4 | fail | A path referenced from SKILL.md does not exist on disk | Either create the referenced file or remove the reference. |
| **C21** | 4/8 | warn | `/\\[a-zA-Z]/` in any markdown file | Use forward slashes in paths, not backslashes. |
| **C22** | 5 | warn | First line of a `scripts/*.sh` file is not `#!...` | Add `#!/usr/bin/env bash` (or appropriate shebang) on line 1. |
| **C23** | 5 | warn | Bash script lacks `set -euo pipefail` (or `set -e` at minimum) | Add `set -euo pipefail` near the top for strict-mode error handling. |
| **C24** | 5 | info | `/\b\d{2,}\b/` in scripts with no comment within 3 lines | Add a comment explaining the constant, or promote it to a named variable. |
| **C25** | 6 | warn | `allowed-tools` contains `Bash(*)` or bare `Bash` without an accompanying justification in the body | Scope `Bash` usage (e.g. `Bash(git *)`) or document why unrestricted use is needed. |
| **C26** | 6 | warn | Any string in `allowed-tools` matching `/\bmcp[_-]/i` that does not start with `mcp__` | Use the `mcp__<server>__<tool>` prefix format. |
| **C27** | 6 | fail | Match of `/(AKIA[0-9A-Z]{16}\|sk-ant-[A-Za-z0-9_-]{20,}\|ghp_[A-Za-z0-9]{20,}\|xox[baprs]-[A-Za-z0-9-]{10,}\|-----BEGIN [A-Z ]+PRIVATE KEY-----)/` in any skill file | Remove the secret, rotate the credential, and reference it via environment variable instead. |
| **C28** | 7 | fail | `examples/` missing or contains no `.md` | Add at least one realistic `examples/example-output.md`. |
| **C29** | 7 | fail | `templates/` missing or empty | Add an output template matching the declared Output Format. |
| **C30** | 7 | warn | `examples/*.md` contains `/lorem ipsum\|foo bar baz\|TBD\|TODO\|placeholder/i` | Replace placeholders with domain-realistic content. |
| **C31** | 8 | warn | `check-aus-english.sh` reports any hits | Use Australian spellings in narrative markdown. |
| **C32** | 8 | warn | Match of `/\b(before\|after\|until\|as of)\s+(january\|february\|march\|april\|may\|june\|july\|august\|september\|october\|november\|december\|20\d{2})/i` | Remove time-bound statement or rephrase to be time-agnostic (use "deprecated" sections instead). |
| **C33** | 8 | info | `LICENSE.txt` missing | Copy the LICENSE.txt from a sibling skill. |
| **C34** | 8 | warn | `parse-frontmatter.sh` returns a non-zero exit code | Fix YAML syntax — check indentation, colons, quoted strings. |
| **C35** | 6 | warn | Scripts reference `yq`, `jq`, `psql`, `gh`, or `node` and neither SKILL.md nor a `scripts/README.md` mentions the dependency | Document the runtime dependency in SKILL.md or add a `scripts/README.md`. |

---

## 3. Grade boundaries, weighting rationale, and edge-case notes

### Why Dimension 1 is 20%

Discovery is the biggest lever on whether a skill gets used. A skill that Claude cannot discover is effectively absent. Metadata is also the cheapest thing to get right — the checkpoints here cost no extra engineering work beyond thoughtful wording, so failing them signals low attention to detail across the whole artefact.

### Why Dimension 5 weights qualitative heavily (7/15)

Terminology drift, phase sequencing quality, and error-handling depth all resist regex. Mechanical checks detect shebangs and strict-mode flags but cannot tell if a phase's inputs actually map to a later phase's expected state. A sub-agent reading the whole skill catches these; the rubric weights accordingly.

### Why Dimension 6 has zero qualitative weight

Tool and security checks are entirely deterministic: fields either are or are not present, patterns either match or do not. Introducing qualitative judgement here would dilute a dimension that should be crisp.

### Why Dimension 8 is only 3%

Standards are necessary but not sufficient. A skill with perfect Australian spelling and forward-slash paths can still be useless; a skill that audits useful things can tolerate one American "color". Low weight reflects that.

### Severity-to-deduction mapping

The rubric's per-checkpoint max scores assume each deterministic checkpoint is either fully met (full points) or failed (zero points). The heuristic catalogue introduces three severities mapped to partial-credit deductions:

- `fail` — subtract the full checkpoint value
- `warn` — subtract half the checkpoint value
- `info` — log only; no deduction

When multiple checks in the catalogue feed one checkpoint (e.g. Dimension 1's D1.3 "name valid" is fed by C05/C06/C07/C08), the worst severity wins — a single `fail` caps the checkpoint at 0 regardless of whether other checks passed.

### Edge-case notes

- **`paths:` frontmatter field** — valid; info-level warning if globs are broader than two directory levels (e.g. `**/*.md`).
- **`context: fork`** — valid; Dimension 5 adds an info note to confirm the body explains the rationale for forking (useful for research skills, not for reporting skills that need the user's cwd).
- **`disable-model-invocation: true`** — valid; skill is user-invocable only. Dimension 1 still requires `description` but relaxes the trigger-word check (C04 becomes info-only).
- **Self-evaluation** — `skill-evaluator` evaluated against itself should score ≥ 85. If it does not, the rubric is probably too strict for its own check list; re-examine.
- **Report file inside target_dir** — if the evaluator's output accidentally lands inside `target_dir`, the next run will flag the `.md` report file as an orphan artefact; this is working as designed and signals that the user ran the evaluator from within the wrong directory.
- **Symlinked directories** — `list-skill-files.sh` uses `find` without `-L`, so symlinks to directories are not followed. Intentional.
