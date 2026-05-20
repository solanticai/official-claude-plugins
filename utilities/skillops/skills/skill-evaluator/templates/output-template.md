# Skill Evaluation: {{skill_name}}

**Plugin:** `{{plugin_name}}`
**Target:** `{{target_dir}}`
**Evaluated:** {{date}}
**Evaluator version:** {{evaluator_version}}
**Mode:** {{mode}}  <!-- full | fast -->

---

## Summary

**Score: {{total_score}} / 100 — Grade {{grade}}**

{{one_sentence_verdict}}

### Dimension scores

| # | Dimension | Score | Weight | Grade |
|---|---|---:|---:|---|
| 1 | Discovery & Metadata | {{d1.score}} | 20 | {{d1.grade}} |
| 2 | Scope & Focus | {{d2.score}} | 15 | {{d2.grade}} |
| 3 | Conciseness | {{d3.score}} | 15 | {{d3.grade}} |
| 4 | Information Architecture | {{d4.score}} | 15 | {{d4.grade}} |
| 5 | Content Quality | {{d5.score}} | 15 | {{d5.grade}} |
| 6 | Tool & Security | {{d6.score}} | 10 | {{d6.grade}} |
| 7 | Testing & Examples | {{d7.score}} | 7 | {{d7.grade}} |
| 8 | Standards Compliance | {{d8.score}} | 3 | {{d8.grade}} |

---

## Frontmatter snapshot

| Field | Value | Status |
|---|---|---|
| `name` | {{fm.name}} | {{fm.name.status}} |
| `description` | _{{fm.description}}_ ({{desc_len}} chars) | {{fm.description.status}} |
| `argument-hint` | {{fm.argument_hint}} | {{fm.argument_hint.status}} |
| `allowed-tools` | {{fm.allowed_tools}} | {{fm.allowed_tools.status}} |
| `effort` | {{fm.effort}} | {{fm.effort.status}} |

---

## Findings

### Dimension 1 — Discovery & Metadata ({{d1.score}}/20)

{{#each d1.findings}}
- **[{{severity}}] {{id}} · {{title}}** — `{{file}}:{{line}}`
  - Evidence: `{{evidence}}`
  - Fix: {{fix}}
{{/each}}

### Dimension 2 — Scope & Focus ({{d2.score}}/15)

{{#each d2.findings}}
- **[{{severity}}] {{id}} · {{title}}** — `{{file}}:{{line}}`
  - Evidence: `{{evidence}}`
  - Fix: {{fix}}
{{/each}}

### Dimension 3 — Conciseness ({{d3.score}}/15)

{{#each d3.findings}}
- **[{{severity}}] {{id}} · {{title}}** — `{{file}}:{{line}}`
  - Evidence: `{{evidence}}`
  - Fix: {{fix}}
{{/each}}

### Dimension 4 — Information Architecture ({{d4.score}}/15)

{{#each d4.findings}}
- **[{{severity}}] {{id}} · {{title}}** — `{{file}}:{{line}}`
  - Evidence: `{{evidence}}`
  - Fix: {{fix}}
{{/each}}

### Dimension 5 — Content Quality ({{d5.score}}/15)

{{#each d5.findings}}
- **[{{severity}}] {{id}} · {{title}}** — `{{file}}:{{line}}`
  - Evidence: `{{evidence}}`
  - Fix: {{fix}}
{{/each}}

### Dimension 6 — Tool & Security ({{d6.score}}/10)

{{#each d6.findings}}
- **[{{severity}}] {{id}} · {{title}}** — `{{file}}:{{line}}`
  - Evidence: `{{evidence}}`
  - Fix: {{fix}}
{{/each}}

### Dimension 7 — Testing & Examples ({{d7.score}}/7)

{{#each d7.findings}}
- **[{{severity}}] {{id}} · {{title}}** — `{{file}}:{{line}}`
  - Evidence: `{{evidence}}`
  - Fix: {{fix}}
{{/each}}

### Dimension 8 — Standards Compliance ({{d8.score}}/3)

{{#each d8.findings}}
- **[{{severity}}] {{id}} · {{title}}** — `{{file}}:{{line}}`
  - Evidence: `{{evidence}}`
  - Fix: {{fix}}
{{/each}}

---

## Prioritised fix list (top 15)

1. **[{{severity}}] {{id}}** · {{title}} — `{{file}}:{{line}}` — {{fix}}
2. ...

_Full list in the JSON sidecar (`skill-evaluation-{{skill_name}}-{{date}}.json`)._

---

## Qualitative review (sub-agent)

{{#if qualitative}}
{{#each qualitative_findings}}
- **{{dimension}} ({{score}}/5)**: {{note}}
{{/each}}
{{else}}
_Fast mode — qualitative review skipped. Maximum achievable score in fast mode: 70/100._
{{/if}}

---

## Appendix — files inspected

| File | Lines | Size (bytes) |
|---|---:|---:|
{{#each files}}
| `{{path}}` | {{lines}} | {{size}} |
{{/each}}
