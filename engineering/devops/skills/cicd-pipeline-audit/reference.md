# CI/CD Pipeline Audit — Reference

## §1 — Audit Taxonomy

### A. Security
| ID | Check |
|---|---|
| A.1 | Workflow-level `permissions:` declared and minimal |
| A.2 | Job-level `permissions:` override where broader access is needed |
| A.3 | Third-party actions pinned by commit SHA (not tag/branch) |
| A.4 | `pull_request_target` only used with untrusted-checkout guards |
| A.5 | Secrets not referenced in `if:` conditions |
| A.6 | OIDC used for cloud auth instead of long-lived access keys |
| A.7 | `GITHUB_TOKEN` scoped appropriately (not relying on default) |
| A.8 | No `workflow_run` triggers that pass untrusted artefacts into trusted jobs |

### B. Reliability
| ID | Check |
|---|---|
| B.1 | Concurrency group set with `cancel-in-progress` where appropriate |
| B.2 | `timeout-minutes` set per job (not relying on 6-hour default) |
| B.3 | Retry strategy on known-flaky steps (network, external APIs) |
| B.4 | Matrix `fail-fast: false` where partial-success is desired |
| B.5 | `needs:` graph doesn't have diamond dependencies that serialize unnecessarily |

### C. Reproducibility
| ID | Check |
|---|---|
| C.1 | Runner pinned to specific OS version (`ubuntu-22.04`, not `ubuntu-latest`) on release workflows |
| C.2 | Tool versions pinned (setup-node/python/go with exact version or `.tool-versions` / `.nvmrc` reference) |
| C.3 | Lockfile committed and used via `npm ci` / `pnpm install --frozen-lockfile` / etc. |
| C.4 | Container images referenced by digest, not tag |
| C.5 | Build outputs byte-reproducible where possible |

### D. Speed & Cache
| ID | Check |
|---|---|
| D.1 | Dependency cache key includes lockfile hash |
| D.2 | Path filters (`on.push.paths`) used on monorepos to skip unrelated changes |
| D.3 | Artefacts reused between jobs rather than rebuilt |
| D.4 | Matrix parallelism sensibly bounded |
| D.5 | Heavy jobs use `if:` to skip when not needed |

### E. Supply chain
| ID | Check |
|---|---|
| E.1 | `npm publish --provenance` (or equivalent) on publish steps |
| E.2 | SBOM generated (Syft / CycloneDX) and attached to release |
| E.3 | Artefacts signed with cosign / sigstore |
| E.4 | Third-party actions from trusted orgs (`actions/`, `github/`, `Azure/`, named vendors) |
| E.5 | No `curl | bash` or `wget | sh` in workflow steps |
| E.6 | `npm install` never run without `--ignore-scripts` for untrusted deps, or with lockfile integrity |

### F. Secrets hygiene
| ID | Check |
|---|---|
| F.1 | No `echo ${{ secrets.* }}` or `run: echo $SECRET` |
| F.2 | Secrets not interpolated into shell strings without quoting |
| F.3 | No secrets in step names or job names (they appear in the UI) |
| F.4 | No secrets written to artefacts |
| F.5 | Environment variables named to avoid shadowing (no `env.GITHUB_TOKEN`) |

### G. Deploy safety
| ID | Check |
|---|---|
| G.1 | Production deploys gated by `environment:` with required reviewers |
| G.2 | Wait timers on production environment (cool-down between deploys) |
| G.3 | Staging runs before prod in the deploy graph |
| G.4 | Rollback workflow exists and is discoverable |
| G.5 | Deploy jobs tagged with environment URL for audit trail |

### H. Observability
| ID | Check |
|---|---|
| H.1 | Failure notifications (Slack / email / webhook) configured |
| H.2 | Required status checks enforced on default branch |
| H.3 | Workflow run history shows acceptable success rate (live mode) |
| H.4 | Artefact sizes don't grow unbounded (cache eviction, retention set) |

---

## §2 — Severity Rubric

| Severity | Definition |
|---|---|
| **CRITICAL** | Active exploit path, or production deploy without any safety (missing approval + no environment protection). Examples: secrets echoed in logs, unpinned third-party action in release workflow, `pull_request_target` + untrusted checkout. |
| **HIGH** | No active exploit but substantial risk. Examples: tag-pinned third-party actions, missing timeouts on prod deploy, `GITHUB_TOKEN` using default permissions on a deploy workflow. |
| **MEDIUM** | Risk or debt that compounds. Examples: unpinned runner, no concurrency control, missing cache on heavy workflow. |
| **INFO** | Observation without direct risk. Examples: "matrix could be optimised", "consider adding path filters". |

---

## §3 — Scoring Rubric

Category weights (sum to 100):

| Category | Weight |
|---|---|
| A. Security | 25 |
| B. Reliability | 10 |
| C. Reproducibility | 10 |
| D. Speed & Cache | 10 |
| E. Supply chain | 15 |
| F. Secrets hygiene | 15 |
| G. Deploy safety | 10 |
| H. Observability | 5 |

Per category, score = 100 × (checks_passed / checks_applicable). Aggregate = weighted mean. Mode: live mode can lower category scores via recent-run success rates (H).

---

## §4 — Platform Hints

| Platform | Config files | Key CLI |
|---|---|---|
| GitHub Actions | `.github/workflows/*.yml` | `gh` |
| GitLab CI | `.gitlab-ci.yml`, `.gitlab/` | `glab` |
| CircleCI | `.circleci/config.yml` | `circleci` |
| Azure Pipelines | `azure-pipelines.yml`, `.azure/` | `az pipelines` |
| Jenkins | `Jenkinsfile`, `jenkins/` | `jenkins-cli` |
| Bitbucket | `bitbucket-pipelines.yml` | — |

Platform-specific severity hints and known gotchas are tracked in each sub-agent's prompt template.
