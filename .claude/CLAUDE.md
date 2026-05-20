# Anthril Claude Plugins — Development Standards

## Conventions

- **Australian English** in all narrative text (colour, optimise, behaviour, organisation)
- **Markdown-first** outputs — every skill produces structured markdown
- **Evidence-backed** — findings include file:line references and confidence scores where applicable

## Skill Structure

Every skill lives under `<category>/<plugin-name>/skills/<skill-name>/` (where `<category>` is one of `lifestyle`, `smb`, `marketing`, `engineering`, `data-science`, `economics`, `utilities`) and must contain:

```
<skill-name>/
├── SKILL.md              # Main skill instructions (under 500 lines)
├── LICENSE.txt           # MIT or Apache 2.0
├── templates/
│   └── output-template.md    # Output format skeleton with {{placeholders}}
└── examples/
    └── example-output.md     # Realistic completed example
```

Optional:

- `reference.md` — Dense reference material (SQL templates, scoring rubrics, lookup tables) extracted to keep SKILL.md under 500 lines
- `scripts/` — Python or Bash helpers for the skill

## SKILL.md Frontmatter

Every SKILL.md begins with YAML frontmatter:

```yaml
---
name: skill-name-in-kebab-case
description: Under 250 characters, front-loaded with key use case
argument-hint: [what-the-user-should-provide]
allowed-tools: Read Write Edit Glob Grep Bash Agent
effort: medium
---
```

### Required Fields

| Field | Description |
|-------|-------------|
| `name` | Kebab-case identifier matching the directory name |
| `description` | Under 250 characters, front-loaded with the primary use case |
| `argument-hint` | Bracketed hint shown to users (e.g., `[business-model-description]`) |
| `allowed-tools` | Space-separated list of Claude Code tools the skill may use |
| `effort` | Complexity level: `low`, `medium`, `high`, or `max` |

### Optional Fields

| Field | Description |
|-------|-------------|
| `context: fork` | Run skill in an isolated subagent context |
| `agent: Explore` | Specify agent type for subagent execution |
| `ultrathink` | Enable extended thinking for complex analytical skills |
| `paths` | Glob patterns for auto-activation on matching files |

## SKILL.md Body

After frontmatter, structure the skill as:

1. **Title** (`# Skill Name`) — followed by `ultrathink` on its own line if needed
2. **User Context** — receives `$ARGUMENTS` from the user
3. **System Prompt** — defines the persona and constraints
4. **Phases** — sequential workflow steps (typically 3-6 phases)
5. **Output Specification** — references the output template

### Phase Pattern

```markdown
## Phase N: Phase Title

### Objective
What this phase accomplishes.

### Steps
1. Step one
2. Step two

### Output
What this phase produces.
```

## Plugin Structure

Each plugin lives under `<category>/<plugin-name>/` and must contain:

```
<plugin-name>/
├── .claude-plugin/
│   └── plugin.json           # Plugin manifest
├── skills/
│   └── <skill-name>/         # One or more skills
├── hooks/                    # Optional lifecycle hooks
│   ├── hooks.json
│   └── scripts/
│       └── suggest-related.sh
├── settings.json             # Plugin settings (usually empty {})
└── README.md                 # Plugin-level documentation
```

## Plugin Manifest (`plugin.json`)

```json
{
  "name": "plugin-name",
  "version": "1.0.0",
  "description": "Short description of what the plugin provides",
  "author": {
    "name": "Anthril",
    "email": "john@anthril.com",
    "url": "https://github.com/anthril"
  },
  "homepage": "https://github.com/anthril/official-claude-plugins/tree/main/<category>/plugin-name",
  "repository": "https://github.com/anthril/official-claude-plugins",
  "license": "MIT",
  "keywords": ["relevant", "keywords"],
  "skills": "./skills/",
  "hooks": "./hooks/hooks.json"
}
```

## Marketplace Registration

When adding a new plugin, add an entry to `.claude-plugin/marketplace.json`:

```json
{
  "name": "plugin-name",
  "version": "1.0.0",
  "description": "Short description",
  "source": "./<category>/plugin-name",
  "category": "category-name",
  "homepage": "https://github.com/anthril/official-claude-plugins/tree/main/<category>/plugin-name"
}
```

Categories: `lifestyle`, `smb`, `marketing`, `engineering`, `data-science`, `economics`, `utilities`

## Hooks

The standard Stop hook suggests related skills after a skill completes:

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash \"${CLAUDE_PLUGIN_ROOT}/hooks/scripts/suggest-related.sh\"",
            "timeout": 5
          }
        ]
      }
    ]
  }
}
```

## Version Management

- Marketplace entry version in `marketplace.json` **must match** the plugin's `plugin.json` version
- Use semantic versioning (MAJOR.MINOR.PATCH)
- Run `node scripts/check-versions.mjs` to validate consistency

## Quality Checklist

Before submitting a new skill:

- [ ] SKILL.md has valid YAML frontmatter with `name`, `description`, `effort`
- [ ] SKILL.md is under 500 lines
- [ ] Uses `$ARGUMENTS` for user input
- [ ] Description is under 250 characters, front-loaded with key use case
- [ ] `effort` field set appropriately (`medium`, `high`, or `max`)
- [ ] `templates/` directory has at least one output template
- [ ] `examples/` directory has at least one example output
- [ ] Dense reference material is in `reference.md`, not SKILL.md
- [ ] Australian English used throughout
- [ ] Tested locally with `claude --plugin-dir .`
