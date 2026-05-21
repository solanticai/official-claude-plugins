# Codebase Profiler — Reference Material

---

## Health Dimension Scoring Rubric

### 1. Dependency Health

| Signal | ✓ Healthy | ⚠ Needs Attention | ✗ Significant Risk |
|---|---|---|---|
| CVEs (critical/high) | 0 | 1–2 high, 0 critical | Any critical, or ≥3 high |
| Outdated deps | <10% of total | 10–30% | >30% or any `"latest"` / `"*"` |
| Circular imports | 0 | 1–3 cycles | >3 cycles |
| Unlocked deps (no lockfile) | Lockfile present | — | No lockfile |

### 2. Test Coverage

| Signal | ✓ Healthy | ⚠ Needs Attention | ✗ Significant Risk |
|---|---|---|---|
| Coverage % (if measured) | ≥70% | 40–69% | <40% |
| Test-to-source ratio | ≥0.5 | 0.2–0.49 | <0.2 |
| Test framework present | Yes | — | No tests detected |
| Coverage config present | Yes | — | No coverage config |

### 3. Type Safety

| Signal | ✓ Healthy | ⚠ Needs Attention | ✗ Significant Risk |
|---|---|---|---|
| TypeScript strict mode | `strict: true` | Some strict flags | No TypeScript / strict off |
| `any` usage | <20 occurrences | 20–100 | >100 or `@ts-nocheck` files |
| `@ts-ignore` count | 0–5 | 6–20 | >20 |

### 4. Code Complexity

| Signal | ✓ Healthy | ⚠ Needs Attention | ✗ Significant Risk |
|---|---|---|---|
| Files >300 LOC | <5% of source files | 5–15% | >15% |
| TODO/FIXME density | <1 per 500 SLOC | 1–3 per 500 SLOC | >3 per 500 SLOC |
| Largest file | <500 LOC | 500–1,000 LOC | >1,000 LOC |

### 5. Security Surface

| Signal | ✓ Healthy | ⚠ Needs Attention | ✗ Significant Risk |
|---|---|---|---|
| Hardcoded secret patterns | 0 | 1–2 (low-severity) | Any high-severity pattern |
| .env files in .gitignore | All covered | Some missing | None covered |
| Dependency CVEs | 0 | High-severity only | Critical present |
| `pull_request_target` misuse | Not present | — | Present without `if:` guard |

### 6. Infrastructure Maturity

| Signal | ✓ Healthy | ⚠ Needs Attention | ✗ Significant Risk |
|---|---|---|---|
| CI/CD present | Yes | Manual deploy only | No CI/CD |
| Hosting config present | Yes | Ad-hoc | None detected |
| Docker / IaC | Present | Partial | None |
| Multi-environment support | .env.staging/.env.prod | Single env | Hardcoded env values |

### 7. Observability

| Signal | ✓ Healthy | ⚠ Needs Attention | ✗ Significant Risk |
|---|---|---|---|
| Error tracking | Sentry / Datadog / etc. | Log-only | No error tracking |
| Structured logging | Pino / Winston / structlog | console.log | No logging |
| APM / tracing | OpenTelemetry / Datadog APM | Basic metrics | None |

### 8. Developer Experience

| Signal | ✓ Healthy | ⚠ Needs Attention | ✗ Significant Risk |
|---|---|---|---|
| Linting config | Present and enforced in CI | Present, not in CI | Absent |
| CHANGELOG / semver | Present | Partial | Absent |
| Pre-commit hooks | Present | — | Absent |
| README present | Comprehensive | Minimal | Absent |

---

## Language Detection Patterns

| Extension(s) | Language |
|---|---|
| `.ts`, `.tsx` | TypeScript |
| `.js`, `.jsx`, `.mjs`, `.cjs` | JavaScript |
| `.py` | Python |
| `.rs` | Rust |
| `.go` | Go |
| `.java` | Java |
| `.kt`, `.kts` | Kotlin |
| `.rb` | Ruby |
| `.php` | PHP |
| `.cs` | C# |
| `.cpp`, `.cc`, `.cxx`, `.h`, `.hpp` | C/C++ |
| `.swift` | Swift |
| `.ex`, `.exs` | Elixir |
| `.scala` | Scala |
| `.sql` | SQL |
| `.sh`, `.bash` | Shell |

Exclude from SLOC counts: `node_modules/`, `.git/`, `dist/`, `build/`, `out/`, `coverage/`,
`__pycache__/`, `*.min.js`, `*.min.css`, `*.map`, `*.lock`, `*.sum`.

---

## Framework Detection Heuristics

Check `package.json` `dependencies` / `devDependencies` for these keys:

| Dep key | Framework label |
|---|---|
| `next` | Next.js |
| `nuxt` | Nuxt.js |
| `@sveltejs/kit` | SvelteKit |
| `@remix-run/node` | Remix |
| `astro` | Astro |
| `react` (no framework) | React (CRA / Vite) |
| `vue` | Vue |
| `@angular/core` | Angular |
| `express` | Express |
| `fastify` | Fastify |
| `hono` | Hono |
| `@nestjs/core` | NestJS |
| `electron` | Electron |
| `react-native` | React Native |
| `expo` | Expo |

For Python: detect `fastapi`, `flask`, `django`, `starlette` from `requirements.txt` / `pyproject.toml`.
For Go: detect `gin`, `echo`, `fiber`, `chi` from `go.mod`.
For Rust: detect `actix-web`, `axum`, `rocket` from `Cargo.toml`.

---

## Secret Detection Patterns

These patterns are checked by `infra-security-scanner` via `grep -rn` against source files
(excluding `node_modules/`, `.git/`, `.env*` files, and lockfiles):

| Pattern | Type | Severity |
|---|---|---|
| `AKIA[0-9A-Z]{16}` | AWS Access Key ID | CRITICAL |
| `-----BEGIN (RSA\|EC\|OPENSSH) PRIVATE KEY-----` | Private key | CRITICAL |
| `sk-[a-zA-Z0-9]{48}` | OpenAI API key | CRITICAL |
| `AIza[0-9A-Za-z-_]{35}` | Google API key | HIGH |
| `ghp_[a-zA-Z0-9]{36}` | GitHub personal token | HIGH |
| `ghs_[a-zA-Z0-9]{36}` | GitHub Actions token | HIGH |
| `sk_live_[0-9a-zA-Z]{24}` | Stripe live key | CRITICAL |
| `rk_live_[0-9a-zA-Z]{24}` | Stripe restricted key | HIGH |
| `xoxb-[0-9]+-[0-9]+-[a-zA-Z0-9]+` | Slack bot token | HIGH |
| `[Pp]assword\s*=\s*['"][^'"]{8,}['"]` | Hardcoded password | HIGH |
| `[Ss]ecret\s*=\s*['"][^'"]{16,}['"]` | Hardcoded secret | MEDIUM |
| `[Aa][Pp][Ii]_?[Kk]ey\s*=\s*['"][^'"]{16,}['"]` | Generic API key | MEDIUM |

Never include matched secret values in the profile document — write `[REDACTED]` and cite only the file:line.

---

## CI/CD Provider Detection

| File path | Provider |
|---|---|
| `.github/workflows/*.yml` | GitHub Actions |
| `.gitlab-ci.yml` | GitLab CI |
| `Jenkinsfile` | Jenkins |
| `.circleci/config.yml` | CircleCI |
| `bitbucket-pipelines.yml` | Bitbucket Pipelines |
| `.buildkite/pipeline.yml` | Buildkite |
| `azure-pipelines.yml` | Azure DevOps |
| `cloudbuild.yaml` | Google Cloud Build |
| `appspec.yml` | AWS CodeDeploy |
| `Makefile` (with CI targets) | Make-based CI |
| `Taskfile.yml` | Task-based CI |

---

## Hosting Provider Detection

| Config file | Provider |
|---|---|
| `vercel.json` / `.vercelignore` | Vercel |
| `fly.toml` | Fly.io |
| `wrangler.toml` / `wrangler.json` | Cloudflare Workers / Pages |
| `netlify.toml` / `_redirects` | Netlify |
| `railway.json` / `railway.toml` | Railway |
| `render.yaml` | Render |
| `Dockerfile` + `docker-compose.yml` | Self-hosted / Docker |
| `k8s/*.yaml` / `helm/` | Kubernetes |
| `app.yaml` | Google App Engine |
| `.platform/` / `platform.sh.yaml` | Platform.sh |
| `Procfile` | Heroku / Render / Railway |
| `serverless.yml` | Serverless Framework |
| `sam.yaml` / `template.yaml` | AWS SAM |
| `cdk.json` | AWS CDK |

---

## License Permissiveness Tiers

| Tier | Licences | Commercial use |
|---|---|---|
| Permissive | MIT, Apache-2.0, BSD-2, BSD-3, ISC, 0BSD | ✓ Free |
| Weak copyleft | LGPL-2.1, LGPL-3.0, MPL-2.0, EPL-2.0 | ⚠ Conditions apply |
| Strong copyleft | GPL-2.0, GPL-3.0, AGPL-3.0, EUPL | ✗ Viral; requires legal review |
| Proprietary | UNLICENSED, BUSL, custom | ✗ Requires explicit permission |

Flag any `GPL` or `AGPL` dep in a commercial project as HIGH severity.

---

## Complexity Thresholds

| Project size (SLOC) | Large file threshold | High TODO density |
|---|---|---|
| <10k | >200 LOC | >5 per file |
| 10k–50k | >300 LOC | >3 per file |
| 50k–200k | >400 LOC | >2 per file |
| >200k (shallow) | >500 LOC | >1 per file |

Test ratio benchmarks (test files ÷ source files):

| Ratio | Assessment |
|---|---|
| ≥0.8 | Excellent coverage density |
| 0.5–0.79 | Good |
| 0.2–0.49 | Moderate — may have gaps |
| <0.2 | Low — likely under-tested |

---

## Monorepo Detection Signals

| File | Tool |
|---|---|
| `pnpm-workspace.yaml` | pnpm workspaces |
| `turbo.json` | Turborepo |
| `nx.json` | Nx |
| `lerna.json` | Lerna |
| `rush.json` | Rush |
| `yarn.lock` + `workspaces` in root `package.json` | Yarn workspaces |
| `Cargo.toml` with `[workspace]` | Rust workspace |
| `go.work` | Go workspace |
| `pyproject.toml` with `[tool.poetry.packages]` | Poetry monorepo |

If any of the above are present, set `monorepo: true` and count workspace packages.
