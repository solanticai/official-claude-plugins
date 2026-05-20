## Summary

Add `lifestyle` plugin category with 4 plugins (personal-productivity, health-wellness, personal-finance, home-life-logistics) — 18 lifestyle skills total.

## Why

Lifestyle was the only empty category in the official-claude-plugins marketplace. Users requested coverage for habits, meal planning, personal finance, and life-admin workflows. Closes #142.

## What Changed

- New plugin `lifestyle/personal-productivity` — 4 skills + interactive onboard command
- New plugin `lifestyle/health-wellness` — 5 skills + health-disclaimer command + macro-calc.py helper
- New plugin `lifestyle/personal-finance` — 5 skills + finance-disclaimer + projection-analyst agent + 2 helper scripts
- New plugin `lifestyle/home-life-logistics` — 4 skills (trip / home / adulting / gifts)
- `.claude-plugin/marketplace.json` — 4 new entries under `lifestyle` category
- `CHANGELOG.md` — entry under 2.8.0
- Each plugin includes standard Stop hook + suggest-related.sh + LICENSE + README

## Risk

**Level:** Low

Specific risks:
- All new plugins; no changes to existing functionality
- Disclaimer pattern in finance + health plugins is new — verify it renders properly before tagging release
- Marketplace.json schema validation must pass via `scripts/check-versions.mjs`

## Test Plan

- [ ] Run `node scripts/check-versions.mjs` — exits 0
- [ ] Test `claude --plugin-dir .` with `/personal-productivity:habit-stacker` against an example prompt — produces output matching template
- [ ] Test `/health-wellness:week-of-meals` produces a plan with disclaimer at top
- [ ] Verify Stop hook fires in each new plugin (sibling-skill suggestion appears)
- [ ] No emoji in any new file (`grep -P '[\x{1F300}-\x{1F9FF}]' lifestyle/**/*.md` returns empty)
- [ ] Australian English spot-check: `grep -i "\bcolor\|\boptimize\|\bbehavior" lifestyle/**/*.md` returns empty
- [ ] Edge case: skill-evaluator runs against each new skill without errors

## Screenshots

N/A — plugin marketplace entries only; no UI changes.

## Checklist

- [x] All new files follow canonical skill structure (SKILL.md + LICENSE + template + example)
- [x] CHANGELOG.md updated under 2.8.0
- [x] Marketplace.json updated with 4 new entries
- [x] No emoji used (Anthril convention)
- [x] Australian English throughout
- [ ] Reviewers tagged
- [ ] Linked issue: #142
