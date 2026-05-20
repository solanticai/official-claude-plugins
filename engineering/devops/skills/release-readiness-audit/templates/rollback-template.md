# Rollback Procedure — {{repo_name}} / {{release_tag}}

**Release:** {{release_tag}}
**Deployed:** {{DD/MM/YYYY HH:mm}}
**Prepared by:** {{author}}

---

## Rollback class

**{{rollback_class}}** *(Trivial / Feature-flag / Config / Data-compatible / Forward-only)*

## When to roll back

Roll back if any of the following hold after deploy:

- Error rate > {{error_threshold}} for > {{error_duration}}
- p95 latency > {{latency_threshold}} for > {{latency_duration}}
- User-reported regression confirmed by oncall

## Prerequisites

- [ ] {{prereq_one}}
- [ ] {{prereq_two}}

## Procedure

1. {{step_one}}
2. {{step_two}}
3. {{step_three}}

## Verification

- [ ] Healthz green
- [ ] Error rate returned to baseline within 5 min
- [ ] {{verification_one}}

## State considerations

{{state_considerations}}

## Contact

- Release author: {{author_contact}}
- Oncall: {{oncall_contact}}
