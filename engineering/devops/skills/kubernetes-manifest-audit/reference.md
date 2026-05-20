# Kubernetes Manifest Audit — Reference

## §1 — Audit Taxonomy

### A. Pod security
| ID | Check | CIS |
|---|---|---|
| A.1 | `securityContext.runAsNonRoot: true` | 5.2.6 |
| A.2 | `securityContext.readOnlyRootFilesystem: true` | 5.2.7 |
| A.3 | `securityContext.allowPrivilegeEscalation: false` | 5.2.5 |
| A.4 | `capabilities.drop: ["ALL"]` | 5.2.8 |
| A.5 | No `hostNetwork`, `hostPID`, `hostIPC` | 5.2.1–5.2.4 |
| A.6 | Seccomp profile set (`RuntimeDefault` minimum) | 5.2.9 |
| A.7 | No `privileged: true` | 5.2.1 |
| A.8 | Pod Security Standards label (`pod-security.kubernetes.io/enforce: restricted`) | — |

### B. Resources
| ID | Check |
|---|---|
| B.1 | Every container has `resources.requests.cpu` |
| B.2 | Every container has `resources.requests.memory` |
| B.3 | Every container has `resources.limits.memory` (CPU limit is situational) |
| B.4 | QoS class appropriate (`Guaranteed` for critical pods, `Burstable` for general) |
| B.5 | No container requests >50% node capacity without justification |

### C. Probes
| ID | Check |
|---|---|
| C.1 | `livenessProbe` configured |
| C.2 | `readinessProbe` configured |
| C.3 | `startupProbe` for slow-start apps |
| C.4 | Probe command meaningful (not `exec: ['true']`) |
| C.5 | Thresholds sensible (not `failureThreshold: 1` on liveness for a slow app) |

### D. Image hygiene
| ID | Check |
|---|---|
| D.1 | Image pinned by digest (`@sha256:...`) or at minimum specific tag |
| D.2 | `imagePullPolicy: IfNotPresent` for tag-pinned images in prod (not `Always`) |
| D.3 | `imagePullSecrets` scoped to the ServiceAccount, not cluster-wide |
| D.4 | No `:latest` tags |
| D.5 | Images from trusted registries |

### E. Secrets & config
| ID | Check |
|---|---|
| E.1 | No `kind: Secret` with plaintext `data:` in Git (use SealedSecrets / ExternalSecrets / SOPS / Vault Agent) |
| E.2 | ConfigMaps not used for credentials |
| E.3 | Secrets mounted as files (not env vars) for long-lived workloads where possible |
| E.4 | `automountServiceAccountToken: false` where the workload doesn't call the API |

### F. Networking
| ID | Check |
|---|---|
| F.1 | NetworkPolicy present (default-deny + allow-lists) |
| F.2 | Service `type: LoadBalancer` only when needed (not for internal services) |
| F.3 | Ingress has `tls:` block |
| F.4 | Ingress hosts documented and not wildcard for prod |

### G. RBAC
| ID | Check |
|---|---|
| G.1 | Per-workload ServiceAccount (not `default`) |
| G.2 | Roles have specific `resources` and `verbs` (no `*`) |
| G.3 | ClusterRoles used only when cross-namespace access is genuinely needed |
| G.4 | RoleBindings grant access to specific ServiceAccounts, not groups |

### H. Availability
| ID | Check |
|---|---|
| H.1 | PDB for critical workloads |
| H.2 | `replicas >= 2` in prod |
| H.3 | Topology spread or pod anti-affinity across zones/nodes |
| H.4 | `maxUnavailable` and `maxSurge` on rolling updates |
| H.5 | `progressDeadlineSeconds` set |

### I. Helm hygiene
| ID | Check |
|---|---|
| I.1 | `values.schema.json` present |
| I.2 | `values.yaml` defaults safe (no prod hostnames, no real credentials) |
| I.3 | Every templated field has a default or is validated |
| I.4 | Chart `version` and `appVersion` semver-correct |
| I.5 | `Chart.yaml` metadata complete (`maintainers`, `home`, `sources`) |

---

## §2 — Severity Rubric

| Severity | Examples |
|---|---|
| CRITICAL | `privileged: true`, `hostNetwork: true` on an app workload, plaintext Secret in Git, RBAC with `verbs: ["*"]` on `Secrets` |
| HIGH | No `runAsNonRoot`, missing resource limits on prod, `:latest` tag on prod, no NetworkPolicy in a multi-tenant namespace |
| MEDIUM | Missing liveness/readiness, replicas=1 in prod, ClusterRole with wider scope than needed |
| INFO | Missing topology spread, `values.schema.json` absent |

---

## §3 — Scoring Weights

| Category | Weight |
|---|---|
| A. Pod security | 20 |
| B. Resources | 15 |
| C. Probes | 10 |
| D. Image hygiene | 10 |
| E. Secrets & config | 15 |
| F. Networking | 10 |
| G. RBAC | 10 |
| H. Availability | 5 |
| I. Helm hygiene | 5 |

---

## §4 — CIS / NSA Hardening Guide Alignment

CIS controls directly covered:
- 5.1 RBAC and Service Accounts → G.*
- 5.2 Pod Security Standards → A.*
- 5.3 Network Policies and CNI → F.*
- 5.4 Secrets Management → E.*
- 5.7 General Policies → D.*, H.*

NSA/CISA Kubernetes Hardening Guide cross-refs:
- Pod security → A.1–A.7
- Network separation → F.1
- Authentication & authorisation → G.*
- Log auditing → out of scope for this skill (see `observability-audit`)
