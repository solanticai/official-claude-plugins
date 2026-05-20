# Campaign Audit — {{account_name}}

**Account:** {{account_id}} ({{platform}})
**Period:** {{start_date}} to {{end_date}} ({{days}} days)
**Total spend:** ${{total_spend_aud}} AUD
**Conversions:** {{total_conversions}}
**Overall health score:** {{health_score}}/100
**Date:** {{DD_MM_YYYY}}

---

## Executive summary

{{one_paragraph_summary}}

---

## Blockers (fix immediately)

| # | Finding | Data point | $ impact / month | Effort | Remediation |
|---|---|---|---|---|---|
{{#blockers}}
| {{n}} | {{finding}} | {{data_point}} | ${{impact}} | {{effort}} | {{remediation}} |
{{/blockers}}

---

## Tuning (next optimisation cycle)

| # | Finding | Data point | $ impact / month | Effort | Remediation |
|---|---|---|---|---|---|
{{#tuning}}
| {{n}} | {{finding}} | {{data_point}} | ${{impact}} | {{effort}} | {{remediation}} |
{{/tuning}}

---

## Experiments (to test next)

| # | Hypothesis | Rationale | Test design |
|---|---|---|---|
{{#experiments}}
| {{n}} | {{hypothesis}} | {{rationale}} | {{test_design}} |
{{/experiments}}

---

## Cross-platform reconciliation

| Source | Purchases | Value (AUD) | Variance |
|---|---|---|---|
| GA4 | {{ga4_purchases}} | ${{ga4_value}} | baseline |
| Google Ads | {{gads_purchases}} | ${{gads_value}} | {{gads_variance}}% |
| Meta | {{meta_purchases}} | ${{meta_value}} | {{meta_variance}}% |

---

## Health scores by area

| Area | Score | Severity |
|---|---|---|
{{#area_scores}}
| {{area}} | {{score}}/100 | {{severity}} |
{{/area_scores}}

---

## Remediation playbook

### Immediate (this week)

1. {{immediate_1}}
2. {{immediate_2}}
3. {{immediate_3}}

### Next (next 2 weeks)

1. {{next_1}}
2. {{next_2}}

### Backlog

1. {{backlog_1}}
2. {{backlog_2}}

---

## Next steps

1. Action the top 3 blockers. Each links to a specific fix skill.
2. Re-run `/ppc-manager:campaign-audit` in 14 days to measure progress.
3. If the account passes this audit (health ≥80), schedule a monthly re-run.
