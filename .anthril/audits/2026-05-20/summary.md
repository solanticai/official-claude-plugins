# Skill Audit — 2026-05-20

Mechanical anti-pattern sweep across every skill in the marketplace using the upgraded `skill-evaluator` (dimensions 9 & 10 — activation/behavioural quality and anti-patterns, checks C36–C45).

## Coverage

- **Skills audited:** 65
- **Check runner:** `utilities/skillops/skills/skill-evaluator/scripts/check-antipatterns.sh`
- **Detectors fired:** C41 (option overload), C42 (script error handling), C43 (hook schema), C44 (skills architecture), C45 (allowed-tools minimality)

## Initial sweep — 21 warn findings

| Check | Count | Description |
|---|---:|---|
| C44 | 1 | `utilities/plan-completion-audit/plan-completion-audit` — SKILL.md > 350 lines without `reference.md`. |
| C45 | 20 | Unused `Agent`, `WebFetch`, or `WebSearch` tokens declared in `allowed-tools` across 17 skills. |

Zero `fail`-severity findings on the initial sweep. The skill-evaluator script itself runs clean (self-evaluation passes).

## Remediation

### C45 — `allowed-tools` minimality

Stripped unused tool tokens from 17 SKILL.md files. The C45 detector was refined to exempt skills launched via the `agent:` or `context: fork` frontmatter (which legitimately need `Agent` in `allowed-tools` even when the body does not reference it by name).

| Plugin | Skills touched | Tokens removed |
|---|---|---|
| `smb/brand-manager` | competitor-analysis | WebSearch |
| `engineering/devops` | devops-needs-assessment, observability-audit, release-readiness-audit, sre-reliability-audit | Agent |
| `engineering/package-manager` | cli-ux-audit, npm-package-audit | Agent |
| `data-science/data-analysis` | cohort-analysis-builder, data-dictionary-generator, dataset-profiling-quality-audit | Agent |
| `data-science/knowledge-engineering` | business-data-model-designer, entity-disambiguation, entity-relationship-mapper, knowledge-graph-builder | Agent |
| `economics/business-economics` | market-sizing-tam-estimator, unit-economics-calculator | WebSearch, WebFetch, Agent |
| `utilities/plan-completion-audit` | plan-completion-audit | WebSearch, WebFetch, Agent |

### C44 — Skills-architecture compliance

`utilities/plan-completion-audit/skills/plan-completion-audit/SKILL.md` was 361 lines (over the 350-line "extract dense material into reference.md" threshold). Phase 10 (Supabase Backend Audit) and Phase 11 (Frontend ↔ Backend Alignment) were slimmed to summary pointers; the full per-sub-phase checklists already exist in `references/supabase-audit-guide.md`. A new `reference.md` index at the skill root points at `references/`. SKILL.md is now 317 lines.

## Final sweep — 0 findings

```
By ID: {} Total: 0
```

Every audited skill passes the deterministic anti-pattern catalogue.

## Plugin version bumps

Patch releases for affected plugins:

| Plugin | Was | Now |
|---|---|---|
| brand-manager | 1.0.1 | 1.0.2 |
| devops | 1.0.1 | 1.0.2 |
| package-manager | 1.1.1 | 1.1.2 |
| data-analysis | 1.0.2 | 1.0.3 |
| knowledge-engineering | 1.0.2 | 1.0.3 |
| business-economics | 1.0.2 | 1.0.3 |
| plan-completion-audit | 1.0.2 | 1.0.3 |
| skillops | 1.1.1 | 1.2.0 (rubric extension, separate commit) |

## Exceptions

None — every finding from the initial sweep was remediated.

## Notes on coverage

This sweep covers the deterministic Dimension 9 / Dimension 10 checks only. The qualitative review layer (Phase 4 of the full evaluator, which invokes a sub-agent for judgement calls on phase sequencing, terminology drift, etc.) was not run across all 65 skills due to cost. To extend coverage, invoke the full evaluator per skill:

```bash
# Single skill, full mode (with qualitative review)
/skill-evaluator <category>/<plugin>/skills/<skill>

# Fast mode (deterministic only, score capped at 85/115)
/skill-evaluator <category>/<plugin>/skills/<skill> --fast
```
