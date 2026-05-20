# DevOps — Anthril Plugin

Nine skills that audit, remediate, and test DevOps and SRE posture. Each skill supports three operating modes: **static-file audit** (default, no tools required), **live-access audit** (uses `kubectl`, `terraform`, `aws`, `gcloud`, `docker` when available), and **apply mode** (opt-in `--apply` flag, per-change confirmation). Runtime testing — load tests, chaos experiments, synthetic alert firing — is supported per skill with blast-radius guardrails.

---

## Skills

| # | Skill | Purpose |
|---|---|---|
| 1 | `devops-needs-assessment` | Plain-language triage for non-experts — does this application need DevOps work, and if so, what first? |
| 2 | `cicd-pipeline-audit` | Audits CI/CD configs (GitHub Actions, GitLab CI, CircleCI, Azure Pipelines, Jenkins) for security, reliability, reproducibility, supply chain. Sub-agent per workflow file. Apply mode edits YAML; live mode calls `gh` to trigger test runs. |
| 3 | `iac-terraform-audit` | Audits Terraform/OpenTofu modules — state, provider pinning, security (Checkov/tfsec taxonomy), module hygiene, environment separation, drift. Sub-agent per module. Live mode runs `terraform plan`. Apply mode writes patches. |
| 4 | `container-audit` | Audits Dockerfiles and docker-compose — base image, user privileges, secret leaks, layer efficiency, signals, healthchecks. Sub-agent per Dockerfile. Live mode runs `docker inspect` and Trivy/Grype scans. Apply mode writes patches. |
| 5 | `kubernetes-manifest-audit` | Audits manifests and Helm charts against CIS K8s Benchmark and NSA/CISA hardening. Sub-agent per chart/group. Live mode runs `kubectl get`, `kube-bench`, `kube-hunter`. Apply mode writes patches or `kubectl patch`. |
| 6 | `observability-audit` | Scores the four pillars (logs, metrics, traces, alerts/dashboards) with per-service coverage heatmap. Live mode queries Prometheus/Grafana/OTel endpoints. Runtime mode fires a synthetic alert end-to-end. |
| 7 | `release-readiness-audit` | Pre-production go/no-go gate — migration safety, rollback, feature flags, runbooks, monitoring, deploy strategy. Live mode compares staging vs prod. Runtime mode runs a canary smoke test. |
| 8 | `devsecops-supply-chain-audit` | Supply-chain posture across every ecosystem detected (npm, pip, Go, Ruby, Docker, Terraform) — dependency pinning, SBOM, signing, branch protection, SLSA. Sub-agent per ecosystem. Live mode runs `npm audit`, `pip-audit`, `govulncheck`, `trivy`. Apply mode opens PRs for pinning fixes. |
| 9 | `sre-reliability-audit` | Reliability maturity — SLOs/SLIs, runbooks, on-call, postmortems, game days. Runtime mode runs a scoped game-day exercise against a non-prod environment. |

---

## Operating modes

Every skill declares which modes it supports. The mode is selected per run.

| Mode | Flag | Behaviour |
|---|---|---|
| **Static-file audit** | default | Reads checked-in files only. No tools required. Always safe. |
| **Live-access audit** | `--live` | Uses CLIs and APIs (read-only) to inspect real state: `kubectl get`, `terraform plan`, `aws s3 ls`, `docker inspect`, `npm audit`, Prometheus queries, etc. Falls back to static mode if tools/credentials aren't available. |
| **Apply mode** | `--apply` | After audit, prompts per finding: `[a]pply / [s]kip / apply [A]ll / [q]uit`. Writes YAML/HCL/JSON patches, runs `kubectl patch`, opens PRs. Every mutation is logged. Destructive operations (DELETE, DROP, `kubectl delete`) require a second confirmation. |
| **Runtime testing** | `--runtime` | Runs synthetic tests: load tests (k6), chaos experiments (chaos-mesh, Gremlin), synthetic alert fires, canary smoke tests. Requires a non-prod target; skill refuses to run against names containing `prod`/`production` without `--i-really-mean-prod`. |

Modes are composable: `--live --apply` means inspect real state, then offer to patch. `--runtime` implies `--live`.

---

## Installation

```bash
claude --plugin-dir ./engineering/devops
```

After Claude Code starts, run `/reload-plugins` to discover the skills.

Marketplace install:

```bash
/plugin install devops@anthril-claude-plugins
```

---

## Invocation

```
/devops:devops-needs-assessment
/devops:cicd-pipeline-audit .github/workflows/
/devops:cicd-pipeline-audit .github/workflows/ --apply
/devops:container-audit Dockerfile --live
/devops:iac-terraform-audit infra/ --live --apply
/devops:kubernetes-manifest-audit charts/api/ --live
/devops:observability-audit . --runtime
/devops:release-readiness-audit --base main --runtime
/devops:devsecops-supply-chain-audit . --live --apply
/devops:sre-reliability-audit . --runtime
```

---

## Where to start

If you're not sure which skill to run first:

```
/devops:devops-needs-assessment
```

It triages your application in plain language and points you at the two or three audits that will give the highest return for your situation.

---

## Output artefacts

Every audit writes outputs into the current working directory and never overwrites without confirmation.

| Skill | Files produced |
|---|---|
| `devops-needs-assessment` | `devops-needs-assessment.md` |
| `cicd-pipeline-audit` | `cicd-pipeline-audit.md`, `cicd-pipeline-audit.json`, `cicd-suggested.yml`, `apply-log.md` (if `--apply`) |
| `iac-terraform-audit` | `iac-terraform-audit.md`, `iac-terraform-audit.json`, `iac-suggested.tf`, `terraform-plan.txt` (if `--live`), `apply-log.md` (if `--apply`) |
| `container-audit` | `container-audit.md`, `container-audit.json`, `dockerfile-suggested.patch`, `image-scan.json` (if `--live`) |
| `kubernetes-manifest-audit` | `kubernetes-manifest-audit.md`, `kubernetes-manifest-audit.json`, `k8s-suggested.yaml`, `cluster-state.json` (if `--live`) |
| `observability-audit` | `observability-audit.md`, `observability-audit.json`, `synthetic-alert-trace.md` (if `--runtime`) |
| `release-readiness-audit` | `release-readiness-audit.md`, `rollback-procedure.md`, `canary-smoke-results.md` (if `--runtime`) |
| `devsecops-supply-chain-audit` | `devsecops-supply-chain-audit.md`, `devsecops-supply-chain-audit.json`, `slsa-self-assessment.md`, `sbom.json` (if `--live`) |
| `sre-reliability-audit` | `sre-reliability-audit.md`, `sre-reliability-audit.json`, `gameday-report.md` (if `--runtime`) |

---

## Safety guarantees

- **Audit-only by default.** Skills report; they do not mutate unless `--apply` is passed.
- **Per-finding confirmation in apply mode.** Every change shown before applied. Destructive operations (DELETE, DROP, `kubectl delete`) require a second confirmation with the literal word `DESTROY`.
- **Production-name guard.** `--runtime` refuses targets containing `prod`/`production` without the `--i-really-mean-prod` flag.
- **Credentials never in chat.** Live-mode CLIs read credentials from the usual places (`~/.aws/`, `~/.kube/config`, `$TF_VAR_*`) — the skill never reads or echoes credential files.
- **Apply log.** Every applied change is written to `apply-log.md` with timestamp, target, before/after, and revert command.

---

## Conventions

- **Australian English** in narrative
- **DD/MM/YYYY** date format
- **Markdown-first** outputs
- **Evidence-backed findings** — every finding carries a `file:line` reference (or live-state citation) and the excerpt that was matched
- **Suppression files** per skill: `.cicd-ignore`, `.iac-ignore`, `.k8s-ignore`, `.container-ignore`, `.secops-ignore`, `.obs-ignore`, `.release-ignore`, `.sre-ignore`

---

## License

MIT for the plugin wrapper. Per-skill `LICENSE.txt` is Apache 2.0 boilerplate.

---

## Author

[Anthril](https://github.com/anthril) — `john@anthril.com`
