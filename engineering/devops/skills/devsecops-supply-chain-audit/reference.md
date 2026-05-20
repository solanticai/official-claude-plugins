# DevSecOps Supply Chain Audit — Reference

## §1 — Audit Taxonomy

### A. Dependency pinning
| ID | Check |
|---|---|
| A.1 | Lockfile present and committed |
| A.2 | Lockfile ecosystem-appropriate (`package-lock.json`, `pnpm-lock.yaml`, `poetry.lock`, `go.sum`, `Gemfile.lock`, `Cargo.lock`) |
| A.3 | Integrity hashes where supported |
| A.4 | No wildcard `*` or unbounded `>=` version ranges on security-critical packages |
| A.5 | `engines` / `python_requires` / `toolchain` version declared |

### B. Vulnerability surface
| ID | Check |
|---|---|
| B.1 | No CRITICAL severity advisories in direct dependencies |
| B.2 | No HIGH severity advisories in production dependencies (dev deps tolerable with suppression) |
| B.3 | No packages older than 2 years without explicit pin justification |
| B.4 | No packages with known-exploited CVEs (CISA KEV catalogue) |
| B.5 | Transitive vulnerabilities audited (not just direct) |

### C. Secret patterns
| ID | Check |
|---|---|
| C.1 | No AWS access keys (`AKIA[0-9A-Z]{16}`, secret key patterns) |
| C.2 | No private keys (`-----BEGIN (RSA |EC |OPENSSH |DSA |)PRIVATE KEY-----`) |
| C.3 | No GitHub tokens (`ghp_`, `gho_`, `ghu_`, `ghs_`) |
| C.4 | No Slack tokens (`xoxb-`, `xoxp-`, `xoxa-`) |
| C.5 | No Stripe / Twilio / SendGrid API key prefixes |
| C.6 | No `.env` or `.env.*` files tracked |
| C.7 | No high-entropy strings in code that look like secrets |

### D. SBOM & provenance
| ID | Check |
|---|---|
| D.1 | SBOM (CycloneDX or SPDX) generated for releases |
| D.2 | SBOM attached to GitHub releases |
| D.3 | npm packages published with `--provenance` |
| D.4 | Container images referenced by digest in deployment |
| D.5 | SLSA level ≥ 1 |

### E. Image signing
| ID | Check |
|---|---|
| E.1 | Container images signed (cosign / sigstore) |
| E.2 | Signature verification in deployment pipeline |
| E.3 | Trust policy documented |

### F. Branch protection (repo-wide)
| ID | Check |
|---|---|
| F.1 | Default branch protected |
| F.2 | Required reviewers (≥1; ideally 2 for prod-critical repos) |
| F.3 | Required status checks include security + tests |
| F.4 | Signed commits required |
| F.5 | Linear history required |
| F.6 | `main`/`master` cannot be deleted |

### G. CODEOWNERS
| ID | Check |
|---|---|
| G.1 | `.github/CODEOWNERS` exists |
| G.2 | Covers `.github/workflows/` (meta-protection) |
| G.3 | Covers infra directories (`infra/`, `terraform/`, `k8s/`) |
| G.4 | Covers security-sensitive paths (`auth/`, `payments/`, `crypto/`) |

### H. Automation
| ID | Check |
|---|---|
| H.1 | Dependabot or Renovate configured |
| H.2 | Grouping sensible (one PR per ecosystem minor/patch) |
| H.3 | Security updates fast-lane (separate config) |
| H.4 | Auto-merge for patch versions where CI passes |
| H.5 | Last 10 automated PRs not ignored (live mode) |

---

## §2 — Severity Rubric

| Severity | Examples |
|---|---|
| CRITICAL | Known-exploited CVE in prod dep (CISA KEV), AWS/GitHub token in HEAD, no lockfile on a published package, `main` branch unprotected on prod repo |
| HIGH | HIGH CVE in prod dep, secret in history (rotated but not scrubbed), signed commits not required, no required reviewers, missing CODEOWNERS on infra |
| MEDIUM | MEDIUM CVEs, no SBOM, no `--provenance`, Dependabot PRs piling up |
| INFO | SLSA L1 but not L2, auto-merge not enabled for patches |

---

## §3 — SLSA Level Self-Assessment

| Level | Requires |
|---|---|
| L0 | — (default) |
| L1 | Documented build process, provenance generated |
| L2 | Hosted/audited build service (GH Actions counts), authenticated publishes, provenance signed |
| L3 | Hardened build environment, ephemeral runners, tamper-evident provenance |
| L4 | Two-party code review for every build, reproducible builds, hermetic |

---

## §4 — Scoring Weights

| Category | Weight |
|---|---|
| A. Dependency pinning | 15 |
| B. Vulnerability surface | 25 |
| C. Secret patterns | 20 |
| D. SBOM & provenance | 10 |
| E. Image signing | 5 |
| F. Branch protection | 15 |
| G. CODEOWNERS | 5 |
| H. Automation | 5 |

---

## §5 — Ecosystem-Specific Notes

| Ecosystem | Lockfile | Scanner | Pinning idiom |
|---|---|---|---|
| npm | `package-lock.json` | `npm audit` | Exact in prod deps; `^` tolerable in dev |
| pnpm | `pnpm-lock.yaml` | `pnpm audit` | Same as npm |
| yarn | `yarn.lock` | `yarn npm audit` | Same as npm |
| pip | `requirements.txt` (with `==`) | `pip-audit` | Always `==` for apps |
| Poetry | `poetry.lock` | `pip-audit` (exported) | `poetry.lock` is authoritative |
| Go | `go.sum` | `govulncheck` | Specific versions via `go get` |
| Cargo | `Cargo.lock` | `cargo audit` | `Cargo.lock` commit for apps only (libraries omit) |
| Bundler | `Gemfile.lock` | `bundler-audit` | `Gemfile.lock` authoritative |
| Maven | `pom.xml` | `dependency-check` | Explicit `<version>` in `<dependencies>` |
| Gradle | Lockfile via plugin | `dependency-check-gradle` | Enable lockfile mode |
| Composer | `composer.lock` | `roave/security-advisories` | Lockfile authoritative |
| Docker | Dockerfile | `trivy image` / `grype` | Pin by digest |
| Terraform | `.terraform.lock.hcl` | `checkov` / `tfsec` for IaC | Provider pinning in `required_providers` |
