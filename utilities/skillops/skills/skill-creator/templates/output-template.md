# Skill Creator Output Template

## Skill Directory Structure

```
skills/<skill-name>/
├── skill.md
├── reference.md          (if needed)
├── LICENSE.txt
├── templates/
│   └── output-template.md
├── examples/
│   └── example-output.md
└── scripts/              (if relevant)
    └── helper.py
```

## Generated SKILL.md Structure

```yaml
---
name: <skill-name>
description: <max 250 chars>
argument-hint: [<hint>]
allowed-tools: <tools>
---
```

### Phases
- Phase 1: [Context Collection]
- Phase 2: [Analysis/Design]
- Phase 3: [Generation/Output]
- ...

### Output Format
[Section headers and descriptions]

### Behavioural Rules
1. [Rule 1]
2. ...

### Edge Cases
1. [Case 1]
2. ...

## Validation Checklist

- [ ] SKILL.md under 500 lines
- [ ] Valid YAML frontmatter
- [ ] Description under 250 characters
- [ ] $ARGUMENTS used for user input
- [ ] ultrathink included (if warranted)
- [ ] templates/ directory populated
- [ ] examples/ directory populated
- [ ] reference.md created (if SKILL.md would exceed 400 lines)
