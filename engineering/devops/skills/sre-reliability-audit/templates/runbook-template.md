# Runbook — {{alert_name}}

**Last updated:** {{DD/MM/YYYY}}
**Author / owner:** {{author}}
**Linked alert rule:** {{alert_rule_ref}}
**Severity:** {{severity}} *(page / non-page)*

---

## What the user sees

{{user_symptom}}

## First step

**Run this command:**

```
{{first_command}}
```

Expected output: {{expected_output}}

## Decision tree

- If {{condition_one}} → go to **Mitigation A**
- If {{condition_two}} → go to **Mitigation B**
- Otherwise → **Escalate**

## Mitigation A — {{mit_a_name}}

1. {{mit_a_step_1}}
2. {{mit_a_step_2}}

**Verify:** {{mit_a_verify}}
**Rollback:** {{mit_a_rollback}}

## Mitigation B — {{mit_b_name}}

1. {{mit_b_step_1}}
2. {{mit_b_step_2}}

**Verify:** {{mit_b_verify}}
**Rollback:** {{mit_b_rollback}}

## Escalation

- Primary oncall: {{primary}}
- Secondary: {{secondary}}
- Service owner: {{owner}}

## Related

- Postmortem for similar incidents: {{related_postmortems}}
- Upstream dependencies: {{upstream}}

## History

- {{DD/MM/YYYY}} — {{change_note}}
