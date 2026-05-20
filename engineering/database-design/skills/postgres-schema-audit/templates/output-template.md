# Postgres Schema Audit — {{project_or_connection_label}}

| Field | Value |
|---|---|
| **Date** | {{DD/MM/YYYY}} |
| **Auditor** | Claude (postgres-schema-audit skill) |
| **Execution mode** | {{supabase-mcp / direct-postgres}} |
| **Project** (supabase-mcp only) | {{project_name}} ({{project_ref}}) |
| **Connection** (direct-postgres only) | {{connection_name}} — host=`{{host}}` db=`{{db}}` user=`{{user}}` sslmode=`{{sslmode}}` |
| **Postgres version** | {{server_version}} |
| **Schemas audited** | {{csv_list}} |
| **Schemas skipped** | {{csv_list_with_reason}} |
| **Tables examined** | {{n}} |
| **Columns examined** | {{n}} |
| **Foreign keys examined** | {{n}} |
| **Triggers / RPCs examined** | {{n}} / {{n}} |
| **RLS policies examined** | {{n}} |
| **Total findings** | {{n}} |
| **CRITICAL / HIGH / MEDIUM / LOW / INFO / FLAG-ONLY** | {{n}} / {{n}} / {{n}} / {{n}} / {{n}} / {{n}} |
| **Supabase advisors integrated** | {{yes — N hints / no — not available in direct-postgres mode}} |
| **`.db-design-ignore` loaded** | {{yes — N entries / no}} |
| **Completeness** | {{X}}/100 |
| **Tier** | {{FULLY AUDITED / MOSTLY AUDITED / PARTIALLY AUDITED / INSUFFICIENT}} |

> **Completeness** measures how thoroughly the skill traced the database — it is NOT a quality grade. A clean schema and a messy schema can both score 100%. System quality is captured in §7 Risk Register.

> **Render rules:** include only ONE of the two identity rows ("Project" or "Connection") — the other is omitted entirely. Never include both. Never include an empty row. Password, connection string, and any other credential material must never appear in this header or anywhere else in the report.

---

## 1. Executive Summary

{{2-3 paragraphs describing the overall shape of the database surface: schema topology, dominant design patterns, relationship density, most impactful findings, and cross-schema issues.}}

**Top findings by blast radius (most tables affected):**
1. {{DB-NNN}} — {{subtype}} — affects {{n}} tables
2. {{DB-NNN}} — {{subtype}} — affects {{n}} tables
3. {{DB-NNN}} — {{subtype}} — affects {{n}} tables

**Top risks (highest cost-of-error):**
1. {{severity}} — {{subtype}} — {{target}}
2. {{severity}} — {{subtype}} — {{target}}
3. {{severity}} — {{subtype}} — {{target}}

**Top relationship improvements:**
1. {{DB-NNN}} — {{from.table.col → to.table.col}} — {{reason}}
2. {{DB-NNN}} — {{from.table.col → to.table.col}} — {{reason}}

---

## 2. Schemas Overview

| Schema | Tables | Columns | FKs | Triggers | RPCs | Policies | RLS-enabled | Findings | Status |
|---|---|---|---|---|---|---|---|---|---|
| {{schema}} | {{n}} | {{n}} | {{n}} | {{n}} | {{n}} | {{n}} | {{n}} | {{n}} | {{ok / partial / failed}} |

If any schema sub-agent returned `partial` or `failed`, the limitation reasons are listed in the appendix.

---

## 3. Findings by Severity

> Each finding carries a subtype code (A1–J5) mapping to the taxonomy in `reference.md` §3, and a category letter (A–J).

### 3a. CRITICAL

| ID | Target | Category | Subtype | Evidence | Remediation |
|---|---|---|---|---|---|
| DB-NNN | {{schema.table.column}} | {{letter}} | {{code}} | {{one-liner}} | See {{DB-NNN}} detail block |

### 3b. HIGH

| ID | Target | Category | Subtype | Evidence | Remediation |
|---|---|---|---|---|---|
| DB-NNN | {{target}} | {{letter}} | {{code}} | {{one-liner}} | See {{DB-NNN}} detail block |

### 3c. MEDIUM

| ID | Target | Category | Subtype | Evidence | Remediation |
|---|---|---|---|---|---|
| DB-NNN | {{target}} | {{letter}} | {{code}} | {{one-liner}} | See {{DB-NNN}} detail block |

### 3d. LOW / INFO

| ID | Target | Category | Subtype | Evidence |
|---|---|---|---|---|
| DB-NNN | {{target}} | {{letter}} | {{code}} | {{one-liner}} |

### 3e. FLAG-ONLY — MANUAL REVIEW REQUIRED — DO NOT AUTO-DELETE

| ID | Target | Subtype | Why flagged | Next step |
|---|---|---|---|---|
| DB-NNN | {{target}} | {{code}} | {{reason}} | {{manual next step}} |

---

## 4. Findings by Category

For each of categories A–J (and CROSS), show a table grouping findings by subtype with representative examples.

### 4a. Keys & Relationships (A)

| Subtype | Count | Example | Severity mix |
|---|---|---|---|
| A1 missing-primary-key | {{n}} | {{DB-NNN}} | {{H}} |
| A3 fk-shaped-no-constraint | {{n}} | {{DB-NNN}} | {{H}} |
| A4 fk-column-no-index | {{n}} | {{DB-NNN}} | {{H}} |
| A5 fk-wrong-type | {{n}} | {{DB-NNN}} | {{C}} |
| ... | | | |

[Repeat for B through J]

---

## 5. Per-Finding Detail Blocks (Top 25)

Ordered by severity, then blast radius, then confidence.

### DB-001 — {{subtype_label}}

| Field | Value |
|---|---|
| Target | `{{schema}}.{{table}}.{{column}}` |
| Category | {{letter}} |
| Subtype | {{code}} |
| Severity | {{CRITICAL / HIGH / MEDIUM / LOW / INFO / FLAG-ONLY}} |
| Confidence | {{n}} |
| Evidence source | {{pg_catalog / information_schema / supabase-advisor / data-sample}} |
| Supabase advisor code | {{code or 'n/a'}} |
| Crosslinks | {{DB-NNN, DB-NNN}} |

**Description:** {{human-readable explanation of the finding}}

**Evidence:**
```sql
{{SQL that produced the finding}}
```

```
{{returned rows or row count}}
```

**Suggested remediation:**

```sql
{{SQL from §6 of reference.md, with -- MANUAL REVIEW REQUIRED header}}
```

**Rollback:** {{rollback strategy or note}}

**Severity adjustments applied:**
- {{signal}} → {{direction}}

---

[Repeat for top 25 findings]

---

## 6. Cross-Schema Analysis

### 6a. Cross-schema foreign keys

| From | To | FK name | Direction notes |
|---|---|---|---|
| {{schema.table.col}} | {{schema.table.col}} | {{fk_name}} | {{expected / unusual}} |

### 6b. Duplicate enum definitions

| Enum name | Schemas | Label overlap |
|---|---|---|
| {{name}} | {{csv}} | {{%}} |

### 6c. Shared lookup candidates

| Table | Schemas | Suggestion |
|---|---|---|
| {{name}} | {{csv}} | Consolidate into `public.{{name}}` |

---

## 7. Risk Register

| ID | Severity | Category | Target | Evidence (one-line) | Action |
|---|---|---|---|---|---|
| DB-001 | {{severity}} | {{letter}} | {{target}} | {{evidence summary}} | {{action}} |

---

## 8. ER Diagram (current state)

```mermaid
erDiagram
  {{table_1}} ||--o{ {{table_2}} : {{relationship}}
  {{table_1}} ||--|| {{table_3}} : {{relationship}}
  {{table_2}} }o--o{ {{table_4}} : {{m_to_n}}
  %% Relationships with no FK constraint are rendered with dashed lines when possible
```

---

## 9. Risk Heatmap

### 9a. Findings by category

```mermaid
pie title Findings by Category
  "A Keys & Relationships" : {{n}}
  "B Data Types" : {{n}}
  "C Constraints" : {{n}}
  "D Arrays & JSONB" : {{n}}
  "E Indexes" : {{n}}
  "F Triggers & RPCs" : {{n}}
  "G RLS" : {{n}}
  "H Naming" : {{n}}
  "I Timestamps" : {{n}}
  "J Orphans" : {{n}}
  "CROSS" : {{n}}
```

### 9b. Findings by severity

```mermaid
pie title Findings by Severity
  "CRITICAL" : {{n}}
  "HIGH" : {{n}}
  "MEDIUM" : {{n}}
  "LOW" : {{n}}
  "INFO" : {{n}}
  "FLAG-ONLY" : {{n}}
```

### 9c. Findings per schema

```mermaid
pie title Findings by Schema
  "{{schema_A}}" : {{n}}
  "{{schema_B}}" : {{n}}
  "{{schema_C}}" : {{n}}
```

---

## 10. Prioritised Action Batches

Group findings into batches that can be reviewed and applied independently. **Start with Batch 1** — it is the lowest-risk and builds confidence in the audit's accuracy.

### Batch 1 — Column comments & documentation (LOWEST RISK)
- {{n}} findings (H5, H6, F10)
- No data impact. Purely ergonomic.

### Batch 2 — Missing indexes
- {{n}} findings (A4/E1, E4)
- Use `CREATE INDEX CONCURRENTLY`. No write downtime.

### Batch 3 — NOT NULL and CHECK constraints
- {{n}} findings (C1, C4)
- Use `NOT VALID` pattern followed by `VALIDATE CONSTRAINT`.

### Batch 4 — Missing foreign keys
- {{n}} findings (A3)
- `NOT VALID` + `VALIDATE`. Add the supporting index in same batch.

### Batch 5 — Default values and updated_at triggers
- {{n}} findings (C2, F1, I5)
- Trivial ALTERs and CREATE TRIGGER.

### Batch 6 — RLS hardening
- {{n}} findings (G1, G2, G3, G4, G5, G6)
- **Test thoroughly in a non-production environment first.**

### Batch 7 — Type changes (HIGHEST RISK)
- {{n}} findings (A5, B1, B3, B4, B5)
- Two-phase migrations. Plan downtime or write paths. Back up first.

### Batch 8 — Function hardening
- {{n}} findings (F2, F8)
- `ALTER FUNCTION ... SET search_path = ''`. Low risk but verify each function still works.

### FLAG-ONLY — Not actioned by this skill
- {{n}} findings — require human decision (table drops, column drops, empty table removal)

---

## 11. Suppressed Findings

| Source | Count |
|---|---|
| `.db-design-ignore` matches | {{n}} |
| Severity below INFO threshold | {{n}} |
| Sub-agent confidence < 60 | {{n}} |
| Supabase advisor false-positive (tagged) | {{n}} |

**Stale ignore patterns** (matched zero findings in this run):
- {{pattern}}
- {{pattern}}

---

## 12. Sub-Agent Limitations

{{One row per phase/category/schema that the sub-agent couldn't fully audit. E.g., "schema X: pg_stat_user_indexes permission denied — E3 skipped"}}

---

## 13. JSON Sidecar

Machine-readable findings written to `database-design-audit.json`. Shape follows `templates/findings-schema.json`. Example:

```json
{
  "id": "DB-001",
  "category": "A",
  "subtype": "A3",
  "subtype_label": "fk-shaped-no-constraint",
  "severity": "HIGH",
  "target": {
    "kind": "column",
    "schema": "operations",
    "table": "tasks",
    "column": "workspace_id"
  },
  "evidence": {
    "sql": "SELECT ... FROM information_schema.columns ...",
    "row_count": 1,
    "evidence_source": "information_schema"
  },
  "description": "...",
  "remediation_sql": "ALTER TABLE ... NOT VALID; ALTER TABLE ... VALIDATE CONSTRAINT ...",
  "confidence": 95
}
```

---

## 14. Draft Migrations

Every CRITICAL, HIGH, and MEDIUM finding emits SQL into `migrations-suggested.sql`. Every statement is commented with its finding ID and a `MANUAL REVIEW REQUIRED — DO NOT APPLY BLINDLY` banner. Destructive operations (DROP TABLE, DROP COLUMN) are always commented out and accompanied by an expanded safety checklist.

See `migrations-suggested.sql` for the full set.
