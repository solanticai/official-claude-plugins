# Skill Audit — ab-test-designer

**Path:** `data-science/experimentation/skills/ab-test-designer/`
**Date:** 2026-05-20
**Rubric:** 8 dims, 115 pts

---

## Special Checks

| Check | Result | Evidence |
|-------|--------|----------|
| (a) Agent tool in allowed-tools for stats-reviewer | PASS | SKILL.md:5 includes `Agent` |
| (b) Bash scoped to python:scripts/power-calc.py | PASS | SKILL.md:5 `Bash(python:scripts/power-calc.py)` — narrow scope |
| (c) SRM + guardrails + decision matrix all required | PASS | SKILL.md:71 (SRM), 67 (≥2 guardrails), 75-86 (decision matrix); reinforced in Behavioural Rules 115-122 |
| (d) ultrathink declared if effort=high | PASS | SKILL.md:6 `effort: high`, line 10 `ultrathink` declared |

**Critical gap:** `scripts/power-calc.py` is referenced (SKILL.md:46, 107) but the `scripts/` directory does not exist. Phase 2 cannot execute as written.

---

## Dimension Scores

### Discovery (20)
- Frontmatter present, `name`/`description`/`argument-hint`/`allowed-tools`/`effort` all set (SKILL.md:1-7)
- Description front-loaded with use case, includes routing detail to stats-reviewer (SKILL.md:3)
- Description length ~200 chars — within 250 limit
- `argument-hint` clear: `[hypothesis-and-context]` (SKILL.md:4)
- **Score: 19/20** (minor: no `paths` for auto-activation on experiment files)

### Scope (15)
- Single coherent purpose: design A/B/n experiments end-to-end (SKILL.md:9-14)
- Clean handoff to stats-reviewer rather than duplicating review logic (SKILL.md:89-93)
- Edge cases bounded (SKILL.md:125-132)
- **Score: 15/15**

### Conciseness (15)
- SKILL.md = 133 lines (well under 500 cap)
- Dense reference correctly extracted to `reference.md` (79 lines: formulas, pitfalls, Bayesian)
- No redundancy between SKILL.md phases and reference
- **Score: 15/15**

### Architecture (15)
- 6-phase structure: Intake → Power → Spec → Decision Matrix → Peer Review → Output (SKILL.md:34-99)
- Template + example + reference + LICENSE all present
- **Missing `scripts/power-calc.py`** despite Bash tool scoped to it (SKILL.md:46, 107) — broken architectural contract
- Agent file exists at `experimentation/agents/stats-reviewer.md` — correctly external
- **Score: 10/15** (-5 for missing script)

### Content (15)
- Statistically literate: SRM, SUTVA, novelty/primacy, Bonferroni/BH, cluster randomisation all named (SKILL.md:127-132; reference.md:53-65)
- Decision matrix covers significant/practical/guardrail breach/inconclusive (SKILL.md:78-86)
- Bayesian alternative covered (reference.md:69-79)
- Example is realistic and high-quality (example-output.md:1-110)
- Australian English ("colour", "randomisation", "optimise") consistent
- **Score: 15/15**

### Tool (10)
- Bash narrowly scoped to one script (SKILL.md:5) — best practice
- Agent tool justified by stats-reviewer routing
- Read/Write/Edit appropriate
- No over-broad Bash permission
- **Score: 10/10**

### Testing (7)
- Example output present (109 lines) and includes stats-reviewer verdict section
- Template aligns 1:1 with example fields
- No A/A test guidance for the skill itself, but the skill recommends A/A pre-launch checks (SKILL.md:71)
- **Score: 6/7**

### Standards (3)
- Australian English throughout
- LICENSE.txt present (MIT, 21 lines)
- Frontmatter conformant to plugin standards
- **Score: 3/3**

### Activation (10)
- `effort: high` + `ultrathink` correctly paired (SKILL.md:6, 10)
- `argument-hint` clear
- No `paths` glob — minor miss (could auto-activate on `*experiment*.md`)
- **Score: 9/10**

### Anti-patterns (5)
- No peeking, no post-hoc decisions, no "we'll stop when significant" — explicitly forbidden (SKILL.md:22-23, 115-122)
- ≥2 guardrails enforced (SKILL.md:116)
- Pre-registration emphasised
- Decision matrix is pre-written
- **Score: 5/5**

---

## Total

| Dim | Score |
|-----|-------|
| Discovery | 19/20 |
| Scope | 15/15 |
| Conciseness | 15/15 |
| Architecture | 10/15 |
| Content | 15/15 |
| Tool | 10/10 |
| Testing | 6/7 |
| Standards | 3/3 |
| Activation | 9/10 |
| Anti-patterns | 5/5 |
| **Total** | **107/115** |

**Grade: A** (≥104)

---

## Top 3 Fixes (P0)

1. **Create `scripts/power-calc.py`** — referenced in SKILL.md:46 and listed in allowed-tools (SKILL.md:5) but the file does not exist. Phase 2 (Power Analysis) cannot run. Should accept baseline/MDE/alpha/power/traffic and emit per-arm n, total, duration, plus 0.5× and 2× sensitivity rows that match the template (output-template.md:45-49).

2. **Add `paths` glob to frontmatter** for auto-activation on experiment briefs (e.g. `paths: ["**/experiments/**/*.md", "**/ab-test-*.md"]`). Currently activation is manual-only despite obvious file-pattern triggers.

3. **Tighten decision-matrix coupling between SKILL.md and template.** SKILL.md:78-86 has 5 rows; template (output-template.md:55-61) has 5 rows but row labels differ slightly ("Significant + practical" vs "Significant + ≥ MDE + no guardrail breach"). Align wording so the example does not silently drift from the spec.

---

## Notes

- Stats-reviewer agent file confirmed at `data-science/experimentation/agents/stats-reviewer.md` — routing target exists.
- Example output (example-output.md) is one of the strongest in this batch — realistic baseline, sensible MDE, complete reviewer section.
- Bash tool scoping (`Bash(python:scripts/power-calc.py)`) is exemplary — should be the template for other skills in the plugin.
