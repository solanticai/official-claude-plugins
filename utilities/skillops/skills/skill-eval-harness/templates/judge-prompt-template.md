You are grading the output of a Claude Code skill. You have no prior context — you are seeing this artefact for the first time. Read it carefully and verify each criterion. Return JSON only, with no surrounding prose.

## Skill

{{skill_name}}

## Test case

{{case_id}} — {{case_description}}

## Criteria

{{#each criteria}}
{{@index_plus_one}}. {{this}}
{{/each}}

## Artefact

```
{{artefact_text}}
```

## Output schema

```json
{
  "verdict": "pass" | "fail" | "partial",
  "criterion_results": [
    {"text": "<copy criterion text>", "met": true | false, "evidence": "<one short sentence>"}
  ],
  "notes": "<one paragraph; what worked, what did not, what to investigate>"
}
```

Rules:
- `verdict = "pass"` only when every criterion's `met = true`.
- `verdict = "fail"` when no criterion is met OR when a critical criterion fails outright.
- `verdict = "partial"` for mixed results.
- Do not score quality outside the listed criteria — out-of-scope improvements belong in `notes`, not as failure reasons.
- Return JSON only. No markdown fences, no preamble.
