# Eval run — {{skill_name}}

**Date:** {{run_date}} · **Mode:** {{mode}} · **Pass-rate:** {{passed}}/{{total}} ({{pct}}%) · **Grade:** {{grade}}

{{regression_banner}}

## Summary

| Metric | Value |
|---|---:|
| Total cases | {{total}} |
| Passed | {{passed}} |
| Partial | {{partial}} |
| Failed | {{failed}} |
| Skipped | {{skipped}} |
| Regressions | {{regressions}} |
| Wins | {{wins}} |
| New cases | {{new_cases}} |

## Per-case results

| ID | Kind | Verdict | Judge | Notes |
|---|---|---|---|---|
{{#each results}}
| {{id}} | {{kind}} | {{verdict}} | {{judge_verdict}} | {{notes}} |
{{/each}}

## Regressions ({{regressions}})

{{#each regressed}}
- **{{id}}** ({{kind}}) — {{reason}}
{{/each}}

## Wins ({{wins}})

{{#each won}}
- **{{id}}** ({{kind}}) — now passing
{{/each}}

## Failing-case detail

{{#each failed_cases}}
### {{id}} — {{kind}}

**Description:** {{description}}

**Expected:** {{expected}}

**Got:** {{actual}}

**Judge notes:** {{judge_notes}}

{{/each}}

---

_Full JSON sidecar: `skill-eval-run-{{skill_name}}-{{date_slug}}.json`._
_Iteration log appended to: `{{target_dir}}/evals/iteration-log.md`._
