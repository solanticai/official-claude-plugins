# Skill Audit — forecasting-model-spec

**Path:** `data-science/experimentation/skills/forecasting-model-spec`
**Date:** 2026-05-20
**Rubric:** 8 dims, 115 pts

---

## Scores

| Dim | Pts | Score | Notes |
|---|---|---|---|
| Discovery (metadata/frontmatter) | 20 | 18 | Valid frontmatter (SKILL.md:1-7); name, desc < 250 chars, effort=high, argument-hint, allowed-tools all present. Missing optional `keywords`/`paths`. Description front-loads use case well. |
| Scope | 15 | 14 | Tight scope: spec only, not the model itself (SKILL.md:14). Clear non-goal stated. Covers ARIMA/SARIMA/Prophet/ML + ETS + intermittent + hierarchical. |
| Conciseness | 15 | 14 | SKILL.md = 139 lines, well under 500. No bloat. Could pull edge cases into reference.md but currently fine. |
| Architecture | 15 | 12 | Phases 1-6 sequential and coherent (SKILL.md:34-95). Output template + example present. **No reference.md** despite SKILL.md:59 referring to "`reference.md`-style guidance" — minor inconsistency. |
| Content quality | 15 | 14 | Strong domain content: Hyndman/Athanasopoulos + Taylor/Letham references (SKILL.md:20); MAPE caveats (SKILL.md:124); leakage check (SKILL.md:138); structural breaks (SKILL.md:137). Example is realistic and detailed. |
| Tool usage | 10 | 10 | Read/Write/Edit only — appropriate for a spec-writing skill (SKILL.md:5, 101). |
| Testing/examples | 7 | 7 | One thorough, AU-grounded example (WAU SaaS, 156 weeks, Prophet, 4 walk-forward origins with baselines). |
| Standards (AusE, MIT) | 3 | 3 | LICENSE.txt present; "Australian English; AUD" stated (SKILL.md:24); "colour", "optimise" not triggered but no US spellings detected. |
| **Subtotal** | **100** | **92** | |
| Activation hints | 10 | 8 | `argument-hint: [series-data-and-horizon]` is descriptive. Description triggers on "forecast/ARIMA/Prophet/ML". No `paths` glob. |
| Anti-patterns | 5 | 5 | No code-as-skill smell; no hidden side-effects; stays in spec lane; doesn't bolt on irrelevant tools. |
| **Total** | **115** | **105** | |

**Grade: A (105 / 115)**

---

## Special checks

**(a) Walk-forward backtest + baselines:** PASS. SKILL.md:72-77 mandates walk-forward, ≥3 origins, naive + seasonal-naive baselines. Behavioural rule "Always beat the baseline" (SKILL.md:121). Template enforces baseline columns (template:56-57). Example demonstrates 4 origins with explicit baseline comparisons (example:68-75).

**(b) AU public holidays / seasonality:** PASS. SKILL.md:51 (Phase 2 diagnostic — "AU public holidays — variable by state"), SKILL.md:123 ("AU holidays explicitly handled. Don't forget school holidays + state-level public holidays"), template:29 (AU holiday-effect row), example:39 (state-by-state holiday consolidation NSW+VIC+QLD+WA+SA+TAS+ACT+NT). Excellent AU grounding.

**(c) Model selection decision tree:** PASS. SKILL.md:58-65 provides a concrete decision tree mapping data-size + seasonality + regressor + frequency to ETS / SARIMA / Prophet / GBT / deep state-space. Could be extracted to reference.md for richer per-branch guidance, but the inline tree is usable.

---

## Top 3 Fixes (P0)

1. **Reconcile the `reference.md` reference.** SKILL.md:59 says "in `reference.md`-style guidance" but no reference.md exists. Either (a) create `reference.md` with an expanded decision tree (data-size × seasonality × regressors × frequency matrix, hyperparameter starting points per family, MAPE-vs-sMAPE-vs-MASE selection guide), or (b) reword to "Decision tree (inline):". Option (a) is preferred — it would also off-load the edge-cases section and unlock room for Croston/MASE/MinT reconciliation detail.

2. **Strengthen intermittent-demand and hierarchical branches in the decision tree.** Edge cases (SKILL.md:133-138) mention Croston and MinT, but Phase 3's decision tree (SKILL.md:58-65) does not route to them. A user with intermittent demand following the tree linearly will land on SARIMA/Prophet. Add explicit pre-checks: "intermittent (>30% zeros) → Croston/TSB"; "hierarchical (sub-totals must reconcile) → MinT/bottom-up after base model".

3. **Add MASE as a baseline-relative metric.** Behavioural rule "Always beat the baseline" (SKILL.md:121) is best operationalised by MASE (Mean Absolute Scaled Error), which is exactly the "ratio to naive" metric. Currently only MAPE/sMAPE/RMSE are listed (SKILL.md:75, template:53). Add MASE to the primary metric list and to the template's per-origin table — this makes "beats baseline" a single number rather than two yes/no columns.

---

## Minor

- Template:43 — empty regressor table has no example row to anchor format; example file fills this well but template alone is sparse.
- Phase 5 says "Daily: prediction vs actual" (SKILL.md:84) but example correctly notes "Daily: Not applicable (weekly cadence)" (example:81). Worth tweaking SKILL.md wording to "At cadence frequency:" rather than "Daily:".
- No mention of probabilistic / interval forecasts (prediction intervals, pinball loss, conformal). For a spec deliverable, "horizon + point estimate" alone may under-serve risk-sensitive use cases.
- `allowed-tools` could include `Glob` if the skill is expected to read prior specs from a repo for consistency; minor.

---

## Verdict

Solid A. Strong AU grounding, correct walk-forward discipline, realistic example. The missing `reference.md` is the only structural issue; intermittent/hierarchical routing and MASE adoption would lift this to a top-of-band A.
