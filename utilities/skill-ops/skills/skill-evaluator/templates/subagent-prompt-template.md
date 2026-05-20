# Qualitative Skill Review — Sub-agent Prompt

You are evaluating the quality of a Claude Code skill. Heuristic checks have already run; your job is the judgement-call layer that regex cannot catch. Score eight dimensions on a 0–5 scale and return structured JSON only — no prose outside the JSON block.

## Target

- **Skill name:** `{{skill_name}}`
- **Plugin:** `{{plugin_name}}`
- **Target directory:** `{{target_dir}}`

## Materials

### SKILL.md

```markdown
{{skill_md_content}}
```

### reference.md

```markdown
{{reference_md_content}}
```

### Example output

```markdown
{{example_md_content}}
```

## Evaluation questions (0–5 each)

For each question, return `score` (integer 0–5) and `note` (≤ 30 words, specific: cite a line number or quote a phrase).

1. **Front-loading** — Do the first 100 characters of the `description` field convey the core action and primary output? A strong description names the action verb and the artefact it produces.
2. **Single-purpose** — Is the skill focused on one coherent task, or does it bundle unrelated responsibilities? Presence of `and` in the title or multiple primary outputs in the description is a signal of kitchen-sink scope.
3. **Actionability** — Does the skill produce a concrete output (a report, a diagram, a file, a set of changes) or is it guidance/rules-only without a deliverable?
4. **Example realism** — Is `examples/example-output.md` populated with domain-realistic content, or does it use placeholder text (lorem-ipsum, `foo/bar`, `TBD`)?
5. **Over-explanation** — Does SKILL.md explain things Claude already knows (what markdown is, what a PDF is, generic "this skill does X" preambles)?
6. **Terminology consistency** — Are the same terms used consistently across SKILL.md, reference.md, and the example? (e.g. "dimension" vs "category" vs "pillar" should not drift.)
7. **Phase sequencing** — Are the phases genuinely sequential with clear boundaries, or do they overlap / could they run in any order? Well-designed phases pass state forward.
8. **Error / edge-case handling** — Are failure paths and edge cases named and addressed in the text, or hand-waved? Look for an explicit "Edge Cases" section plus per-phase error notes.

## Output format (return ONLY this JSON, no surrounding prose)

```json
{
  "qualitative_scores": {
    "discovery_metadata":        { "score": 0, "note": "" },
    "scope_focus":               { "score": 0, "note": "" },
    "conciseness":               { "score": 0, "note": "" },
    "information_architecture":  { "score": 0, "note": "" },
    "content_quality":           { "score": 0, "note": "" },
    "tool_security":             { "score": 0, "note": "" },
    "testing_examples":          { "score": 0, "note": "" },
    "standards_compliance":      { "score": 0, "note": "" }
  },
  "qualitative_findings": [
    { "dimension": "scope_focus", "severity": "warn", "note": "Title bundles 'audit and fix' — consider splitting." }
  ]
}
```

Map the eight questions to dimensions as follows:

| Question | Dimension |
|---|---|
| 1 Front-loading | discovery_metadata |
| 2 Single-purpose | scope_focus |
| 3 Actionability | scope_focus _(contributes alongside Q2)_ |
| 4 Example realism | testing_examples |
| 5 Over-explanation | conciseness |
| 6 Terminology consistency | content_quality |
| 7 Phase sequencing | content_quality _(contributes alongside Q6)_ |
| 8 Error handling | content_quality _(contributes alongside Q6, Q7)_ |

For dimensions that receive multiple questions, return the average (rounded to the nearest integer 0–5). For dimensions not covered by questions (information_architecture, tool_security, standards_compliance), return `score: 0` and `note: "not applicable to qualitative review"` — the deterministic layer handles them.
