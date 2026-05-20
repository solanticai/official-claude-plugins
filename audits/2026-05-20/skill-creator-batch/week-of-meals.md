# Skill Audit: week-of-meals

**Path:** `lifestyle/health-wellness/skills/week-of-meals/`
**Date:** 2026-05-20

## Special Checks

- (a) **Disclaimer at top of output template?** YES — template line 11 places disclaimer block before any content. Example matches at line 11.
- (b) **macro-calc.py referenced in allowed-tools?** YES — SKILL.md:5 `Bash(python:scripts/macro-calc.py)`, but `scripts/` directory **does not exist**. Broken reference.
- (c) **AskUserQuestion in allowed-tools given Phase 1 uses it?** NO — Phase 1 header (SKILL.md:54) says "AskUserQuestion — 5 questions" but `allowed-tools` (SKILL.md:5) omits `AskUserQuestion`. Inconsistency.

## Scoring

### Discovery (20)
Description (SKILL.md:3) front-loads key use case, "7-day meal plan with macro targets, prep-day workflow, AUD shopping list" — concrete, scannable, under 250 chars. Trigger list (SKILL.md:21-27) is clear. Argument-hint present (line 4). **Score: 18/20**

### Scope (15)
Single coherent deliverable — weekly meal plan. Edge cases (SKILL.md:166-172) handle pregnancy, EDs, diabetes, GLP-1, budget extremes. Boundary with `smart-supplement-stack` is explicit (line 154). **Score: 14/15**

### Conciseness (15)
SKILL.md 172 lines — well under 500 cap. Dense reference correctly extracted to `reference.md` (118 lines). No bloat. **Score: 15/15**

### Architecture (15)
Five phases (Intake → Macro Calc → Meal Architecture → Weekly Build → Shopping List). Sequential, logical, each phase has clear output. Tool-usage table (lines 127-133) maps cleanly. **Score: 14/15**

### Content (15)
Australian-specific (AUD, Coles/Woolies/ALDI, NHMRC, APD), evidence-based (ISSN, Mifflin–St Jeor, Raubenheimer & Simpson). Behavioural rules (lines 152-162) and edge cases concrete. Reference includes macro tables, swap matrix, prep-day routines. **Score: 14/15**

### Tool (10)
`allowed-tools` (line 5) declares `Bash(python:scripts/macro-calc.py)` but the script **does not exist on disk** — directory missing. Phase 1 (line 54) invokes AskUserQuestion but it's not in allowed-tools. Two real defects. **Score: 5/10**

### Testing (7)
One realistic example (`examples/example-output.md`, 131 lines) with Brisbane recomp scenario, populated tables, AUD costs. Matches template structure. **Score: 6/7**

### Standards (3)
Australian English consistent (colour absent — but "optimise/behaviour" naturally not needed; uses AUD, metric, Coles/Woolies). Frontmatter compliant. LICENSE present. **Score: 3/3**

### Activation (10)
Trigger phrases clear ("meal plan", "macros", "shopping list", AUD budget). `ultrathink` set (line 10) appropriate for complex planning. **Score: 9/10**

### Anti-patterns (5)
No anti-patterns (no recommending supplements per rule 2; refers out for clinical; no aggressive cuts). Disclaimer present. Note however: SKILL.md:28 and :140 reference `commands/health-disclaimer.md` which is **not co-located** — unverified external path. Minor deduction. **Score: 4/5**

## Total: 102/115 — Grade B

## Top 3 Fixes (P0)

1. **Create `scripts/macro-calc.py`** — referenced in allowed-tools at SKILL.md:5 and called in Phase 2 (SKILL.md:68) but the file does not exist. Either add the script implementing Mifflin–St Jeor TDEE or remove the Bash entry from allowed-tools and rewrite Phase 2 to compute inline.
2. **Add `AskUserQuestion` to `allowed-tools`** at SKILL.md:5 — Phase 1 (SKILL.md:54) is titled "Intake (AskUserQuestion — 5 questions)" but the tool is not whitelisted, so the skill cannot execute Phase 1 as written.
3. **Resolve `commands/health-disclaimer.md` reference** — cited verbatim at SKILL.md:28 and SKILL.md:140 but not co-located within the skill. Either inline the disclaimer text in the skill (template already inlines it at line 11), or document the canonical path within the plugin and verify it exists.
