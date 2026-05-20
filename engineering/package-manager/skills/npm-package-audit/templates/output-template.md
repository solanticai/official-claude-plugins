# npm Package Audit Report

## Summary

| Field | Value |
|-------|-------|
| **Package** | {{name}}@{{version}} |
| **Date** | {{YYYY-MM-DD}} |
| **Overall Score** | {{X}}/100 |
| **Overall Verdict** | {{PASS / FAIL / PASS WITH WARNINGS / CONDITIONAL}} |
| **Critical Issues** | {{count}} |
| **Warnings** | {{count}} |
| **Suggestions** | {{count}} |

## Package Identity

| Field | Value |
|-------|-------|
| Name | {{name}} |
| Version | {{version}} |
| Description | {{description}} |
| License | {{license}} |
| Build Tool | {{tsup / rollup / esbuild / tsc / vite}} |
| Test Framework | {{vitest / jest / mocha / none}} |
| CI/CD | {{GitHub Actions / GitLab CI / none}} |

---

## Phase Results

### Phase 1: Package Discovery -- CONTEXT
[Package identity and tech stack summary]

### Phase 2: package.json Quality -- {{X}}/15 -- {{PASS/FAIL}}

| Check | Status | Details |
|-------|--------|---------|
| name | {{PASS/FAIL}} | {{details}} |
| version | {{PASS/FAIL}} | {{details}} |
| description | {{PASS/FAIL}} | {{details}} |
| license | {{PASS/FAIL}} | {{details}} |
| author | {{PASS/FAIL}} | {{details}} |
| repository | {{PASS/FAIL}} | {{details}} |
| homepage | {{PASS/FAIL}} | {{details}} |
| bugs | {{PASS/FAIL}} | {{details}} |
| keywords | {{PASS/FAIL}} | {{details}} |
| engines | {{PASS/FAIL}} | {{details}} |
| files | {{PASS/FAIL}} | {{details}} |
| type | {{PASS/FAIL}} | {{details}} |
| sideEffects | {{PASS/FAIL}} | {{details}} |
| packageManager | {{PASS/FAIL}} | {{details}} |

### Phase 3: Exports Map & Entry Points -- {{X}}/15 -- {{PASS/FAIL}}

| Export Path | Types | Import | Require | Status |
|-------------|-------|--------|---------|--------|
| "." | {{file}} | {{file}} | {{file}} | {{PASS/FAIL}} |
| "./cli" | {{file}} | {{file}} | {{file}} | {{PASS/FAIL}} |
| "./utils" | {{file}} | {{file}} | {{file}} | {{PASS/FAIL}} |
| "./package.json" | -- | {{file}} | {{file}} | {{PASS/FAIL}} |

### Phase 4: Build Configuration -- {{X}}/15 -- {{PASS/FAIL}}

| Check | Status | Details |
|-------|--------|---------|
| Dual CJS/ESM | {{PASS/FAIL}} | {{details}} |
| Source maps | {{PASS/FAIL}} | {{details}} |
| Type declarations | {{PASS/FAIL}} | {{details}} |
| Clean builds | {{PASS/FAIL}} | {{details}} |
| Tree shaking | {{PASS/FAIL}} | {{details}} |
| Bundle size | {{PASS/FAIL}} | {{size in KB}} |
| External deps | {{PASS/FAIL}} | {{details}} |
| Build reproducibility | {{PASS/FAIL}} | {{details}} |

### Phase 5: Type Declarations -- {{X}}/10 -- {{PASS/FAIL}}

| Check | Status | Details |
|-------|--------|---------|
| tsc --noEmit | {{PASS/FAIL}} | {{error count}} errors |
| .d.ts completeness | {{PASS/FAIL}} | {{details}} |
| No `any` in public API | {{PASS/FAIL}} | {{count}} occurrences |
| Strict mode | {{PASS/FAIL}} | {{details}} |
| Export type coverage | {{PASS/FAIL}} | {{X}}% of exports typed |

### Phase 6: Testing & Coverage -- {{X}}/10 -- {{PASS/FAIL}}

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Lines | {{X}}% | 80% | {{PASS/FAIL}} |
| Branches | {{X}}% | 70% | {{PASS/FAIL}} |
| Functions | {{X}}% | 75% | {{PASS/FAIL}} |
| Statements | {{X}}% | 80% | {{PASS/FAIL}} |

| Check | Status | Details |
|-------|--------|---------|
| Test suite passes | {{PASS/FAIL}} | {{pass}}/{{total}} tests |
| No skipped tests | {{PASS/FAIL}} | {{count}} skipped |
| Integration tests | {{PASS/FAIL}} | {{present/missing}} |

### Phase 7: Cross-OS Compatibility -- {{X}}/10 -- {{PASS/FAIL}}

| Check | Status | Details |
|-------|--------|---------|
| Path separators | {{PASS/FAIL}} | {{count}} hardcoded paths found |
| Line endings | {{PASS/FAIL}} | .gitattributes {{present/missing}} |
| Bin shebangs | {{PASS/FAIL}} | {{details}} |
| CI OS matrix | {{PASS/FAIL}} | {{os list}} |
| path.join/resolve usage | {{PASS/FAIL}} | {{details}} |
| process.platform guards | {{PASS/FAIL}} | {{details}} |
| fs case sensitivity | {{PASS/FAIL}} | {{details}} |

### Phase 8: Security & Supply Chain -- {{X}}/10 -- {{PASS/FAIL}}

| Severity | Count |
|----------|-------|
| Critical | {{count}} |
| High | {{count}} |
| Moderate | {{count}} |
| Low | {{count}} |

| Check | Status | Details |
|-------|--------|---------|
| npm audit | {{PASS/FAIL}} | {{details}} |
| No install scripts | {{PASS/FAIL}} | {{details}} |
| Lock file | {{PASS/FAIL}} | {{present/missing}} |
| Dependency count | {{PASS/FAIL}} | {{count}} direct, {{count}} transitive |
| Known CVEs | {{PASS/FAIL}} | {{details}} |
| .npmrc safety | {{PASS/FAIL}} | {{details}} |

### Phase 9: Publishing & CI/CD -- {{X}}/10 -- {{PASS/FAIL}}

| Check | Status | Details |
|-------|--------|---------|
| publishConfig | {{PASS/FAIL}} | {{details}} |
| prepublishOnly | {{PASS/FAIL}} | {{details}} |
| CI publish workflow | {{PASS/FAIL}} | {{details}} |
| Provenance | {{PASS/FAIL}} | {{details}} |
| Version tagging | {{PASS/FAIL}} | {{details}} |
| Branch protection | {{PASS/FAIL}} | {{details}} |
| Dry run tested | {{PASS/FAIL}} | {{details}} |
| .npmignore / files | {{PASS/FAIL}} | {{details}} |

### Phase 10: Documentation -- {{X}}/5 -- {{PASS/FAIL}}

| Document | Status | Notes |
|----------|--------|-------|
| README.md | {{PASS/FAIL}} | {{sections present/missing}} |
| CONTRIBUTING.md | {{PASS/FAIL}} | {{present/missing}} |
| CHANGELOG.md | {{PASS/FAIL}} | {{present/missing}} |
| LICENSE | {{PASS/FAIL}} | {{matches package.json}} |
| SECURITY.md | {{PASS/FAIL}} | {{present/missing}} |

---

## Prioritised Action List

### Critical (must fix before publish)
1. {{finding with file:line}}

### Warnings (should fix)
1. {{finding with file:line}}

### Suggestions (nice to have)
1. {{finding}}

---

## Visual Summary

```mermaid
pie title Issues by Severity
    "Critical" : {{count}}
    "Warning" : {{count}}
    "Suggestion" : {{count}}
```

```mermaid
pie title Score Distribution by Phase
    "package.json" : {{score}}
    "Exports Map" : {{score}}
    "Build Config" : {{score}}
    "Type Declarations" : {{score}}
    "Testing" : {{score}}
    "Cross-OS" : {{score}}
    "Security" : {{score}}
    "Publishing" : {{score}}
    "Documentation" : {{score}}
```
