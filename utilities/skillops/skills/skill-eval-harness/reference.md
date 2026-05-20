# Skill Eval Harness — Reference

Dense material extracted from SKILL.md so the main file stays scannable. Three sections:

1. [Test-case schema](#1-test-case-schema)
2. [Judge taxonomy](#2-judge-taxonomy)
3. [Scoring rules and regression semantics](#3-scoring-rules-and-regression-semantics)

---

## 1. Test-case schema

A suite file lives at `<skill-dir>/evals/suite.yaml` and matches this shape:

```yaml
skill: <kebab-case skill name>           # required
description: <one line>                  # optional
test_cases:                              # required, length ≥ 7 (3 positive activation + 2 negative + 2 edge)
  - id: <kebab-case>                     # required, unique within suite
    kind: activation | functional | edge-case | regression
    description: <one line>              # required
    user_input: <string or null>         # required (null means "no input")
    expected_activation: true | false    # set for kind=activation
    expected_outputs:                    # set for kind=functional
      - kind: file_created
        path_glob: "<glob>"              # e.g. "skill-evaluation-*.md"
      - kind: contains
        text: "<substring>"
      - kind: matches
        pattern: "<regex>"
      - kind: equals
        value: "<exact string>"
    expected_error: <error-code or regex> # set for kind=edge-case
    judge_criteria:                      # optional, list of strings; LLM-as-judge
      - "..."
      - "..."
    timeout_seconds: <int>               # optional, default 120
    tags: [<tag>, ...]                   # optional, free-form for filtering
```

### Required test-category mix

A suite is considered **complete** when it has at least:

- **3** activation-positive cases (`expected_activation: true`)
- **2** activation-negative cases (`expected_activation: false`)
- **2** edge-case cases (`expected_error` set)

The harness warns (not fails) when a suite is below this mix; `skill-eval-bootstrap` generates a baseline that meets it.

---

## 2. Judge taxonomy

The harness uses two independent judging layers:

### Deterministic layer (always run)

| Test kind | What the deterministic judge checks |
|---|---|
| activation | `expected_activation` matches `check-activation.sh` verdict |
| functional | every entry in `expected_outputs[]` is satisfied — file globs match, text appears, regex matches |
| edge-case | the skill's emitted error matches `expected_error` (literal or regex) |
| regression | the artefact diff against a previous run is empty for stable cases |

A case passes the deterministic layer iff **every** declared check passes. Partial matches are `fail`, not `partial` (the LLM judge handles partial credit).

### Qualitative layer (LLM-as-judge, skipped when `--mode=fast`)

Triggered for functional cases with non-empty `judge_criteria`. Independence rule: the judge runs in a fresh `Agent` context with `subagent_type: "Explore"`. No prior conversation history is fed in; only the artefact, the criteria, and a strict output schema.

Judge prompt schema (see `templates/judge-prompt-template.md`):

```
You are grading the output of a Claude Code skill. Read the artefact below
and verify each criterion. Return JSON only.

Criteria:
1. {{criterion_1}}
2. {{criterion_2}}
...

Artefact:
```
{{artefact_text}}
```

Output schema:
{
  "verdict": "pass" | "fail" | "partial",
  "criterion_results": [{"text": "...", "met": true|false, "evidence": "..."}],
  "notes": "<one paragraph>"
}
```

The judge's `verdict` overrides a deterministic-pass to `partial` if `criterion_results[].met` is mixed, but a deterministic-fail is never upgraded by the judge.

---

## 3. Scoring rules and regression semantics

### Pass-rate calculation

```
pass_rate = (cases where deterministic=pass AND (mode=fast OR judge != fail)) / total
```

`partial` counts as 0.5 of a pass in the pass-rate; reported separately in the breakdown table.

### Regression detection

The harness compares the current run against the most recent prior run **for the same skill** (matched by suite `skill:` value, not file path).

A case is a **regression** when:
- Its `id` exists in both runs
- Prior run = `pass`, current run = `fail` or `partial`

A case is a **win** when:
- Its `id` exists in both runs
- Prior run = `fail`/`partial`, current run = `pass`

New cases (added since the last run) are reported separately — they count toward pass-rate but not toward regressions or wins.

### Iteration-log row

Each run appends one row to `<skill-dir>/evals/iteration-log.md`:

```
| Date | Pass-rate | Regressions | Wins | New | Mode | Notes |
|---|---:|---:|---:|---:|---|---|
| 2026-05-20 14:32 | 92% (12/13) | 0 | 1 | 0 | full | Removed unused Agent token |
```

The `Notes` column is one short sentence; the run report has the detail. The skill-eval-harness skill writes this row automatically.

### Grade boundaries

| Grade | Pass-rate |
|---|---|
| A | ≥ 90% |
| B | 75–89% |
| C | 60–74% |
| D | 45–59% |
| F | < 45% |

The grade is shown in the chat summary header.
