# Changelog Entry — v2.8.0

**Generated:** 20/05/2026
**From:** v2.7.0
**To:** HEAD
**Commits:** 47

---

## Generated CHANGELOG Entry (paste at top of CHANGELOG.md)

```markdown
## [2.8.0] - 2026-05-20

### Added

- **New `lifestyle` category** with 4 plugins: `personal-productivity`, `health-wellness`, `personal-finance`, `home-life-logistics` — 18 lifestyle skills covering habits, meal planning, money, travel.
- **New `data-science/experimentation` plugin** — 4 skills for A/B test design, readouts, forecasting, and causal-impact analysis, with a `stats-reviewer` peer-review agent.
- **New `economics/strategic-economics` plugin** — 3 skills for competitive dynamics, elasticity estimation, and moat-strength audit, with a `red-team-strategist` agent.
- 3 new skills in `economics/business-economics`: pricing-architecture-designer, cost-structure-builder, break-even-scenario-modeller.
- 5 new skills in `engineering/database-design`: erd-generator, rls-policy-designer, migration-plan-builder, index-strategy-planner, supabase-schema-bootstrap. Plus `db-reviewer` agent and `db-bootstrap` interactive command.
- 5 new skills in `utilities/utilities`: changelog-generator, pr-description-writer, env-var-auditor, doc-link-validator, repo-snapshot.

### Changed

- `economics/business-economics` bumped v1.0.3 → v1.1.0 (5 skills now).
- `engineering/database-design` bumped v1.2.0 → v1.3.0 (7 skills now, plus hooks/agents/commands).
- `utilities/utilities` bumped v2.0.0 → v2.1.0 (6 skills now).
- Marketplace.json: 6 new plugin entries; 3 version bumps.

### Conventions

All new skills follow the canonical structure (SKILL.md + LICENSE.txt + templates/output-template.md + examples/example-output.md, with reference.md where dense lookup material applies). Australian English throughout; AUD + metric units in lifestyle skills; AU super / Centrelink / ASIC / TGA context where relevant.
```

---

## Classification Summary

| Section | Count |
|---------|-------|
| Added (feat) | 38 |
| Changed (refactor / perf) | 4 |
| Fixed (fix) | 0 |
| Docs (omitted from changelog) | 3 |
| Chore (omitted) | 2 |
| Breaking | 0 |

---

## Unclassified Commits — review manually

| SHA | Subject | Suggested classification |
|-----|---------|--------------------------|
| abc1234 | "update files" | Investigate — likely chore; ask author |
| def5678 | "WIP — kid feedback" | Likely missed before squash; investigate |

---

## Suggested version bump

Based on: 0 breaking, 38 features, 0 fixes
**Recommended:** 2.7.0 → 2.8.0 (minor bump — many features, no breaks)
