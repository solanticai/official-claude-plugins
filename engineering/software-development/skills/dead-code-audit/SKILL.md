---
name: dead-code-audit
description: Audit a codebase for dead code — unused exports, orphaned files, dead dependencies, unreachable branches, abandoned flags, unused CSS — across multiple languages. Produces a confidence-scored report with cleanup actions. Use for dead code, code cleanup, bundle bloat, pre-refactor analysis.
argument-hint: [target-directory-or-package]
allowed-tools: Read Grep Glob Write Edit Bash(git:*, ls:*, wc:*, find:*, cat:*, mkdir:*, test:*) Agent
effort: high
---

# Dead Code Audit

ultrathink

## Before You Start

1. **Locate the target.** Use `$ARGUMENTS` if provided, otherwise the current working directory. If neither resolves to a real directory, ask the user for the target path before continuing.
2. **Detect the stack.** Run `scripts/detect-stack.sh` to identify languages, frameworks, and monorepo layout. This determines which tool matrix to apply in Phase 2.
3. **Check tooling availability.** Run `scripts/check-tools.sh`. Missing tools are reported as Phase 1 findings — continue with whichever tools are available rather than aborting.
4. **Load `.deadcode-ignore`.** If the target directory contains a `.deadcode-ignore` file, parse it and treat the patterns as suppression rules during Phase 7.
5. **Map project structure.** Inventory the codebase excluding `node_modules/`, `.venv/`, `venv/`, `target/`, `dist/`, `build/`, `.next/`, `.nuxt/`, `coverage/`, `.git/`.

## User Context

$ARGUMENTS

Detected stack: !`bash "${CLAUDE_PLUGIN_ROOT}/skills/dead-code-audit/scripts/detect-stack.sh" .`

Tool availability: !`bash "${CLAUDE_PLUGIN_ROOT}/skills/dead-code-audit/scripts/check-tools.sh" .`

---

## Audit Phases

Execute every phase in order. For each finding, record: file path, line number (or symbol identifier), category, subtype, raw tool output, baseline confidence. Use the rubric in `${CLAUDE_PLUGIN_ROOT}/skills/dead-code-audit/reference.md` §3 for scoring. Do not skip phases — mark as `N/A` if genuinely not applicable to the detected stack.

**Read-only guarantee.** This skill never modifies source files. Every finding is a hypothesis requiring user review. The output is a report, not a refactor.

---

### Phase 1: Stack Discovery & Inventory (context only — no score)

**Objective:** Build an accurate picture of the codebase before scanning.

1. Read top-level config files: `package.json`, `pyproject.toml` / `setup.py` / `requirements*.txt`, `go.mod`, `Cargo.toml`, `pom.xml` / `build.gradle*`, `composer.json`, `Gemfile`, `*.csproj` / `*.sln`.
2. Detect monorepo layout: `pnpm-workspace.yaml`, `lerna.json`, `nx.json`, `turbo.json`, `Cargo.toml [workspace]`, `go.work`, `rush.json`. If detected, list each package and treat each as an audit target.
3. Identify build, test, and lint frameworks per language.
4. Count files by extension to scope the audit (helps right-size tool invocations).
5. Read `.deadcode-ignore` (if present) and any framework-specific ignore files (`.knipignore`, `vulture-whitelist.py`, etc.).
6. Note any configuration that affects detection: `tsconfig.json` `paths`, Python `__all__`, Rust `pub use` re-exports, Go `//go:build` tags.

This phase produces a context block at the top of the report. No score.

---

### Phase 2: Code-Level Dead Code (25 points)

**Objective:** Detect dead symbols inside source files using the per-language tool matrix in `reference.md` §1.

For each detected language, run the appropriate tool from the matrix:

- **JS/TS:** `scripts/run-knip.sh` (preferred) or `npx knip --reporter json`. Knip detects unused files, exports, types, deps, and class members in one pass.
- **Python:** `scripts/run-vulture.sh` or `vulture . --min-confidence 60`. Cross-checks with `ruff check --select F401,F841` for per-file unused imports/locals.
- **Go:** `deadcode ./...` from `golang.org/x/tools/cmd/deadcode` (sound callgraph analysis), plus `staticcheck -checks U1000 ./...`.
- **Rust:** `cargo +nightly rustc -- -W dead_code` for code-level, `cargo machete` for deps (see Phase 3).
- **Java/Kotlin:** Qodana CLI with `UnusedDeclarationInspection` enabled, or IntelliJ headless inspect.
- **PHP:** `vendor/bin/phpstan analyse` and `vendor/bin/dead-code-detector` (shipmonk).
- **Ruby:** `debride .` plus `rubocop --only Lint/UselessAssignment,Lint/UnusedMethodArgument`.
- **C#:** `dotnet format analyzers --diagnostics IDE0051 IDE0052 IDE0059 IDE0060`.

For every finding, capture one of these subtypes (full taxonomy in `reference.md` §2):

| Subtype | Default baseline |
|---|---|
| `unused-import` | 95 |
| `unused-local` | 95 |
| `unreachable-code` | 100 |
| `unused-private-member` | 80 |
| `unused-export` | 65 |
| `unused-file` | 65 |
| `unused-react-component` | 70 |
| `unused-api-route` | 60 |
| `commented-code-block` | 75 |
| `orphaned-test-file` | 80 |

Findings are raw at this stage — Phase 7 verifies and adjusts confidence.

Score: deduct points per the rubric in `reference.md` §3, capped at 25.

---

### Phase 3: Dependency-Level Dead Code (15 points)

**Objective:** Identify unused or duplicate package dependencies.

Run per language:

- **JS/TS:** `npx knip --dependencies --reporter json` (or `npx depcheck --json`).
- **Python:** Compare imports in source against `pyproject.toml` / `requirements*.txt`. Use `pip-check` if available.
- **Go:** `go mod why <module>` for each dep listed in `go.mod`, plus `go mod tidy -v` dry-run.
- **Rust:** `cargo machete` (fast) and `cargo udeps` (accurate, requires nightly) if available.
- **Java:** `mvn dependency:analyze` or Gradle `dependencyInsight`.
- **PHP:** `composer-unused` if installed.
- **Ruby:** Cross-reference `Gemfile.lock` against `require`/`require_relative` calls.
- **C#:** `dotnet list package --vulnerable` plus manual check of `<PackageReference>` usage.

Categorise findings: `unused-runtime-dep`, `unused-dev-dep`, `duplicate-dep`, `version-mismatch`, `lockfile-drift`.

Score: 15 minus deductions per `reference.md` §3.

---

### Phase 4: Asset & Style Dead Code (10 points)

**Objective:** Find unused styles, images, fonts, and other static assets.

1. **Tailwind CSS** — read `tailwind.config.{js,ts}`. Tailwind 3+ purges automatically; flag legacy `purge:` configs as a finding rather than a dead-code issue. For `@apply` and custom CSS, scan `*.css` for class definitions and grep source for usages.
2. **Plain CSS / SCSS** — extract class selectors and grep across `*.{ts,tsx,js,jsx,vue,svelte,html}` for matches.
3. **Image assets** — list files under `public/`, `static/`, `assets/`, `src/assets/`. For each, grep source for the basename. Report any with zero references.
4. **Fonts** — scan `<link rel="stylesheet">` and `@font-face` declarations; check against actual usage in CSS.
5. **Icon sprites / SVG manifests** — if `sprites.svg` or similar exists, list symbol IDs and verify each is referenced.

Note: Asset detection has high false-positive risk for projects using dynamic class names (`bg-${color}-500`). Mark such findings with reduced confidence and a `dynamic-class-risk` flag.

Score: 10 minus deductions per `reference.md` §3.

---

### Phase 5: Infrastructure Dead Code (15 points)

**Objective:** Find dead environment variables, feature flags, migrations, CI jobs, and Docker stages.

1. **Environment variables** — extract names from `.env*` files and from `process.env.*` / `os.environ.*` / `env::var(...)` references in source. Report:
   - Variables defined in `.env*` but never read in source (`unused-env-var`)
   - Variables read in source but never defined in any `.env*` or CI config (`undefined-env-var-reference`)
2. **Feature flags** — locate flag definitions (LaunchDarkly, Unleash, ConfigCat, custom flag tables). For each, grep source for the flag key. Report flags with no consumers (`dead-feature-flag`).
3. **Database migrations** — list migration files, check filenames for `*revert*`/`*rollback*`, and read recent migrations to detect column additions that were later dropped without follow-up. Output as `orphaned-migration` (informational).
4. **DB columns** — if a schema file or generated types file is present (e.g., `database.types.ts` from Supabase, `schema.rb` from Rails, Prisma `schema.prisma`), list columns and grep source for each. Flag candidates with `db-column-candidate`. **These findings are FLAG-ONLY — see Important Principles.**
5. **CI jobs** — read `.github/workflows/*.yml`, `.gitlab-ci.yml`, `.circleci/config.yml`. Find jobs that are never triggered (no matching `on:` event, never called from another workflow).
6. **Docker stages** — read `Dockerfile`s for multi-stage builds; flag named stages that are never `COPY --from=`'d.

Score: 15 minus deductions per `reference.md` §3. **DB column findings are never deducted from this score** — they are informational only.

---

### Phase 6: Documentation & Comment Graveyards (5 points)

**Objective:** Find stale documentation and large commented-out code blocks.

1. **README references** — grep `README.md` and top-level docs for filenames, then check each referenced path exists.
2. **Internal markdown links** — for every `.md` file, check that relative links resolve.
3. **JSDoc / docstring references** — grep `@see`, `@link`, `Reference:`, `See:` annotations and verify the targets still exist.
4. **Commented-out code blocks** — find runs of `>5` consecutive comment lines that look like code (have `;`, `{`, `}`, `def `, `function `, `import `, `class `). Report as `commented-code-block`.
5. **Stale TODO/FIXME** — use `git blame` to find TODO/FIXME comments older than 12 months. Report as `stale-todo` (low severity).

Score: 5 minus deductions per `reference.md` §3.

---

### Phase 7: Verification & Confidence Scoring (20 points)

**Objective:** Walk every finding through the 10-step verification protocol and adjust confidence.

For each finding from Phases 2–6, apply the protocol from `reference.md` §4:

1. Full-repo grep for the symbol name (case-sensitive and case-insensitive).
2. Sibling-package grep (monorepos): grep across all workspace packages.
3. Config-file scan: `*.json`, `*.yml`, `*.yaml`, `*.toml`, `*.env*`, `*.config.*`.
4. Test-file scan separately: `**/*.test.*`, `**/*.spec.*`, `__tests__/**`, `tests/**`, `*_test.go`, `test_*.py`.
5. Documentation scan: `*.md`, `*.mdx`, `docs/**`.
6. DI / route registration scan: `routes.ts`, `app.module.ts`, `urls.py`, `web.php`, `routes.rb`, framework router files.
7. Dynamic-reference scan: look for `getattr(`, string-key dispatch (`registry["..."]`), route param binding, reflection (`Class.forName`, `Activator.CreateInstance`), `eval(`, dynamic imports.
8. Git blame age check: very recently added code is more likely intentional even if currently unreferenced.
9. Coverage data check: if `coverage/`, `lcov.info`, `coverage.xml`, or `.coverage` exists, cross-reference findings against coverage.
10. Framework convention check from `reference.md` §5: file-conventional routes (Next.js `page.tsx`, `route.ts`, `layout.tsx`; Rails autoload paths; Django `urls.py`; Laravel routes), decorator-discovered handlers, proc-macros, etc.

After verification, adjust confidence per `reference.md` §3 rules. Drop findings below 60. For `unused-export` or `unused-file` findings between 60 and 89, **spawn an `Agent(subagent_type=Explore)`** with a focused prompt to deep-search for dynamic references the static tools may have missed. Record the verification trail for each finding.

**For `.deadcode-ignore` entries**, suppress matching findings entirely and surface them in the report as a "suppressed by ignore file" tally.

Score: 20 minus deductions per `reference.md` §3.

---

### Phase 8: Reporting (10 points)

**Objective:** Produce the final report.

Generate the markdown report using `${CLAUDE_PLUGIN_ROOT}/skills/dead-code-audit/templates/output-template.md` as the structural skeleton. The report must include:

1. Executive summary with verdict, top wins, top risks
2. Stack & tooling table
3. Findings grouped by confidence tier (CRITICAL / WARNING / SUGGESTION / FLAG-ONLY)
4. Findings grouped by category
5. Detail blocks for the top 20 findings, each with full verification evidence
6. Suggested `.deadcode-ignore` entries for known false positives
7. Prioritised action list grouped into thematic batches
8. Mermaid pie chart of findings by category
9. Pointer to a JSON sidecar (use `templates/findings-schema.json` shape)

Severity mapping (per `reference.md` §7):

- **CRITICAL** — confidence ≥90 AND ≥10 LOC saved
- **WARNING** — confidence 70–89 OR confidence ≥90 with <10 LOC
- **SUGGESTION** — confidence 60–69
- **FLAG-ONLY** — DB columns, dynamic-dispatch suspects, anything explicitly excluded from auto-action recommendations

Score: 10 minus deductions for missing report sections.

---

## Total Score & Verdict

| Phase | Max | What it measures |
|---|---|---|
| Phase 2 — Code-level | 25 | Dead symbols, exports, files |
| Phase 3 — Dependencies | 15 | Unused / duplicate packages |
| Phase 4 — Assets & styles | 10 | Dead CSS, images, fonts |
| Phase 5 — Infrastructure | 15 | Env vars, flags, CI, Docker (DB columns flag-only) |
| Phase 6 — Documentation | 5 | Stale docs, comment graveyards |
| Phase 7 — Verification | 20 | Confidence scoring quality |
| Phase 8 — Reporting | 10 | Report completeness |
| **Total** | **100** | |

The total reflects how *clean* the codebase is, not how good the audit was — high scores mean little dead code was found. Verdicts:

- **90–100** — CLEAN
- **70–89** — MODERATE DEBT
- **50–69** — HIGH DEBT
- **0–49** — CRITICAL DEBT

---

## Important Principles

- **Every finding is a hypothesis, not a delete command.** The report describes evidence. The user decides what to act on.
- **Never propose deleting public API symbols** without an explicit "exported intentionally" check. Public surface area requires human review even at high confidence.
- **DB columns are FLAG-ONLY.** Never propose dropping a column. Database changes require schema migrations, application changes, and backfills coordinated outside the scope of this skill. Reports must use the exact phrase `MANUAL REVIEW REQUIRED — DO NOT AUTO-DELETE` next to DB column findings.
- **Every finding includes a file path and line number** (or unambiguous symbol identifier). "Some unused exports somewhere" is useless.
- **Respect `.deadcode-ignore`** entries. Treat them as load-bearing and surface them as suppressed in the report.
- **Do not modify any source files.** This is a report-only skill. If the user asks for cleanup, point them at the prioritised action list and let them drive the changes.
- **Prefer running real tools over guessing.** `knip`, `vulture`, `deadcode` output beats eyeballing imports.
- **Document tool versions** in the report so audits are reproducible.

---

## Edge Cases

1. **Empty project / new project.** If fewer than 20 source files exist, run a lightweight scan and produce a "no significant findings" report with stack detection only. Don't fabricate findings to fill phases.
2. **Monorepo.** Treat each workspace package as a separate audit target and produce a per-package summary plus a workspace-level rollup. Cross-package references count as "used" during verification.
3. **Generated code.** Files marked as generated (`@generated`, `// AUTO-GENERATED`, `__generated__/`, `*.gen.ts`) must be excluded from findings — verification step 7 catches this. List excluded directories in the report.
4. **Public library / SDK.** When `package.json` `name` is scoped (`@org/...`) or `pyproject.toml` declares a published package, treat all `unused-export` findings as confidence ≤60 (suggestion only). Public API cannot be assessed from inside the package.
5. **Framework conventions.** Next.js `app/`, `pages/`, Rails autoload paths, Django `urls.py` includes, Laravel auto-discovered controllers — these files appear orphaned to static analysis but are loaded by convention. Phase 7 step 10 must catch these; if it doesn't, a finding here is a bug in the verification protocol.
6. **Reflection-heavy languages.** Java DI, .NET reflection, Ruby `method_missing`, Python `getattr` — tools cannot statically prove a method is unused. Mark findings in reflection-heavy code as `dynamic-dispatch-risk` and lower confidence by 30 points.
7. **Test-only code.** Helpers in `test/` or `__tests__/` that are only used by other tests are NOT dead — they are part of the test infrastructure. Verification step 4 must isolate this case.
8. **Tool failures.** If a language tool crashes, returns non-zero, or is missing, record it as a Phase 1 finding and continue with the remaining tools rather than aborting the audit.
