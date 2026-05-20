# Brand Manager — Anthril Plugin

A complete brand creation toolkit for Claude Code. Nine interview-driven skills that take a business from idea to a finished, design-handoff-ready brand system: foundational identity, audience and competitor mapping, visual standards, design tokens, website copy, and legal artefacts.

---

## Skills

| # | Skill | Purpose |
|---|---|---|
| 1 | `brand-identity` | Generate the foundational identity — mission, vision, values, voice, tone, and Jung archetype mapping |
| 2 | `brand-guidelines` | Compile a complete brand book covering logo, colour, typography, imagery, and voice rules |
| 3 | `target-audience` | Build ICP, personas, jobs-to-be-done, and channel preferences |
| 4 | `competitor-analysis` | Audit competitors and produce a positioning map plus white-space opportunities |
| 5 | `logo-brief` | Create a designer-ready (or AI-image-generator-ready) logo brief with concept directions |
| 6 | `color-palette` | Generate a brand palette in HEX/RGB/HSL/OKLCH with WCAG-validated contrast pairs |
| 7 | `design-tokens` | Export tokens to CSS variables, Tailwind config, JSON, and Style Dictionary |
| 8 | `legal-disclaimers` | Draft jurisdiction-aware legal disclaimers, privacy notices, cookie banners, and ToS outlines |
| 9 | `website-copy` | Generate SEO-aware, conversion-focused website copy across home, about, features, pricing, and contact |

Each skill is interview-driven, follows a 3–6 phase workflow, ships with a markdown output template, a worked example, an Apache 2.0 LICENSE, and (where useful) a reference.md and CLI helper script.

---

## Installation

### Local development

```bash
claude --plugin-dir ./brand-manager
```

After Claude Code starts, run `/reload-plugins` to discover the skills.

### Marketplace install

If installed from a marketplace, the plugin lives under your plugins folder and the skills are automatically discovered.

---

## Invocation

Skills are namespaced under `brand-manager`:

```
/brand-manager:brand-identity        "AU SaaS for indie hackers; founder is a designer"
/brand-manager:color-palette         "trustworthy fintech, blue + sand, mobile-first"
/brand-manager:design-tokens         "use the Beacon palette from earlier session"
/brand-manager:competitor-analysis   "Pixelforge vs Annapurna, Devolver, Coffee Stain"
/brand-manager:website-copy          "Stillwater meditation app, 5 pages, calm voice"
/brand-manager:legal-disclaimers     "AU e-commerce store selling outdoor gear"
```

If no arguments are passed, each skill begins its Phase 1 by asking the questions it needs to proceed.

---

## How the skills connect

The skills are designed to chain together. A typical end-to-end brand build:

```
brand-identity            → defines voice, values, archetype
        ↓
target-audience           → defines who the brand is for
        ↓
competitor-analysis       → defines what space the brand owns
        ↓
logo-brief + color-palette + design-tokens   → build the visual system
        ↓
brand-guidelines          → consolidates everything into a brand book
        ↓
website-copy              → applies the system to public-facing copy
        ↓
legal-disclaimers         → adds the regulatory layer
```

Each skill's output is markdown-first and can be passed verbatim into the next skill as context.

---

## Skill structure

Every skill in this plugin follows the same layout:

```
skills/<skill-name>/
├── SKILL.md                       # Main interview-driven workflow
├── reference.md                   # Frameworks, lookup tables, formulas (where applicable)
├── LICENSE.txt                    # Apache 2.0
├── templates/
│   └── output-template.md         # Markdown skeleton with {{placeholders}}
├── examples/
│   └── example-output.md          # Realistic completed example
└── scripts/                       # Optional CLI helpers
    └── <utility>.py
```

`SKILL.md` files are kept under 500 lines. Dense reference material lives in `reference.md`.

---

## Conventions

- **Australian English** throughout (colour, organise, optimise, prioritise)
- **DD/MM/YYYY** date format
- **AUD** when currency is mentioned
- **Markdown-first** outputs — every skill produces clean, copy-pasteable markdown

---

## Disclaimer

The `legal-disclaimers` skill produces drafted templates intended as a starting point for legal review. **It is not legal advice.** All legal artefacts produced by this plugin must be reviewed by a qualified solicitor in the relevant jurisdiction before publication or use.

---

## License

MIT — see `.claude-plugin/plugin.json`. Per-skill LICENSE.txt files are Apache 2.0 boilerplate.

---

## Author

[Anthril](https://github.com/anthril) — `john@anthril.com`
