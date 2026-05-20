# Dead Code Audit — {{project_name}}

| Field | Value |
|---|---|
| **Date** | {{DD/MM/YYYY}} |
| **Auditor** | Claude (dead-code-audit skill) |
| **Stack** | {{detected_languages_csv}} |
| **Total findings** | {{N}} |
| **High-confidence (≥90)** | {{N}} |
| **Estimated LOC savings** | {{N}} |
| **Total score** | {{X}}/100 |
| **Verdict** | {{CLEAN / MODERATE DEBT / HIGH DEBT / CRITICAL DEBT}} |

---

## 1. Executive Summary

{{2-3 paragraphs describing the overall state of the codebase, the most impactful findings, and the most important risks. Top 3 wins and top 3 risks in bullet form.}}

**Top wins (highest impact, lowest risk):**
1. {{finding-id}} — {{description}}
2. {{finding-id}} — {{description}}
3. {{finding-id}} — {{description}}

**Top risks (highest cost-of-error):**
1. {{description}}
2. {{description}}
3. {{description}}

---

## 2. Stack & Tooling

| Language | Files | Tool | Version | Status |
|---|---|---|---|---|
| {{lang}} | {{count}} | {{tool}} | {{version}} | {{ran / skipped — reason}} |

**Skipped tools:** {{list any tools that could not run, with reason}}

**`.deadcode-ignore` loaded:** {{yes — N entries / no}}

**Excluded paths (generated code, vendor, etc.):** {{list}}

---

## 3. Findings by Confidence Tier

### 3a. CRITICAL — High confidence (90–100%)

| ID | File | Line | Symbol | Subtype | Confidence | LOC | Action |
|---|---|---|---|---|---|---|---|
| DC-001 | {{path}} | {{n}} | {{name}} | {{subtype}} | {{n}} | {{n}} | {{batch}} |

### 3b. WARNING — Medium confidence (70–89%)

| ID | File | Line | Symbol | Subtype | Confidence | LOC | Action |
|---|---|---|---|---|---|---|---|
| DC-NNN | {{path}} | {{n}} | {{name}} | {{subtype}} | {{n}} | {{n}} | {{batch}} |

### 3c. SUGGESTION — Low confidence (60–69%)

| ID | File | Line | Symbol | Subtype | Confidence | LOC | Notes |
|---|---|---|---|---|---|---|---|
| DC-NNN | {{path}} | {{n}} | {{name}} | {{subtype}} | {{n}} | {{n}} | {{notes}} |

### 3d. FLAG-ONLY — DB columns and dynamic-dispatch suspects

> **MANUAL REVIEW REQUIRED — DO NOT AUTO-DELETE**

| ID | Object | Subtype | Reason flagged | Recommended next step |
|---|---|---|---|---|
| DC-NNN | {{table.column or symbol}} | {{db-column-candidate / dynamic-dispatch-risk}} | {{reason}} | {{next step}} |

---

## 4. Findings by Category

### 4a. Code-Level (Phase 2)

**Score: {{X}}/25**

| Subtype | Count | Example | LOC saved |
|---|---|---|---|
| unused-import | {{n}} | DC-NNN | {{n}} |
| unused-local | {{n}} | DC-NNN | {{n}} |
| unreachable-code | {{n}} | DC-NNN | {{n}} |
| unused-private-member | {{n}} | DC-NNN | {{n}} |
| unused-export | {{n}} | DC-NNN | {{n}} |
| unused-file | {{n}} | DC-NNN | {{n}} |
| unused-react-component | {{n}} | DC-NNN | {{n}} |
| unused-api-route | {{n}} | DC-NNN | {{n}} |
| commented-code-block | {{n}} | DC-NNN | {{n}} |
| orphaned-test-file | {{n}} | DC-NNN | {{n}} |

### 4b. Dependency-Level (Phase 3)

**Score: {{X}}/15**

| Subtype | Count | Examples |
|---|---|---|
| unused-runtime-dep | {{n}} | {{package names}} |
| unused-dev-dep | {{n}} | {{package names}} |
| duplicate-dep | {{n}} | {{package names}} |
| lockfile-drift | {{n}} | {{details}} |

### 4c. Assets & Styles (Phase 4)

**Score: {{X}}/10**

| Subtype | Count | Examples |
|---|---|---|
| unused-css-class | {{n}} | {{class names}} |
| unused-asset-file | {{n}} | {{file paths}} |
| legacy-purge-config | {{n}} | {{file path}} |

### 4d. Infrastructure (Phase 5)

**Score: {{X}}/15**

| Subtype | Count | Examples |
|---|---|---|
| unused-env-var | {{n}} | {{var names}} |
| undefined-env-var-reference | {{n}} | {{var names}} |
| dead-feature-flag | {{n}} | {{flag keys}} |
| orphaned-migration | {{n}} | {{file paths}} |
| db-column-candidate | {{n}} | **FLAG-ONLY** {{table.column}} |
| unused-ci-job | {{n}} | {{job names}} |
| dead-docker-stage | {{n}} | {{stage names}} |

### 4e. Documentation (Phase 6)

**Score: {{X}}/5**

| Subtype | Count | Examples |
|---|---|---|
| broken-doc-link | {{n}} | {{links}} |
| stale-todo | {{n}} | {{file:line}} |

---

## 5. Detail Blocks (Top 20 Findings)

### DC-001 — {{symbol_name}}

| Field | Value |
|---|---|
| File | {{file_path}}:{{line}} |
| Subtype | {{subtype}} |
| Confidence | {{n}} |
| Tool | {{tool name}} |
| Severity | {{CRITICAL / WARNING / SUGGESTION / FLAG-ONLY}} |
| LOC saved | {{n}} |

**Tool output:**
```
{{raw tool output snippet}}
```

**Verification trail:**
1. Full-repo grep: {{result}}
2. Sibling-package grep: {{result}}
3. Config-file scan: {{result}}
4. Test-file scan: {{result}}
5. Documentation scan: {{result}}
6. DI / route registration scan: {{result}}
7. Dynamic-reference scan: {{result}}
8. Git blame age: {{date — N days}}
9. Coverage check: {{result}}
10. Framework convention check: {{result}}

**Recommendation:** {{action}}

**Rollback note:** {{git revert command if user acts on this}}

---

[Repeat for top 20 findings]

---

## 6. Suggested `.deadcode-ignore` Entries

Based on findings that look like false positives, consider adding these to `.deadcode-ignore`:

```
# Framework conventions
{{pattern}}                # {{justification}}

# Auto-discovered handlers
{{pattern}}                # {{justification}}

# Public API surface
{{pattern}}                # {{justification}}
```

---

## 7. Prioritised Action List

Findings are grouped into thematic batches. **Start with batch 1** — it's the lowest-risk and builds confidence in the audit's accuracy.

### Batch 1 — Imports & Locals (lowest risk)
- {{N}} findings, {{N}} LOC
- {{summary}}

### Batch 2 — Unreachable Code Blocks
- {{N}} findings, {{N}} LOC

### Batch 3 — Unused Private Members
- {{N}} findings, {{N}} LOC

### Batch 4 — Unused Exports & Files
- {{N}} findings, {{N}} LOC
- **Higher risk** — verify each finding manually

### Batch 5 — Unused Dependencies
- {{N}} findings
- Removing deps requires `npm install` / `pip uninstall` / `cargo update`

### Batch 6 — Asset & CSS Cleanup
- {{N}} findings, {{N}} files

### Batch 7 — Infrastructure (env vars, flags, CI)
- {{N}} findings

### Batch 8 — Documentation Cleanup
- {{N}} findings

---

## 8. Visual Summary

```mermaid
pie title Findings by Category
    "Code-level" : {{n}}
    "Dependencies" : {{n}}
    "Assets & styles" : {{n}}
    "Infrastructure" : {{n}}
    "Documentation" : {{n}}
```

```mermaid
pie title Findings by Confidence Tier
    "CRITICAL (90-100)" : {{n}}
    "WARNING (70-89)" : {{n}}
    "SUGGESTION (60-69)" : {{n}}
    "FLAG-ONLY" : {{n}}
```

```mermaid
pie title Estimated LOC Savings by Batch
    "Imports & locals" : {{n}}
    "Unreachable" : {{n}}
    "Private members" : {{n}}
    "Exports & files" : {{n}}
    "CSS & assets" : {{n}}
```

---

## 9. JSON Sidecar

A machine-readable copy of all findings is recommended for CI gating and tracking. The JSON shape follows `templates/findings-schema.json`. To generate it, ask the skill to output a JSON sidecar file alongside this report.

Example finding:
```json
{
  "id": "DC-001",
  "file": "src/utils.ts",
  "line": 42,
  "symbol": "unusedHelper",
  "category": "code-level",
  "subtype": "unused-export",
  "confidence": 92,
  "tool": "knip",
  "severity": "CRITICAL",
  "verification_evidence": [
    {"step": 1, "result": "no matches"},
    {"step": 6, "result": "not registered in any router"}
  ],
  "recommendation": "Safe to delete in batch 4"
}
```

---

## 10. Suppressed Findings

| Source | Count |
|---|---|
| `.deadcode-ignore` matches | {{n}} |
| Generated code paths | {{n}} |
| Confidence < 60 (dropped) | {{n}} |
| Framework convention paths | {{n}} |

**Total suppressed:** {{n}}
