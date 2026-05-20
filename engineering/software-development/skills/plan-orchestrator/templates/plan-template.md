# Plan Orchestrator — Consolidated Plan

| Field | Value |
|---|---|
| **Generated** | {{YYYY-MM-DD HH:MM}} |
| **Target** | `{{target}}` |
| **Tasks** | {{N}} |
| **Domains routed** | {{N}} |
| **Coverage** | {{X}}% (missing: {{N}}, spurious: {{N}}) |

---

## 1. Task Coverage

| ID | Status | Domains | Original task |
|---|---|---|---|
| T1 | 🟢 covered | frontend | {{verbatim bullet}} |
| T2 | 🟢 covered | database, backend | {{verbatim bullet}} |
| T3 | 🔴 missing | backend | {{verbatim bullet}} |

Status legend:
- 🟢 covered — at least one agent returned a section for this ID
- 🟡 duplicate — multiple agents addressed the same ID (cross-cutting; deduped below)
- 🔴 missing — no agent returned a section after sweeper rounds; surfaced in §6
- ⚪ unknown — coverage script did not classify (should not occur in a clean run)

---

## 2. Per-Task Plan

### T1 — {{original bullet text}}

**Domains:** {{...}}
**Contributing agents:** {{count, only shown if >1}}

{{verbatim section body from the contributing agent(s), preserving
  Investigation summary / Evidence / Proposed steps / Risks / Verification}}

### T2 — {{original bullet text}}

{{...}}

---

## 3. Aggregated Change Set by File

Files referenced across the per-task plans, sorted alphabetically. If multiple tasks touch the same file, batch the changes.

| File | Tasks |
|---|---|
| `apps/web/src/middleware.ts` | T1, T4 |
| `supabase/migrations/20260425_add_currency.sql` | T2 |

---

## 4. Cross-Cutting Concerns

Tasks that span multiple domains. Coordinate the relevant agents' recommendations in your execution.

- **T2** (database, backend) — {{...}}
- **T7** (security, infrastructure) — {{...}}

---

## 5. Suggested Execution Order

Apply changes in this order to minimise rework: schema → infra → security → backend → frontend → tests → docs.

1. **Database** — T2
2. **Infrastructure** — T5
3. **Security** — T7
4. **Backend** — T3, T6
5. **Frontend** — T1, T4
6. **Testing** — T8
7. **Documentation** — T9

---

## 6. Unresolved Items

These task IDs did not receive coverage from any sub-agent, even after sweeper rounds. Investigate manually before acting on the plan.

- **T3** — {{original bullet}}
