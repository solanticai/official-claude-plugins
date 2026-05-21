# Codebase Profile — {{profile_id}}

| Field | Value |
|---|---|
| Generated | {{generated_at}} |
| Profiler version | {{profiler_version}} |
| Target | {{target}} |
| Profile depth | {{profile_depth}} |
| Overall health | {{health_tier_emoji}} **{{health_tier}}** |

---

## 1. Stack Identity

| Dimension | Value |
|---|---|
| Primary language | {{primary_language}} |
| Framework | {{framework}} {{framework_version}} |
| Runtime | {{runtime_version}} |
| Package manager | {{package_manager}} |
| TypeScript strict mode | {{typescript_strict}} |
| Monorepo | {{monorepo}} |

---

## 2. Codebase Metrics

| Metric | Value |
|---|---|
| Total files | {{total_files}} |
| Source files | {{source_files}} |
| SLOC (approx.) | {{sloc}} |

### Language Breakdown

{{language_breakdown_table}}

### Largest Files

{{largest_files_table}}

---

## 3. Dependency Graph

| Metric | Value |
|---|---|
| Direct dependencies | {{dep_direct}} |
| Dev dependencies | {{dep_dev}} |
| Transitive (estimated) | {{dep_transitive}} |
| Lockfile present | {{lockfile_present}} |
| Outdated | {{dep_outdated}} |
| Circular import chains | {{dep_circular}} |

### Vulnerability Summary

{{vulnerability_table}}

### Licence Breakdown

{{licence_table}}

### Outdated Dependencies (top 10)

{{outdated_deps_table}}

---

## 4. Architecture Topology

| Dimension | Value |
|---|---|
| Client/server model | {{client_server_model}} |
| API routes | {{api_routes_count}} |
| Data layer | {{data_layer}} |
| Entry points | {{entry_points_count}} |

### Entry Points

{{entry_points_list}}

### External Services Detected

{{external_services_list}}

### Topology Diagram

See [.anthril/codebase-topology.md](.anthril/codebase-topology.md)

---

## 5. Code Quality Signals

### Type Safety

| Signal | Value |
|---|---|
| Language | {{type_language}} |
| Typed | {{typed_language}} |
| Strict mode | {{ts_strict}} |
| `any` usage | {{any_count}} occurrences |
| `@ts-ignore` | {{ts_ignore_count}} occurrences |
| `@ts-nocheck` files | {{ts_nocheck_files}} |
| Type coverage | {{type_coverage_pct}} |

### Linting

| Signal | Value |
|---|---|
| Config files found | {{lint_configs}} |
| Disable comments | {{lint_disable_count}} |
| ESLint errors | {{eslint_errors}} |
| ESLint warnings | {{eslint_warnings}} |
| Linting enforced in CI | {{lint_in_ci}} |

### Complexity

| Signal | Value |
|---|---|
| Files over threshold | {{large_files_count}} |
| TODO / FIXME count | {{todo_count}} |
| TODO density | {{todo_density}} per 500 SLOC |
| Duplication tooling | {{duplication_config}} |

### Top TODO / FIXME Locations

{{top_todos_list}}

### Test Posture

| Signal | Value |
|---|---|
| Test framework | {{test_framework}} |
| E2E framework | {{e2e_framework}} |
| Test files | {{test_file_count}} |
| Source files | {{source_file_count}} |
| Test-to-source ratio | {{test_to_source_ratio}} |
| Coverage report found | {{coverage_report_found}} |
| Coverage % | {{coverage_pct}} |

---

## 6. Security Surface

### Secrets Detection

{{secrets_table}}

### Environment Variable Management

| Signal | Value |
|---|---|
| `.env` files found | {{env_files_count}} |
| All in `.gitignore` | {{env_in_gitignore}} |
| Secrets manager detected | {{secrets_manager}} |
| `.env.example` present | {{env_example}} |

### Auth Pattern

| Signal | Value |
|---|---|
| Auth library | {{auth_library}} |
| Auth model | {{auth_model}} |

---

## 7. Infrastructure & Observability

### Hosting

| Signal | Value |
|---|---|
| Provider | {{hosting_provider}} |
| Config file | {{hosting_config_file}} |
| Containerised | {{containerised}} |
| IaC tooling | {{iac_tools}} |

### CI/CD

| Provider | Workflow count |
|---|---|
{{ci_cd_table}}

### CI/CD Security Posture

{{cicd_security_table}}

### Observability

| Dimension | Tool |
|---|---|
| Error tracking | {{error_tracking}} |
| Structured logging | {{logging_library}} |
| APM / tracing | {{apm_tracing}} |

---

## 8. Health Dashboard

| Dimension | Signal summary | Status |
|---|---|---|
| Dependency health | {{dep_health_signal}} | {{dep_health_status}} |
| Test coverage | {{test_signal}} | {{test_status}} |
| Type safety | {{type_signal}} | {{type_status}} |
| Code complexity | {{complexity_signal}} | {{complexity_status}} |
| Security surface | {{security_signal}} | {{security_status}} |
| Infrastructure maturity | {{infra_signal}} | {{infra_status}} |
| Observability | {{observability_signal}} | {{observability_status}} |
| Developer experience | {{dx_signal}} | {{dx_status}} |

---

## 9. Recommended Focus Areas

{{focus_areas_list}}

---

## 10. Profile Metadata

| Item | Path |
|---|---|
| This document | `.anthril/codebase-profile.md` |
| JSON sidecar | `.anthril/codebase-profile.json` |
| Topology diagram | `.anthril/codebase-topology.md` |
| Agent reports | `.anthril/profile-run/{{profile_id}}/` |
| Dependency analysis | `.anthril/profile-run/{{profile_id}}/dependency-analyst.md` |
| Architecture map | `.anthril/profile-run/{{profile_id}}/architecture-mapper.md` |
| Quality profile | `.anthril/profile-run/{{profile_id}}/quality-profiler.md` |
| Security scan | `.anthril/profile-run/{{profile_id}}/infra-security-scanner.md` |
