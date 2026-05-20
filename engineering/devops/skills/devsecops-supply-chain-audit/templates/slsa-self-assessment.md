# SLSA Self-Assessment — {{repo_name}}

**Assessed:** {{DD/MM/YYYY}}
**Current level:** L{{slsa_level}}

---

## L1 — Documentation

| Requirement | Status | Evidence |
|---|---|---|
| Build process documented | {{l1_a}} | {{l1_a_evidence}} |
| Provenance generated | {{l1_b}} | {{l1_b_evidence}} |

## L2 — Hosted build + authenticated publish

| Requirement | Status | Evidence |
|---|---|---|
| Hosted build service (GH Actions / GitLab CI / CircleCI) | {{l2_a}} | {{l2_a_evidence}} |
| Authenticated publish | {{l2_b}} | {{l2_b_evidence}} |
| Provenance signed | {{l2_c}} | {{l2_c_evidence}} |

## L3 — Hardened build

| Requirement | Status | Evidence |
|---|---|---|
| Ephemeral runners | {{l3_a}} | {{l3_a_evidence}} |
| Tamper-evident provenance | {{l3_b}} | {{l3_b_evidence}} |
| Isolated build environment | {{l3_c}} | {{l3_c_evidence}} |

## L4 — Two-party review + reproducible

| Requirement | Status | Evidence |
|---|---|---|
| Two-party review for every build-affecting change | {{l4_a}} | {{l4_a_evidence}} |
| Reproducible builds | {{l4_b}} | {{l4_b_evidence}} |
| Hermetic build | {{l4_c}} | {{l4_c_evidence}} |

---

## Gap analysis

{{gap_analysis}}

---

## Roadmap

| Level | Estimated effort | Blockers |
|---|---|---|
| L{{current}} → L{{current_plus_1}} | {{effort_next}} | {{blockers_next}} |
