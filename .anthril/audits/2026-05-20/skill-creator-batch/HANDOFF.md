# Skill-Evaluator Batch — 2026-05-20

This batch contains every new skill introduced by the 2.8.0 release. Each skill should be evaluated via `/skillops:skill-evaluator <skill-path>` and the report saved alongside this handoff.

## Recommended Workflow

```bash
# In a fresh Claude Code session for each skill (or batch of 3–5):
/skillops:skill-evaluator <path>

# Save the report under:
# audits/2026-05-20/skill-creator-batch/<skill-name>.md
```

Aggregate after each batch into a score matrix (skill × 8 dimensions × score).

**P0 threshold:** any score < 70 on Architecture, Content, or Standards → must-fix before the skill is considered shippable.

---

## New Skills to Evaluate (32 total)

### `lifestyle/personal-productivity/` (4)

1. `lifestyle/personal-productivity/skills/habit-stacker`
2. `lifestyle/personal-productivity/skills/sunday-reset`
3. `lifestyle/personal-productivity/skills/deep-focus-day`
4. `lifestyle/personal-productivity/skills/energy-detective`

### `lifestyle/health-wellness/` (5)

5. `lifestyle/health-wellness/skills/week-of-meals`
6. `lifestyle/health-wellness/skills/move-more-plan`
7. `lifestyle/health-wellness/skills/sleep-tune-up`
8. `lifestyle/health-wellness/skills/smart-supplement-stack`
9. `lifestyle/health-wellness/skills/daily-wellness-stack`

### `lifestyle/personal-finance/` (5)

10. `lifestyle/personal-finance/skills/money-map`
11. `lifestyle/personal-finance/skills/debt-knockout-plan`
12. `lifestyle/personal-finance/skills/savings-game-plan`
13. `lifestyle/personal-finance/skills/future-me-projection`
14. `lifestyle/personal-finance/skills/rainy-day-plan`

### `lifestyle/home-life-logistics/` (4)

15. `lifestyle/home-life-logistics/skills/trip-day-by-day`
16. `lifestyle/home-life-logistics/skills/home-tlc-calendar`
17. `lifestyle/home-life-logistics/skills/adulting-checklist`
18. `lifestyle/home-life-logistics/skills/thoughtful-gifts-plan`

### `data-science/experimentation/` (4)

19. `data-science/experimentation/skills/ab-test-designer`
20. `data-science/experimentation/skills/experiment-readout-builder`
21. `data-science/experimentation/skills/forecasting-model-spec`
22. `data-science/experimentation/skills/causal-impact-analyser`

### `economics/business-economics/` additions (3)

23. `economics/business-economics/skills/pricing-architecture-designer`
24. `economics/business-economics/skills/cost-structure-builder`
25. `economics/business-economics/skills/break-even-scenario-modeller`

### `economics/strategic-economics/` (3)

26. `economics/strategic-economics/skills/competitive-dynamics-analyser`
27. `economics/strategic-economics/skills/elasticity-estimator`
28. `economics/strategic-economics/skills/moat-strength-audit`

### `engineering/database-design/` additions (5)

29. `engineering/database-design/skills/erd-generator`
30. `engineering/database-design/skills/rls-policy-designer`
31. `engineering/database-design/skills/migration-plan-builder`
32. `engineering/database-design/skills/index-strategy-planner`
33. `engineering/database-design/skills/supabase-schema-bootstrap`

### `utilities/utilities/` additions (5)

34. `utilities/utilities/skills/changelog-generator`
35. `utilities/utilities/skills/pr-description-writer`
36. `utilities/utilities/skills/env-var-auditor`
37. `utilities/utilities/skills/doc-link-validator`
38. `utilities/utilities/skills/repo-snapshot`

---

## Aggregation Template

Once all individual reports are filed, aggregate into `aggregate.md`:

| Skill | Metadata | Scope | Concise­ness | Architecture | Content | Tools | Testing | Standards | Total | P0 fixes |
|-------|----------|-------|--------------|--------------|---------|-------|---------|-----------|-------|---------|
| habit-stacker | | | | | | | | | | |
| sunday-reset | | | | | | | | | | |
| ... | | | | | | | | | | |

---

## Additional sanity checks before evaluator pass

Already verified in this session:

- ☑ `node scripts/check-versions.mjs` exits 0 (all 19 plugins in sync)
- ☑ All new SKILL.md files have valid YAML frontmatter
- ☑ Every new skill has `templates/` + `examples/` directories with content
- ☑ Standard Stop hook (`suggest-related.sh`) present in every new plugin
- ☑ CHANGELOG.md updated under 2.8.0 with the full plugin manifest
- ☑ Marketplace.json registers all 6 new plugins + 3 version bumps

Manual checks to run before dispatching the evaluator batch:

- ☐ `grep -RIn "color\|optimize\|behavior" lifestyle/` returns empty (AU spelling)
- ☐ No emoji in any new file: `python -c "import re,glob; [print(f) for f in glob.glob('**/SKILL.md',recursive=True) if re.search(r'[\\U0001F300-\\U0001F9FF]', open(f,encoding='utf-8').read())]"`
- ☐ Every SKILL.md is under 500 lines: `find . -name "SKILL.md" -newer audits/2026-05-20 -exec wc -l {} \; | sort -rn | head -10`
- ☐ All `LICENSE.txt` files match the MIT canonical text

---

## Sequencing the Evaluator Runs

The evaluator is heavy (each run takes ~3–8 minutes of LLM time). Recommended sequencing:

- **Batch 1 (4 skills):** personal-productivity — these establish the lifestyle baseline
- **Batch 2 (5 skills):** health-wellness — disclaimer pattern is novel; high evaluator priority
- **Batch 3 (5 skills):** personal-finance — disclaimer + agent pattern; high evaluator priority
- **Batch 4 (4 skills):** home-life-logistics
- **Batch 5 (4 skills):** experimentation — agent pattern; check stats-reviewer interaction
- **Batch 6 (6 skills):** economics — both business-economics additions and strategic-economics
- **Batch 7 (5 skills):** database-design additions
- **Batch 8 (5 skills):** utilities additions

After each batch:

1. Aggregate the 4–6 scores into a running table
2. Spot-check Australian-English + emoji absence in any skill scoring < 80 on Standards
3. Fix any P0 issues before moving to the next batch
4. Re-run `node scripts/check-versions.mjs` after any plugin.json edit

## Bulk-mode (optional, after operator review)

If trust is established after Batch 1, the operator can use the Agent tool with `subagent_type: claude` to run the evaluator on multiple skills in parallel (3–4 at once). This trades depth of human review for throughput.

```
Agent batch:
  - Evaluate habit-stacker; save report to audits/2026-05-20/skill-creator-batch/habit-stacker.md
  - Evaluate sunday-reset; save report to audits/2026-05-20/skill-creator-batch/sunday-reset.md
  - Evaluate deep-focus-day; save report to audits/2026-05-20/skill-creator-batch/deep-focus-day.md
  - Evaluate energy-detective; save report to audits/2026-05-20/skill-creator-batch/energy-detective.md
```

Each spawned agent loads only the target skill's directory and runs the evaluator; parent context stays clean.
