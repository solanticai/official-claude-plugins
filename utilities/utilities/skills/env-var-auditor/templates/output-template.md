# Env Var Audit — {{repo_name}}

**Date:** {{date_dd_mm_yyyy}}

---

## Inventory Summary

- `.env.example` location: `{{path}}`
- Declared vars: {{n}}
- Code references found: {{n}}
- Healthy (declared + used): {{n}}
- Drift (declared, unused): {{n}}
- Missing docs (used, undeclared): {{n}}
- Hidden config (in .env not .env.example): {{n}}
- Security flags: {{n}}

---

## Drift — Declared, Never Used (consider removing)

| Variable | Comment in .env.example | Recommended action |
|----------|------------------------|--------------------|
| {{VAR}} | {{comment}} | Remove from .env.example or verify deploy-only use |

---

## Missing Documentation — Used in code, never declared

| Variable | First found | Recommended action |
|----------|-------------|--------------------|
| {{VAR}} | {{file:line}} | Add to .env.example with example value + comment |

---

## Hidden Config — In .env not in .env.example

| Variable | Recommended action |
|----------|--------------------|
| {{VAR}} | Add to .env.example (without secret value) or document why hidden |

---

## Security Flags

| Variable | Pattern matched | Recommended action |
|----------|----------------|--------------------|
| {{VAR}} | name contains 'SECRET'/'KEY'/'TOKEN' | Add "# DO NOT COMMIT" comment + provisioning doc |

---

## Recommended Actions

1. {{action_1}}
2. {{action_2}}
3. {{action_3}}
