# Future Me Projection — {{user_name_or_alias}}

> **Important — read first.** The information produced by this skill is **general financial information only** — not personal financial product advice as defined by the *Corporations Act 2001* (Cth). It does not take your personal objectives, circumstances, or needs into account.
>
> Before acting on anything produced here, please consult a financial adviser who is licensed by ASIC (Australian Financial Services Licence / AFSL) and an authorised representative. For tax-specific decisions, consult a registered tax agent. For Centrelink, superannuation, or estate planning, also consult a specialist as relevant.
>
> Assumptions used in projections — including investment returns, inflation, tax rates, and superannuation contribution caps — are based on publicly available information and reasonable defaults. They are illustrative, not predictive.

---

## Inputs Snapshot

| Field | Value |
|-------|-------|
| Current age | {{age}} |
| Target retirement age | {{retire}} |
| Current super balance | ${{super}} |
| Current outside-super balance | ${{outside}} |
| Salary | ${{salary}} |
| Total contribution rate | {{n}}% |
| Risk tolerance / asset allocation | {{type}} |

---

## Three Scenarios at Retirement

| Scenario | Return | Contribution | Real balance | Nominal balance | First-year drawdown (real) | Sustainability over 25y |
|---------|--------|-------------|--------------|----------------|--------------------------|------------------------|
| Conservative | 5% | current | ${{n}} | ${{n}} | ${{n}} | {{sustained/depleted_at_age}} |
| Base | 7% | current | ${{n}} | ${{n}} | ${{n}} | {{sustained/depleted_at_age}} |
| Optimistic | 8.5% | +20% | ${{n}} | ${{n}} | ${{n}} | {{sustained/depleted_at_age}} |

---

## Sensitivity Tables

### Return × Contribution (base age, real balance at retirement)

| Return \ Contribution | Current | +10% | +25% |
|----------------------|---------|------|------|
| 5% | | | |
| 7% | | | |
| 8.5% | | | |

### Retirement Age (base scenario, real balance)

| Retire at | 60 | 65 | 67 |
|----------|----|----|----|
| Real balance | | | |

### Drawdown Rate Sustainability

| Rate | Result over 25y |
|------|----------------|
| 3% | |
| 4% | |
| 5% | |

---

## Sequence-of-Returns Analysis

Stress scenario: first 5 years of drawdown deliver −10%, 0%, 0%, 5%, 5%.

| Outcome | Base | Stressed |
|---------|------|----------|
| Real balance at year 10 | | |
| Depleted by age | | |

**Mitigations:**

- Pre-drawdown cash buffer (2–3 yr expenses outside super)
- Glide path: shift toward lower equity in final 5 years before retirement
- Variable spending rule: accept lower withdrawals in down years

---

## Analyst Notes — Things Worth Knowing

_[Inserted by projection-analyst agent]_

---

## Suggested questions for a licensed adviser

- Am I on track for my target retirement age + lifestyle?
- Is my asset allocation right given my time to retirement?
- Should I be using max concessional contributions this FY?
- What's my pre-drawdown buffer plan?
- How should my asset allocation glide as I approach retirement?

---

## Review Date

**Annual:** {{date_dd_mm_yyyy}} — re-run projection at FY end with new balances + salary + assumptions.
