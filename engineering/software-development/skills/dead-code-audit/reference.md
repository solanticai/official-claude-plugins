# Dead Code Audit Reference

Dense lookup tables, tool matrices, and scoring rules for the dead-code-audit skill. Loaded on demand from `SKILL.md`.

## Table of Contents

- [1. Per-Language Tool Matrix](#1-per-language-tool-matrix)
- [2. Dead-Code Category Taxonomy](#2-dead-code-category-taxonomy)
- [3. Confidence Scoring Rubric](#3-confidence-scoring-rubric)
- [4. 10-Step Verification Protocol](#4-10-step-verification-protocol)
- [5. False-Positive Patterns by Framework](#5-false-positive-patterns-by-framework)
- [6. `.deadcode-ignore` File Format](#6-deadcode-ignore-file-format)
- [7. Severity & Action Mapping](#7-severity--action-mapping)
- [8. Tool Output Normalisation](#8-tool-output-normalisation)
- [9. Quick Tool Install Commands](#9-quick-tool-install-commands)

---

## 1. Per-Language Tool Matrix

### JavaScript / TypeScript

| Tool | Install | Run | Strengths | Limitations |
|---|---|---|---|---|
| **knip** (canonical) | `npm i -D knip` | `npx knip --reporter json` | Files, exports, types, deps, class members in one pass. Knows Next.js, Vite, Storybook, Jest, Vitest, ESLint. Active maintenance. | Requires a `knip.json` for non-default monorepo layouts. |
| ts-prune | `npm i -D ts-prune` | `npx ts-prune` | Lightweight, only unused TS exports. | **Maintenance mode.** Use knip instead. |
| depcheck | `npm i -D depcheck` | `npx depcheck --json` | Dependency-only analysis. | Misses dev-only deps used via npm scripts. |
| eslint-plugin-unused-imports | `npm i -D eslint-plugin-unused-imports` | ESLint run | Per-file unused imports, autofix-able. | Single-file scope only. |
| ts-unused-exports | `npm i -D ts-unused-exports` | `npx ts-unused-exports tsconfig.json` | TS exports across the project. | Superseded by knip. |
| unimported | `npm i -D unimported` | `npx unimported` | Orphaned files. | Less accurate than knip. |

**Recommended pipeline:** `knip` for everything, `eslint-plugin-unused-imports` for per-file CI gating.

### Python

| Tool | Install | Run | Strengths | Limitations |
|---|---|---|---|---|
| **vulture** (canonical) | `pip install vulture` | `vulture . --min-confidence 60` | Cross-file unused functions, classes, imports, locals. Confidence-scored 0–100. Whitelist support. | False positives on dynamic dispatch (`getattr`, plugin systems). |
| ruff | `pip install ruff` | `ruff check --select F401,F841` | Per-file unused imports (F401) and locals (F841). Extremely fast. | **Per-file only.** Does not detect cross-file unused functions. (See ruff issue #872.) |
| deadcode | `pip install deadcode` | `deadcode .` | Newer alternative, lower false-positive claims. | Less mature than vulture. |
| unimport | `pip install unimport` | `unimport --check .` | Unused imports, autofix. | Imports only. |

**Recommended pipeline:** `vulture` for full audit, `ruff F401,F841` for per-commit hooks.

### Go

| Tool | Install | Run | Strengths | Limitations |
|---|---|---|---|---|
| **deadcode** (canonical) | `go install golang.org/x/tools/cmd/deadcode@latest` | `deadcode ./...` | **Sound** callgraph analysis — if it flags a function, it's truly unreachable. Official x/tools. | Requires `main` package as entry point. Slower on large codebases. |
| staticcheck | `go install honnef.co/go/tools/cmd/staticcheck@latest` | `staticcheck -checks U1000 ./...` | Unused vars, fields, funcs, types, methods, constants. Fast. | Slightly more false positives than `deadcode`. |
| deadmono | `go install github.com/arxeiss/deadmono@latest` | `deadmono ./services/...` | Designed for Go monorepos — intersects results across services. | Niche, less mature. |

**Recommended pipeline:** `deadcode` for unreachable functions, `staticcheck U1000` for everything else.

### Rust

| Tool | Install | Run | Strengths | Limitations |
|---|---|---|---|---|
| `rustc -W dead_code` | Built-in | `cargo +nightly rustc -- -W dead_code` | First-party, comprehensive. | Pollutes build output. |
| **cargo-machete** | `cargo install cargo-machete` | `cargo machete` | Fast (ripgrep + rayon) unused-deps scan. Supports ignore list. | Regex-based — false positives on proc macros. |
| cargo-udeps | `cargo install cargo-udeps --locked` | `cargo +nightly udeps` | Accurate compiler-output analysis. | Slower, requires nightly. |
| cargo-shear | `cargo install cargo-shear` | `cargo shear` | Modern alternative to machete. | Newer, less battle-tested. |

**Recommended pipeline:** `rustc dead_code` lint in CI + `cargo machete` for deps.

### Java / Kotlin

| Tool | Install | Run | Strengths | Limitations |
|---|---|---|---|---|
| **Qodana CLI** (canonical) | Docker pull `jetbrains/qodana-jvm-community` | `qodana scan --linter qodana-jvm-community` | Headless IntelliJ inspections including `UnusedDeclarationInspection` — best-in-class for JVM. | Heavy (Docker image). |
| detekt | Gradle plugin | `./gradlew detekt` | Fast Kotlin static analysis. | **Does NOT do cross-file dead code detection** — single-file scope. |
| bye-bye-dead-code | Gradle plugin | `./gradlew detectDeadCode` | Cross-module dead code for Gradle projects. | Kotlin/Android focused. |
| Codekvast | Java agent | Runtime instrumentation | Runtime detection — finds code never executed in production. | Requires production deployment. |

**Recommended pipeline:** Qodana for static, Codekvast for runtime confirmation.

### PHP

| Tool | Install | Run | Strengths | Limitations |
|---|---|---|---|---|
| **shipmonk/dead-code-detector** (canonical) | `composer require --dev shipmonk/dead-code-detector` | `vendor/bin/dead-code-detector` | Cross-project unused methods, constants, properties, enum cases. Knows Symfony, Doctrine, PHPUnit, Laravel, Twig. Detects dead cycles. | PHPStan extension (requires PHPStan). |
| PHPStan | `composer require --dev phpstan/phpstan` | `vendor/bin/phpstan analyse` | Built-in unused private methods/properties/constants. | Private members only without extensions. |
| Psalm | `composer require --dev vimeo/psalm` | `vendor/bin/psalm --find-dead-code` | Whole-project dead code, `@psalm-api` escape hatch. | Slower than PHPStan. |
| TomasVotruba/unused-public | `composer require --dev tomasvotruba/unused-public` | Run via PHPStan | Detects unused public methods. | Niche. |

**Recommended pipeline:** `shipmonk/dead-code-detector` (covers everything else).

### Ruby

| Tool | Install | Run | Strengths | Limitations |
|---|---|---|---|---|
| **debride** (canonical) | `gem install debride` | `debride .` | Static dead-method detection. | High false-positive rate due to Ruby's dynamism. |
| RuboCop | `gem install rubocop` | `rubocop --only Lint/UselessAssignment,Lint/UnusedMethodArgument,Lint/UnusedBlockArgument` | Per-file unused locals/args. | File-scoped. |
| coverband | `gem install coverband` | Runtime | Production code coverage — finds methods never called. | Requires runtime instrumentation. |
| fasterer | `gem install fasterer` | `fasterer` | Performance hints (sometimes flags dead code). | Off-topic. |

**Recommended pipeline:** `debride` for static + RuboCop `Lint/Unused*` for per-file.

### C# / .NET

| Tool | Install | Run | Strengths | Limitations |
|---|---|---|---|---|
| **Roslyn analyzers** (canonical) | Built-in | `dotnet format analyzers --diagnostics IDE0051 IDE0052 IDE0059 IDE0060` | First-party, fast, integrated with build. | IDE0051 = unused private member. IDE0052 = unread private member. IDE0059 = unused value. IDE0060 = unused parameter. |
| ReSharper InspectCode | JetBrains | `inspectcode MySolution.sln` | Comprehensive, including cross-project. | Commercial. |
| dotnet-outdated | `dotnet tool install -g dotnet-outdated-tool` | `dotnet outdated` | Outdated and unused packages. | Outdated focus. |

**Recommended pipeline:** Roslyn analyzers in CI + ReSharper for full audits.

---

## 2. Dead-Code Category Taxonomy

### Domain A: Code-Level (10 subtypes)

| Subtype | Description | Tools | Baseline confidence |
|---|---|---|---|
| `unused-import` | Imported symbol never referenced | ruff F401, knip, RuboCop | 95 |
| `unused-local` | Local variable assigned but never read | ruff F841, IDE0059, Lint/UselessAssignment | 95 |
| `unused-param` | Function parameter never used | IDE0060, Lint/UnusedMethodArgument | 80 (interface contracts may require it) |
| `unreachable-code` | Code after `return`/`raise`/`throw`/`break` | rustc, staticcheck SA4006, vulture | 100 |
| `unused-private-member` | Private class field/method/property never used internally | PHPStan, IDE0051, knip | 80 |
| `unused-export` | Module export never imported elsewhere | knip, vulture, ts-unused-exports | 65 |
| `unused-file` | Source file never imported, never auto-loaded | knip, unimported | 65 |
| `unused-react-component` | Component defined but never rendered | knip + JSX scan | 70 |
| `unused-api-route` | Route handler never called from a router/registry | manual + framework convention check | 60 |
| `commented-code-block` | >5 consecutive comment lines that resemble code | grep + heuristic | 75 |
| `orphaned-test-file` | Test file whose subject under test no longer exists | filename matching | 80 |

### Domain B: Dependency-Level (4 subtypes)

| Subtype | Description | Baseline confidence |
|---|---|---|
| `unused-runtime-dep` | Listed in `dependencies` but never imported | 80 |
| `unused-dev-dep` | Listed in `devDependencies` but never used in scripts/source | 70 |
| `duplicate-dep` | Same logical package installed multiple times | 90 |
| `lockfile-drift` | Lockfile out of sync with manifest | 95 |

### Domain C: Assets & Styles (3 subtypes)

| Subtype | Description | Baseline confidence |
|---|---|---|
| `unused-css-class` | CSS class defined but never used | 65 (dynamic class names common) |
| `unused-asset-file` | Image/font/svg with zero references | 75 |
| `legacy-purge-config` | Tailwind 2 `purge:` config in Tailwind 3+ project | 100 |

### Domain D: Infrastructure (6 subtypes)

| Subtype | Description | Baseline confidence | Notes |
|---|---|---|---|
| `unused-env-var` | Defined in `.env*` but never read in source | 75 | |
| `undefined-env-var-reference` | Read in source but never defined | 90 | Bug, not dead code |
| `dead-feature-flag` | Flag defined but never branched on | 70 | |
| `orphaned-migration` | Migration whose effect was reverted | 60 | Informational only |
| `db-column-candidate` | Column appears unused in source | 50 | **FLAG-ONLY — never propose deletion** |
| `unused-ci-job` | CI job that never triggers | 80 | |
| `dead-docker-stage` | Multi-stage Dockerfile stage never copied from | 90 | |

### Domain E: Documentation (2 subtypes)

| Subtype | Description | Baseline confidence |
|---|---|---|
| `broken-doc-link` | Markdown link to a path that doesn't exist | 100 |
| `stale-todo` | TODO/FIXME older than 12 months | 50 |

---

## 3. Confidence Scoring Rubric

### Baseline + Adjustments (Vulture-style 0–100)

Start with the baseline from §2. Apply additive/subtractive adjustments based on signals:

| Signal | Adjustment |
|---|---|
| Symbol marked `@public` / `@psalm-api` / exported in `__all__` / `pub use` | −30 |
| Symbol is in a test file | +10 (test code is leaf code) |
| Symbol has test coverage > 0 in `lcov.info` | −40 (if covered, it's used) |
| Symbol is in a `*.gen.*` or `__generated__` path | suppress entirely |
| Symbol is in a framework convention path (Phase 7 step 10) | −40 |
| File modified in the last 14 days (`git log`) | −20 (probably WIP) |
| Reflection/dynamic dispatch detected nearby | −30 |
| Symbol name appears in `*.json`, `*.yml`, `*.toml` config | −25 |
| Symbol name appears in any `*.md` documentation | −10 |
| Symbol matches a `.deadcode-ignore` pattern | suppress entirely |
| Sibling-package grep returned matches (monorepo) | −40 |

### Score Tiers

| Score | Tier | Action |
|---|---|---|
| 90–100 | CRITICAL | Top of action list. Safe to remove after one verification grep. |
| 70–89 | WARNING | Group into thematic batch. Manual review recommended. |
| 60–69 | SUGGESTION | List in appendix. Verify before acting. |
| <60 | DROPPED | Excluded from main report. List in "low-confidence" appendix only if verbose mode. |

### Phase Score Deductions

| Phase | Max | Deduction Rules |
|---|---|---|
| 2 — Code-level | 25 | Start at 25. −1 per CRITICAL finding (max −15). −0.5 per WARNING (max −10). |
| 3 — Dependencies | 15 | −2 per unused runtime dep, −1 per unused dev dep, −3 per duplicate, −5 for lockfile drift. |
| 4 — Assets & styles | 10 | −1 per unused asset file (max −5). −1 per legacy purge config. −0.5 per unused CSS class (max −4). |
| 5 — Infrastructure | 15 | −2 per dead feature flag, −1 per unused env var, −3 per dead Docker stage, −2 per unused CI job. **DB column candidates never deduct.** |
| 6 — Documentation | 5 | −0.5 per broken doc link (max −3). −1 per major commented-code block (>50 lines, max −2). |
| 7 — Verification | 20 | Start at 20. −5 if any finding lacks verification trail. −5 if framework convention check was skipped. −5 if `.deadcode-ignore` was not loaded. −5 if no Explore agent was used for any unused-export ≥70 confidence. |
| 8 — Reporting | 10 | −2 per missing report section (executive summary, stack table, tier groups, category groups, action list, JSON pointer, mermaid chart). |

Minimum score per phase: 0 (cannot go negative).

---

## 4. 10-Step Verification Protocol

For every Phase 2–6 finding, walk these steps and record evidence:

| # | Step | Tool / Command | What to look for |
|---|---|---|---|
| 1 | Full-repo grep | `Grep` tool, case-sensitive, then case-insensitive | Any reference matching the symbol name |
| 2 | Sibling-package grep (monorepo) | `Grep` across other workspace roots | Cross-package usage |
| 3 | Config-file scan | `Grep` in `*.{json,yml,yaml,toml,env*,config.*}` | Configuration referencing the symbol by name |
| 4 | Test-file scan | `Grep` in `**/*.{test,spec}.*`, `__tests__/**`, `tests/**`, `*_test.go`, `test_*.py` | Symbol used by test infrastructure |
| 5 | Documentation scan | `Grep` in `*.md`, `*.mdx`, `docs/**` | Symbol mentioned in docs (downgrades but doesn't disprove) |
| 6 | DI / route registration scan | Read `routes.*`, `*.module.ts`, `urls.py`, `web.php`, `routes.rb`, `Startup.cs` | Framework auto-registration |
| 7 | Dynamic-reference scan | `Grep` for `getattr\(`, `\[".*"\]`, `eval\(`, `Class\.forName`, `Activator\.CreateInstance`, `import\(` | String-based dispatch |
| 8 | Git blame age check | `Bash: git log --oneline -- <file> \| head -5` | If recently added, downgrade to suggestion |
| 9 | Coverage data check | Read `coverage/lcov.info`, `coverage.xml`, `.coverage` | Lines covered → not dead |
| 10 | Framework convention check | Match path against §5 patterns | File-conventional routes etc. |

**Stop early.** If steps 1–4 produce a clear "found" match, stop and downgrade the finding immediately.

**Spawn an Explore agent** for `unused-export` and `unused-file` findings with confidence ≥70 — these have the highest cost of false-positive deletion. Prompt the agent with the symbol name, file path, and the 10 verification steps, and ask for evidence either way.

---

## 5. False-Positive Patterns by Framework

### Next.js (App Router)

These files appear orphaned but are loaded by file convention:

```
app/**/page.{ts,tsx,js,jsx}            # Route page
app/**/layout.{ts,tsx,js,jsx}          # Layout
app/**/loading.{ts,tsx,js,jsx}         # Loading UI
app/**/error.{ts,tsx,js,jsx}           # Error boundary
app/**/not-found.{ts,tsx,js,jsx}       # 404 page
app/**/route.{ts,js}                   # API route handler
app/**/template.{ts,tsx,js,jsx}        # Template
app/**/default.{ts,tsx,js,jsx}         # Parallel route default
middleware.{ts,js}                     # Edge middleware
instrumentation.{ts,js}                # Telemetry
```

Convention exports `generateMetadata`, `generateStaticParams`, `generateViewport`, `revalidate`, `dynamic`, `runtime`, `preferredRegion` are framework hooks — never flag as unused exports.

### Next.js (Pages Router)

```
pages/**/*.{ts,tsx,js,jsx}             # Route pages
pages/api/**/*.{ts,js}                 # API routes
pages/_app.{ts,tsx,js,jsx}             # App wrapper
pages/_document.{ts,tsx,js,jsx}        # Document
pages/_error.{ts,tsx,js,jsx}           # Error page
```

Exports `getServerSideProps`, `getStaticProps`, `getStaticPaths`, `getInitialProps` are framework hooks.

### NestJS

Decorator-discovered: `@Controller()`, `@Injectable()`, `@Module()`, `@Resolver()`, `@WebSocketGateway()`, `@EventPattern()`, `@MessagePattern()`. Classes with these decorators are never unused even if no static import references them.

### Django

URL string dispatch: `urls.py` patterns reference views by string in some configurations. Template tags loaded via `{% load %}`. Management commands in `management/commands/*.py`. Migrations in `migrations/*.py`. App configs in `apps.py`.

### Flask

Blueprint registration is explicit but route handlers are referenced only by `@app.route` decorators — handlers appear unused to static analysis. CLI commands via `@click.command`.

### Rails / Zeitwerk autoloading

All files under `app/` are autoloaded by name. `app/models/`, `app/controllers/`, `app/jobs/`, `app/mailers/`, `app/services/`, `app/helpers/` — no explicit imports. Validation/callback methods (`before_save`, `after_create`) are referenced by symbol via DSL.

### Spring (Java)

Annotation scanning: `@Component`, `@Service`, `@Repository`, `@Controller`, `@RestController`, `@Configuration`, `@Bean`, `@Autowired`, `@EventListener`. Classes with these are auto-discovered.

### Laravel (PHP)

Route facades, Eloquent models loaded by string, Blade components in `app/View/Components/`, Service providers in `config/app.php`, Artisan commands in `app/Console/Commands/`.

### Symfony (PHP)

DI autowiring through service container. Controllers in `src/Controller/`. Event subscribers via `EventSubscriberInterface`.

### Go

Reflection via `reflect.ValueOf`. Plugin system via `plugin.Open`. Init functions (`func init()`) — automatically called, never unused. Test helpers in `*_test.go` files used only by other tests.

### Rust

Procedural macros that generate code referencing symbols not visible to static analysis. `#[no_mangle]` exported symbols. FFI exports. Build scripts (`build.rs`).

### React / React Server Components

Server actions (`'use server'`), client components (`'use client'`), `loading.tsx`, `error.tsx`, named exports consumed by file-convention frameworks (Next, Remix).

### Vue 3 / Nuxt

`pages/**` (Nuxt routing), `layouts/**`, `middleware/**`, `plugins/**`, `composables/**` (auto-imported), `components/**` (auto-imported), `<script setup>` macros (`defineProps`, `defineEmits`, `defineExpose`, `defineSlots`).

---

## 6. `.deadcode-ignore` File Format

Place `.deadcode-ignore` at the project root (or each workspace root in monorepos). Each line is a glob or symbol pattern with a justification comment.

### Syntax

```
# Comment line — ignored
<glob-pattern>      # <one-line justification>
<symbol-pattern>    # <one-line justification>
```

### Glob rules

- Standard `**`, `*`, `?`, `[abc]` patterns
- Leading `/` anchors to project root; otherwise matches anywhere
- Trailing `/` matches directories
- `!` prefix negates a previous match

### Symbol rules

- Bare identifiers match symbol names regardless of file
- `module.symbol` syntax matches dotted paths
- Glob characters allowed in symbols (`generate*`)

### Examples

```
# Framework conventions (Next.js)
app/**/page.tsx                     # Next.js file-conventional route
app/**/layout.tsx                   # Next.js layout
app/**/route.ts                     # Next.js API route handler
generateMetadata                    # Next.js metadata hook
generateStaticParams                # Next.js SSG hook

# Auto-discovered handlers
src/api/handlers/*.ts               # auto-loaded by route registry
src/jobs/**                         # discovered by job scheduler

# Public API surface
@acme/utils:*                       # public package exports — verify externally

# Generated code
src/__generated__/**                # codegen output
*.gen.ts                            # generator artefacts

# Historical migrations
src/migrations/**                   # historical, never directly imported

# Legal / SEO assets
public/legal/**                     # required by ToS

# Mobile-app legacy env vars
NEXT_PUBLIC_LEGACY_API_URL          # consumed by deprecated mobile v1.x
```

### Validation

- Every entry MUST have a justification comment. Findings without justification are reported as "unjustified ignore" warnings in Phase 8.
- Patterns matching zero findings are reported as "stale ignore" warnings.

---

## 7. Severity & Action Mapping

| Severity | Trigger | Recommended action | Where in report |
|---|---|---|---|
| **CRITICAL** | Confidence ≥ 90 AND ≥ 10 LOC saved | Top of action list. Single-grep verification, then delete. | Section 3a |
| **WARNING** | Confidence 70–89, OR confidence ≥ 90 with < 10 LOC | Group into thematic batch. Manual review before acting. | Section 3b |
| **SUGGESTION** | Confidence 60–69 | List in appendix. Investigate manually. | Section 3c |
| **FLAG-ONLY** | DB columns, dynamic dispatch, public API | Informational only — no action recommendation. | Section 3d |

### Thematic Batching for the Action List

Group findings into batches that can be reviewed and acted on independently:

1. **Imports & locals** (lowest risk) — bulk autofix candidate
2. **Unreachable code blocks**
3. **Unused private members**
4. **Unused exports & files** (highest cost of error)
5. **Unused dependencies**
6. **Asset & CSS cleanup**
7. **Infrastructure** (env vars, flags, CI)
8. **Documentation cleanup**

Order matters — batch 1 is the safest starting point and builds confidence in the audit's accuracy before tackling higher-risk batches.

---

## 8. Tool Output Normalisation

Each tool produces a different format. Normalise into the unified `findings-schema.json` shape (see `templates/findings-schema.json`).

### Knip JSON output

```json
{
  "files": ["src/orphan.ts"],
  "exports": [
    {"name": "unusedHelper", "filePath": "src/utils.ts", "line": 42}
  ],
  "dependencies": ["lodash"],
  "devDependencies": ["@types/foo"]
}
```

Map to:
- `files` → `unused-file` subtype
- `exports` → `unused-export` subtype
- `dependencies` → `unused-runtime-dep`
- `devDependencies` → `unused-dev-dep`

### Vulture text output

```
src/utils.py:42: unused function 'helper' (60% confidence)
src/utils.py:55: unused import 'os' (90% confidence)
```

Parse with regex `^([^:]+):(\d+): unused (\w+) '([^']+)' \((\d+)% confidence\)$`. Vulture's confidence becomes the baseline; apply §3 adjustments on top.

### Go deadcode output

```
src/main.go:42:6: unreachable function: helper
```

All `deadcode` findings are sound (callgraph-proven) → start at confidence 100.

### Cargo machete output

```
acme-app -- 1 unused dependency:
  serde_json
```

→ `unused-runtime-dep`, baseline 80.

### Roslyn IDE0051 output

```
src/Foo.cs(42,9): info IDE0051: Private member 'Foo.unused' is unused
```

→ `unused-private-member`, baseline 80.

### Normalised finding shape

```json
{
  "id": "DC-001",
  "file": "src/utils.ts",
  "line": 42,
  "column": 0,
  "symbol": "unusedHelper",
  "category": "code-level",
  "subtype": "unused-export",
  "confidence": 78,
  "tool": "knip",
  "raw_output_snippet": "src/utils.ts: unused export 'unusedHelper' (line 42)",
  "verification_evidence": [
    {"step": 1, "result": "no matches"},
    {"step": 2, "result": "no matches"},
    {"step": 6, "result": "not registered in any router"}
  ],
  "recommendation": "Safe to delete — single-batch removal with imports cleanup",
  "severity": "WARNING"
}
```

---

## 9. Quick Tool Install Commands

For `scripts/check-tools.sh` to print when a tool is missing.

| Language | Tool | Install command |
|---|---|---|
| JS/TS | knip | `npm install -D knip` |
| Python | vulture | `pip install vulture` |
| Python | ruff | `pip install ruff` |
| Go | deadcode | `go install golang.org/x/tools/cmd/deadcode@latest` |
| Go | staticcheck | `go install honnef.co/go/tools/cmd/staticcheck@latest` |
| Rust | cargo-machete | `cargo install cargo-machete` |
| Rust | cargo-udeps | `cargo install cargo-udeps --locked` |
| Java | qodana | `docker pull jetbrains/qodana-jvm-community` |
| PHP | shipmonk/dead-code-detector | `composer require --dev shipmonk/dead-code-detector` |
| PHP | phpstan | `composer require --dev phpstan/phpstan` |
| Ruby | debride | `gem install debride` |
| C# | (built-in) | `dotnet format analyzers --diagnostics IDE0051 IDE0052 IDE0059 IDE0060` |
