# Mermaid Diagram Templates

The `write-path-mapping` skill emits four Mermaid diagrams into the final report. This file shows the structural skeleton of each. `scripts/mermaid-render.py` fills them in from `write-path-map.json`.

---

## A. System Write Flowchart (`flowchart TD`)

Single-page overview of every write path in the project. Subgraphs per domain. Entry-point nodes colored by the highest-severity risk attached to them. Persistence-target nodes drawn with shape-based semantics.

**Node shapes:**

| Shape | Mermaid | Meaning |
|---|---|---|
| `[(table)]` | `node[(label)]` | SQL table |
| `[[cache]]` | `node[[label]]` | cache / in-memory store |
| `((api))` | `node((label))` | external API |
| `[\file/]` | `node[\label/]` | file / object storage |
| `{{queue}}` | `node{{label}}` | queue or topic |
| `((event))` | `node((label))` | domain event |
| `{auth}` | `node{label}` | decision / auth gate |

**Color classes:**

```mermaid
flowchart TD
    classDef critical fill:#ff6b6b,stroke:#c00,color:#fff;
    classDef high fill:#ffa94d,stroke:#d97706,color:#fff;
    classDef medium fill:#ffe066,stroke:#d4a017,color:#333;
    classDef info fill:#a5d8ff,stroke:#1971c2,color:#0b3d66;
    classDef ok fill:#b2f2bb,stroke:#2f9e44,color:#0b3d1e;
```

**Skeleton:**

```mermaid
flowchart TD
    classDef critical fill:#ff6b6b,stroke:#c00,color:#fff;
    classDef high fill:#ffa94d,stroke:#d97706,color:#fff;
    classDef medium fill:#ffe066,stroke:#d4a017,color:#333;
    classDef info fill:#a5d8ff,stroke:#1971c2,color:#0b3d66;
    classDef ok fill:#b2f2bb,stroke:#2f9e44,color:#0b3d1e;

    subgraph dom_app["app"]
        e_WP001["POST /api/tasks"]
        e_WP002["POST /api/contracts"]
    end
    subgraph dom_supabase["supabase/functions"]
        e_WP003["apply-workspace-template"]
    end

    g_WP001{"auth"}
    e_WP001 --> g_WP001
    t_tasks[("operations.tasks")]
    t_cache[["redis:tasks:*"]]
    g_WP001 --> t_tasks
    g_WP001 --> t_cache

    class e_WP001 ok;
    class e_WP002 high;
    class e_WP003 critical;
```

---

## B. Per-Endpoint Sequence Diagram (`sequenceDiagram`)

One per top-20 endpoint. Shows the full stack from actor to persistence plus downstream effects.

**Skeleton:**

```mermaid
sequenceDiagram
    title POST /api/tasks
    actor U as User
    participant MW as middleware
    participant R as route.ts POST
    participant V as Zod
    participant S as tasks service
    participant DB as Supabase (operations.tasks)
    participant C as Redis cache
    participant T as trigger tasks_after_insert
    participant AL as operations.audit_log

    U->>MW: POST /api/tasks {payload}
    MW->>MW: authMiddleware
    MW->>R: forward (user.id in ctx)
    R->>V: CreateTaskSchema.parse(input)
    V-->>R: parsed
    R->>S: createTask(user, input)
    S->>DB: insert into operations.tasks
    DB-->>T: fires trigger
    T->>AL: insert into audit_log
    S->>C: DEL workspace:{id}:tasks
    S-->>R: Task
    R-->>U: 201 {task}
```

---

## C. Data-Domain Write Map (`flowchart LR`)

Bipartite reverse index: entry points on the left, persistence targets on the right. Answers "who writes to this table / cache / queue?".

**Skeleton:**

```mermaid
flowchart LR
    subgraph Entries["Write Entries"]
        direction TB
        en_WP001["POST /api/tasks"]
        en_WP002["POST /api/tasks/bulk"]
        en_WP003["queue:task-import consumer"]
        en_WP004["cron: weekly_task_rollup"]
    end

    subgraph Targets["Persistence Targets"]
        direction TB
        tg_tasks[("operations.tasks")]
        tg_history[("operations.task_history")]
        tg_audit[("operations.audit_log")]
        tg_redis[["redis workspace:*:tasks"]]
    end

    en_WP001 --> tg_tasks --> tg_audit
    en_WP001 --> tg_redis
    en_WP002 --> tg_tasks --> tg_audit
    en_WP003 --> tg_tasks --> tg_audit
    en_WP004 --> tg_history
```

---

## D. DB Trigger / Function Graph (`flowchart LR`)

Postgres-side effects only. Shows cascades of triggers and functions that fire from table mutations. Reveals side-effect chains invisible in application code.

**Skeleton:**

```mermaid
flowchart LR
    tr_src_tasks[("operations.tasks")]
    tr_fn_after_insert{{"fn: tasks_after_insert_audit"}}
    tr_tgt_audit_log[("operations.audit_log")]
    tr_fn_bump_counters{{"fn: bump_workspace_counters"}}
    tr_tgt_counters[("operations.workspace_counters")]

    tr_src_tasks --> tr_fn_after_insert --> tr_tgt_audit_log
    tr_src_tasks --> tr_fn_bump_counters --> tr_tgt_counters
```

---

## Rendering Notes

- `scripts/mermaid-render.py` consumes `write-path-map.json` and emits all four diagrams into a single markdown block suitable for embedding in the main report.
- Node IDs are sanitized (alphanumeric + underscore, no leading digit) by `sanitize_id()`.
- Labels are truncated to 80 chars and escaped for Mermaid (`"`, `|`, newlines).
- Diagrams with zero data render an `empty[No data detected]` placeholder node rather than failing.
- Preview locally with `mmdc` (mermaid-cli) or by pasting into <https://mermaid.live>.
