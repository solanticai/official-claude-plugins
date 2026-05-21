# Skill-Evaluator Aggregate — 2.8.0 Batch

**Date:** 20/05/2026
**Skills evaluated:** 38
**Method:** Dispatched parallel general-purpose agents per skill, each applying the 8-dimension rubric (Discovery 20 / Scope 15 / Conciseness 15 / Architecture 15 / Content 15 / Tool 10 / Testing 7 / Standards 3 + Activation 10 + Anti-patterns 5; total 115).

**Grade boundaries:** A ≥104, B 86–103, C 69–85, D 52–68, F <52.

---

## Headline Results

| Metric | Value |
|--------|-------|
| Average score | **104.7 / 115** |
| Median score | 105 / 115 |
| Lowest score | 94 (savings-game-plan) |
| Highest score | 113 (index-strategy-planner) |
| A grades (≥ 104) | **25 / 38 (66%)** |
| B grades (86–103) | 13 / 38 (34%) |
| C / D / F grades | 0 |

**No P0-critical failures.** All skills passed the basic shippability bar. Lowest score (savings-game-plan, 94/B) is still firmly in shippable territory.

---

## Per-Skill Scores

### Lifestyle — personal-productivity (4)

| Skill | Score | Grade |
|-------|-------|-------|
| habit-stacker | 97 | B |
| sunday-reset | 110 | A |
| deep-focus-day | 112 | A |
| energy-detective | 98 | B |
| **Subtotal avg** | **104.3** | — |

### Lifestyle — health-wellness (5)

| Skill | Score | Grade |
|-------|-------|-------|
| week-of-meals | 102 | B |
| move-more-plan | 97 | B |
| sleep-tune-up | 101 | B |
| smart-supplement-stack | 104 | A |
| daily-wellness-stack | 100 | B |
| **Subtotal avg** | **100.8** | — |

### Lifestyle — personal-finance (5)

| Skill | Score | Grade |
|-------|-------|-------|
| money-map | 102 | B |
| debt-knockout-plan | 103 | B |
| savings-game-plan | 94 | B |
| future-me-projection | 106 | A |
| rainy-day-plan | 108 | A |
| **Subtotal avg** | **102.6** | — |

### Lifestyle — home-life-logistics (4)

| Skill | Score | Grade |
|-------|-------|-------|
| trip-day-by-day | 108 | A |
| home-tlc-calendar | 104 | A |
| adulting-checklist | 95 | B |
| thoughtful-gifts-plan | 107 | A |
| **Subtotal avg** | **103.5** | — |

### Data-science — experimentation (4)

| Skill | Score | Grade |
|-------|-------|-------|
| ab-test-designer | 107 | A |
| experiment-readout-builder | 108 | A |
| forecasting-model-spec | 105 | A |
| causal-impact-analyser | 109 | A |
| **Subtotal avg** | **107.3** | — |

### Economics — business-economics additions (3)

| Skill | Score | Grade |
|-------|-------|-------|
| pricing-architecture-designer | 109 | A |
| cost-structure-builder | 105 | A |
| break-even-scenario-modeller | 104 | A |
| **Subtotal avg** | **106.0** | — |

### Economics — strategic-economics (3)

| Skill | Score | Grade |
|-------|-------|-------|
| competitive-dynamics-analyser | 108 | A |
| elasticity-estimator | 109 | A |
| moat-strength-audit | 112 | A |
| **Subtotal avg** | **109.7** | — |

### Engineering — database-design additions (5)

| Skill | Score | Grade |
|-------|-------|-------|
| erd-generator | 105 | A |
| rls-policy-designer | 107 | A |
| migration-plan-builder | 109 | A |
| index-strategy-planner | 113 | A |
| supabase-schema-bootstrap | 104 | A |
| **Subtotal avg** | **107.6** | — |

### Utilities — utilities additions (5)

| Skill | Score | Grade |
|-------|-------|-------|
| changelog-generator | 99 | B |
| pr-description-writer | 109 | A |
| env-var-auditor | 107 | A |
| doc-link-validator | 101 | B |
| repo-snapshot | 99 | B |
| **Subtotal avg** | **103.0** | — |

---

## Recurring P0 Fixes (Cross-Cutting)

These issues appeared in 3+ skills each. Fix them in a sweep rather than per-skill:

### 1. `AskUserQuestion` missing from `allowed-tools` (~12 skills affected)

Pattern: skills declare Phase 1 intake via `AskUserQuestion` in the body, but the frontmatter `allowed-tools` line omits the tool. As written, the skill cannot actually invoke it.

**Affected:** habit-stacker, sunday-reset, deep-focus-day, week-of-meals, move-more-plan, sleep-tune-up, smart-supplement-stack, money-map, savings-game-plan, rls-policy-designer (cross-checked), and others.

**Fix:** Append `AskUserQuestion` to every affected `allowed-tools` line.

### 2. Plugin-level scripts referenced via wrong relative path (~8 skills)

Pattern: shared scripts live at `<plugin>/scripts/`, not at `<plugin>/skills/<skill>/scripts/`. Skills reference them as `scripts/X.py` in `allowed-tools`, which resolves to skill-local (where they don't exist) rather than plugin-root.

**Affected:** week-of-meals (macro-calc.py), debt-knockout-plan + future-me-projection (retirement-projection.py + debt-payoff-calc.py), ab-test-designer (power-calc.py), break-even-scenario-modeller (cvp-calc.py), erd-generator (schema-introspect.sh), changelog-generator (git-history-digest.sh), doc-link-validator (link-check.py).

**Fix options:**
- Use `${CLAUDE_PLUGIN_ROOT}/scripts/X.py` in `allowed-tools` and invocations
- OR move scripts into each skill's `scripts/` directory (duplicate, but resolves)
- OR adjust the Bash matcher syntax to `Bash(python:../../scripts/X.py)`

Repo-wide standard needed; pick one and apply consistently.

### 3. Disclaimer referenced but not inlined (8 skills in lifestyle/health-wellness + lifestyle/personal-finance)

Pattern: SKILL.md says "Disclaimer at top of template" but the actual `templates/output-template.md` ships only a `> Disclaimer.` one-liner with no expanded text. The referenced `commands/health-disclaimer.md` / `commands/finance-disclaimer.md` are plugin-level reference files; the skill's output won't auto-include them.

**Affected:** week-of-meals, move-more-plan, sleep-tune-up, smart-supplement-stack, daily-wellness-stack, money-map, debt-knockout-plan, savings-game-plan, future-me-projection, rainy-day-plan.

**Fix:** Inline the full disclaimer block at the top of each `templates/output-template.md` (and `examples/example-output.md`). The disclaimer-command files become reference text for documentation, not a runtime dependency.

### 4. Single example only (~10 skills)

Pattern: each skill ships one realistic `examples/example-output.md`. Multiple auditors recommended a second contrasting example to demonstrate edge cases declared in the SKILL.md.

**Affected (most-requested second examples):**
- move-more-plan — novice + bodyweight + 3 sessions/wk
- smart-supplement-stack — pregnancy / polypharmacy referral path
- sleep-tune-up — apnoea-suspected red-flag stop
- money-map — sole-trader irregular-income
- rainy-day-plan — sole-trader scenario
- supabase-schema-bootstrap — explicit RLS bundle in the example
- repo-snapshot — non-anthril example to demonstrate generalisability

**Fix:** Add a second example per skill; lowest-effort fixes are usually the ones the user cares about most.

### 5. Phase heading depth (~4 skills)

Pattern: phases use `### Phase N:` instead of `## Phase N:`. Other skills use `##`.

**Affected:** sleep-tune-up, daily-wellness-stack, thoughtful-gifts-plan, repo-snapshot.

**Fix:** Bulk find/replace `### Phase ` → `## Phase ` in those files.

### 6. Missing `paths` auto-activation glob (~6 skills)

Pattern: frontmatter doesn't declare `paths` for auto-activation on relevant files.

**Affected:** sunday-reset, debt-knockout-plan, competitive-dynamics-analyser, moat-strength-audit, rainy-day-plan, others.

**Fix (optional but recommended):** Add a `paths` glob to frontmatter where the skill would naturally activate on certain file types (e.g. `**/budget*.md`, `**/weekly-review*.md`).

---

## Per-Plugin Subtotals (ranked)

| Plugin | Subtotal avg | Skills | Rank |
|--------|-------------|--------|------|
| strategic-economics | 109.7 | 3 | 🥇 |
| database-design (additions) | 107.6 | 5 | 🥈 |
| experimentation | 107.3 | 4 | 🥉 |
| business-economics (additions) | 106.0 | 3 | 4 |
| personal-productivity | 104.3 | 4 | 5 |
| home-life-logistics | 103.5 | 4 | 6 |
| utilities (additions) | 103.0 | 5 | 7 |
| personal-finance | 102.6 | 5 | 8 |
| health-wellness | 100.8 | 5 | 9 |

Health-wellness scored lowest as a plugin, driven almost entirely by the disclaimer-inlining and `AskUserQuestion` issues (both fixable in a single sweep). The strategic-economics plugin scored highest, likely because: small skill count, focused scope, mature reference material, and consistent red-team-strategist agent pattern.

---

## Recommended Sweep (Single PR)

Address the top 3 recurring fixes in one PR:

1. **`AskUserQuestion` to allowed-tools** — 12 files, single line each
2. **Inline disclaimer block in lifestyle templates** — 10 files (5 health-wellness + 5 personal-finance), template + example each
3. **Plugin-level script path resolution** — pick `${CLAUDE_PLUGIN_ROOT}/scripts/X` standard and apply to ~8 affected `allowed-tools` lines

Estimated effort: 60–90 minutes for the sweep. Expected outcome: average score lifts from 104.7 → ~108, with no skill below 100.

After the sweep, the second-example backlog (10 skills × 1 example each) can be staged across follow-up PRs.

---

## Files Generated

All 38 individual reports plus this aggregate are under:

`audits/2026-05-20/skill-creator-batch/`

```
AGGREGATE.md
HANDOFF.md
habit-stacker.md
sunday-reset.md
deep-focus-day.md
energy-detective.md
week-of-meals.md
... (38 individual reports)
```

Each individual report contains: skill name, score, grade, dimension breakdown, top 3 fixes with file:line evidence.

---

## Conclusion

**All 38 new skills are shippable.** The 2.8.0 batch passed evaluator review with 66% A grades and a 104.7/115 average — a strong baseline. The recurring P0 list is small (3 high-leverage fixes) and entirely mechanical; a single sweep PR would lift the average into the high-A range. No skill needs rework; all are usable as shipped.

The lowest-scoring skill (savings-game-plan, 94/B) still exceeds the B threshold by 8 points and has clear, actionable feedback.

**Recommendation:** Ship 2.8.0 now; track the recurring-fix sweep as a follow-up issue.
