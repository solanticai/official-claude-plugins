# Repo Snapshot — official-claude-plugins

**Date:** 20/05/2026
**Audience:** new-hire (engineering)

---

## At a Glance

| Aspect | Value |
|--------|-------|
| Primary language | Markdown (skill definitions) + Bash + Python + JavaScript (build helpers) |
| Framework | Claude Code plugin SDK (skills + hooks + commands + agents) |
| Build tool | Node + pnpm (for `check-versions.mjs`); Python (for skill scripts) |
| Test framework | Internal `skill-evaluator` (LLM-as-judge); no traditional unit tests |
| Database | None (file-based plugin marketplace) |
| Deployment | GitHub repo + Claude Code marketplace catalog |
| CI | None visible in repo (pre-commit hook for changelog enforcement) |
| Total LOC (markdown + scripts) | ~85k (incl. all skill SKILL.md, references, examples) |
| Top-level folders | 8 (one per plugin category) |
| Last commit | 20/05/2026 (today) |

---

## Folder Tree (curated)

```
official-claude-plugins/
├── .claude/                # Project-level Claude config + CLAUDE.md instructions
├── .claude-plugin/         # marketplace.json + global plugin config
├── .github/                # GitHub Actions, issue templates (sparse)
├── audits/                 # Quarterly LLM-as-judge audit results
├── data-science/           # Plugins: data-analysis, knowledge-engineering, experimentation
├── economics/              # Plugins: business-economics, strategic-economics
├── engineering/            # Plugins: database-design, devops, package-manager, software-development
├── lifestyle/              # NEW: personal-productivity, health-wellness, personal-finance, home-life-logistics
├── marketing/              # Plugins: ppc-manager
├── scripts/                # check-versions.mjs (version-parity validator) + helpers
├── seo/                    # Plugins: seo-toolkit (20 skills)
├── smb/                    # Plugins: business-operations, brand-manager
├── utilities/              # Plugins: utilities (general-purpose), resource-manager, skill-ops
├── CHANGELOG.md            # Keep a Changelog format; recently updated 2.8.0
├── README.md               # Marketplace overview
└── SECURITY.md             # Per-plugin security summary
```

Top-level files of note:

- `CHANGELOG.md` — read this for recent additions
- `.claude/CLAUDE.md` — project instructions Claude Code reads on every session
- `.claude-plugin/marketplace.json` — single source of truth for plugin registration
- `scripts/check-versions.mjs` — run before any version bump

---

## Top Files by LOC

| File | LOC | Worth attention? |
|------|-----|-----------------|
| `audits/2026-05-20/judge/fleet-judge.md` | ~3,200 | Yes — most recent fleet-wide audit; calibrated rubric |
| `data-science/experimentation/skills/causal-impact-analyser/reference.md` | ~280 | Yes — example of dense reference.md pattern |
| `economics/strategic-economics/skills/moat-strength-audit/reference.md` | ~260 | Yes — same pattern; 7 Powers detailed criteria |
| `seo/seo-toolkit/skills/serp-analysis/SKILL.md` | ~480 | Heavy skill near the 500-line cap |
| `lifestyle/personal-productivity/skills/habit-stacker/SKILL.md` | ~240 | Recent; good reference |
| `engineering/database-design/skills/supabase-schema-bootstrap/examples/example-output.md` | ~290 | Heavy example; usable as template |
| ... 14 more | | |

---

## Dependency Surface

- **Runtime deps (Node):** none — pure markdown + bash + python skills
- **Build tool deps:** Node + pnpm for `check-versions.mjs` (a single ~120-line script)
- **Python scripts:** stdlib only across all skill scripts (no requirements.txt)
- **Notable libs:** N/A (this is a content repo, not an application)
- **Risk flags:** none

---

## Contributor + Cadence

- **Top contributor (last 6 mo):** johnoconnor0 (founder)
- **Commits per month (last 3 mo avg):** ~60–80
- **Activity status:** very active

---

## Onboarding Recommendations

For audience = new-hire (engineering), read in order:

1. `.claude/CLAUDE.md` — project conventions (Australian English, no emoji, 500-line cap, etc.); read first
2. `CHANGELOG.md` v2.8.0 entry — understand most recent additions + scope of plugin
3. `smb/business-operations/skills/revenue-channel-mapper/SKILL.md` — canonical reference plugin to imitate
4. `utilities/skill-ops/skills/skill-creator/SKILL.md` — meta-skill that creates new skills
5. `scripts/check-versions.mjs` — what runs before every release

---

## Risks Surfaced

1. **Single-contributor risk** — one developer, ~60–80 commits/month. Bus-factor of 1. Mitigation: documented conventions in CLAUDE.md make handoff plausible.
2. **No CI** — the changelog-enforcement hook is a clever stand-in but only enforced locally on the author's machine. Anyone could PR with a stale CHANGELOG and the hook won't catch it.
3. **Heavy reliance on conventions** — skill structure is enforced by convention + suggest-related.sh, not by lint. A new contributor could ship a non-conforming skill without realising. Mitigation: `/skillops:skill-evaluator` exists for post-hoc audit.
4. **CHANGELOG.md is large** — 200+ lines, will need pagination strategy at some point.
5. **No SBOM / dep manifest** — for a content repo this is fine, but skills with Python scripts (e.g. macro-calc.py) have no `requirements.txt` (intentional — stdlib only; needs explicit comment for future contributors).
