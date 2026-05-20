# Agent Report — {{agent_name}}

> Sub-agents fill this template once per assigned task ID. The orchestrator's
> compile-plan.py parses on `### T<N>` headings — the structure inside each
> section is for human readers and the per-task aggregation. Do not change
> the heading shape.

**Target:** `{{target_dir}}`
**Assigned task IDs:** {{T1, T2, …}}
**MCPs used:** {{Supabase, Stripe, …}} or "none"
**MCPs unreachable:** {{list, with reason}} or "none"

---

### {{TASK_ID}} — {{short title}}

**Original:** {{verbatim bullet text}}
**Domain:** {{frontend | backend | database | infrastructure | testing | security | documentation}}
**Confidence:** {{low | medium | high}}

**Investigation summary:**
{{2–4 sentences on what was checked and what was found.}}

**Evidence:**
- `{{path/to/file.ts}}:{{line}}` — {{what was observed}}
- `{{path/to/other.sql}}:{{line}}` — {{what was observed}}
- {{MCP query result, with the query echoed verbatim, if applicable}}

**Proposed steps:**
1. {{Step 1 — include target file path and line where relevant.}}
2. {{Step 2}}
3. {{Step 3}}

**Risks:**
- {{Risk + suggested mitigation}}

**Verification:**
- {{How to confirm the change worked — test command, manual check, MCP query, etc.}}

---

### {{TASK_ID_2}} — {{short title}}

{{... repeat the block above for every assigned task ID ...}}
