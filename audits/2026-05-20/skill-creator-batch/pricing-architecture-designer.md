# Skill Audit — pricing-architecture-designer

**Date:** 2026-05-20
**Path:** `economics/business-economics/skills/pricing-architecture-designer`
**Files:** SKILL.md (139), reference.md (95), templates/output-template.md (59), examples/example-output.md (71), LICENSE.txt (21)

---

## Score Summary

| Dim | Max | Score |
|-----|-----|-------|
| Discovery (metadata/description) | 20 | 19 |
| Scope (single clear purpose) | 15 | 14 |
| Conciseness (under 500 lines, signal density) | 15 | 15 |
| Architecture (phases, refs, separation) | 15 | 14 |
| Content (depth, evidence, frameworks) | 15 | 14 |
| Tool usage (allowed-tools fit) | 10 | 9 |
| Testing (example realism + coverage) | 7 | 6 |
| Standards (AU English, license, structure) | 3 | 3 |
| Activation (frontmatter, argument-hint) | 10 | 10 |
| Anti-patterns (avoidance) | 5 | 5 |
| **Total** | **115** | **109** |

**Grade: A** (>=104)

---

## Special Checks

### (a) Five pricing-model archetypes covered
PASS. SKILL.md:46-51 lists Tiered, Usage-based, Freemium, Value-based, Outcome-based (plus Hybrid as a 6th). reference.md:7-12 echoes the same matrix with "Best when / Cautions". Description front-loads the five archetypes (SKILL.md:3).

### (b) Fences + anchors design pattern explicit
PASS. SKILL.md:57-66 defines fences/anchors at phase level. reference.md:34-47 enumerates 6 fence types with defensibility criteria. reference.md:50-68 covers Asymmetric Dominance decoy, Centering (~70% middle preference), and Decoy tier patterns with worked numerics.

### (c) AU-context example
PASS. example-output.md:1 titled "AU B2B SaaS (project-management for trades)"; AUD pricing throughout (lines 16-22); AU date format `20/05/2026` (line 3); trades-industry segmentation (sole-trader / crew / operator) is distinctly AU SMB-flavoured.

---

## Dimension Notes

**Discovery (19/20):** Description is 192 chars, front-loaded with archetypes, segment context, and AU framing (SKILL.md:3). Could trim "AU SMB and growth-stage" duplication.

**Scope (14/15):** Single purpose — pricing model selection + packaging. Slight scope-creep into migration + 90-day monitoring + A/B test suggestions, but each phase is tight and the migration content is genuinely part of pricing architecture.

**Conciseness (15/15):** 139 lines, well under 500. Reference material correctly extracted to `reference.md` (SKILL.md:108 references template; reference.md not explicitly cross-linked from body — minor).

**Architecture (14/15):** Six clean phases (SKILL.md:32-96). Output spec at line 106-115. Behavioural rules and edge cases separated (lines 119-138). Missing: explicit pointer to `reference.md` from SKILL.md body — reader has to discover it.

**Content (14/15):** Cites Monetizing Innovation, Van Westendorp PSM, Gabor-Granger (SKILL.md:14). reference.md:16-30 unpacks PSM mechanics. Common Mistakes table (reference.md:74-83) is dense and well-targeted. Could go deeper on Gabor-Granger (named once, not explained).

**Tool usage (9/10):** `Read Write Edit` is correct for a markdown-output skill. No unnecessary Bash/Agent. `[[ab-test-designer]]` cross-ref at SKILL.md:127 is good. Minor: `effort: high` is justified given the analytical depth.

**Testing (6/7):** Example is realistic, end-to-end, with monitoring thresholds and assumptions stated (example-output.md:34-38). Only one example covers SaaS-hybrid; no example of pure usage / freemium / value-based / outcome.

**Standards (3/3):** AU English (organise, behaviour, colour not triggered; "ARR", "AUD" used). MIT LICENSE present. Directory structure matches the project standard.

**Activation (10/10):** Frontmatter has all required fields. `argument-hint: [product-and-segments]` is clear. `effort: high` appropriate. `ultrathink` declared (SKILL.md:10).

**Anti-patterns (5/5):** No emojis. No vague claims. Explicit guidance against tier-sprawl (SKILL.md:66), race-to-bottom (line 134), cost-plus (line 121). Behavioural Rules section makes priors explicit.

---

## Top 3 Fixes (P0)

1. **Cross-link `reference.md` from SKILL.md body.** Currently the dense reference (decoy patterns, PSM mechanics, fence types, migration table) is only discoverable by file-system browsing. Add an explicit "See `reference.md` for fence taxonomy, PSM mechanics, and migration patterns" line near Phase 3 (around SKILL.md:67).

2. **Add a second example for a non-tiered archetype.** Only one example (SaaS hybrid). Add at least one of: usage-based (e.g. an AU marketplace charging per transaction), freemium (AU consumer app), or outcome-based (AU professional services) to demonstrate the decision tree at SKILL.md:46-51 actually routes to different architectures.

3. **Explain Gabor-Granger or drop the citation.** It's named at SKILL.md:14 but never appears in `reference.md`. Either add a 5-line reference block (sequential price-point ascending purchase-intent questioning) or remove the reference to avoid implying coverage that isn't there.

---

## Minor Observations

- Template ARR units inconsistent (output-template.md:28-30 — Conservative shows `${{n}}`, Base/Aggressive show `${{n}}M`).
- Migration table in template (output-template.md:38) hardcodes "Grandfather 12 months" — should be a placeholder.
- Behavioural Rule 5 (SKILL.md:125) says "AU-currency-anchored where relevant" which is slightly weak — could be promoted to "AUD by default for AU products; flag explicitly if multi-currency".
