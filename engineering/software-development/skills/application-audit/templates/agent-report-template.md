# Agent Report — {{agent_name}}

> Auditors fill this template once per finding. The skill's `validate-findings.py`
> parses on `### F<N>` headings — the structure inside each section is for human
> readers and the per-finding aggregation. Do not change the heading shape.

**Audit ID:** `{{audit_id}}`
**Target:** `{{target_dir}}`
**Profile:** `.anthril/preset-profile.md` (read at run start)
**Permissive mode:** {{true | false}}
**MCPs used:** {{Supabase, Vercel, Sentry, ...}} or "none"
**MCPs unreachable:** {{list, with reason}} or "none"
**Memex consulted:** {{plugin | wiki | none}}
**Open questions filed:** {{count}} — see `.anthril/questions/{{agent_name}}-*.md`

---

### F1 — {{short title}}

**Category:** {{rendering | caching | auth | rls | connection-pool | realtime | secret-leak | bundle | a11y | indexing | ...}}
**Severity (proposed):** {{CRITICAL | HIGH | MEDIUM | LOW | INFO}}
**Confidence:** {{low | medium | high}}
**Source notes ref:** {{tasks.md §3 | client-connection-audit.md §5 | none}}

**Investigation summary:**
{{2–4 sentences: what was checked and what was found.}}

**Evidence:**
- `{{path/to/file.ts}}:{{line}}` — {{what was observed}}
- `{{path/to/other.sql}}:{{line}}` — {{what was observed}}
- {{MCP query result, with the query echoed verbatim, if applicable}}

**Proposed remediation:**
1. {{Step 1 — include target file path and line where relevant.}}
2. {{Step 2}}
3. {{Step 3}}

**Risks if left unfixed:**
- {{Concrete consequence + likelihood + blast radius}}

**Verification:**
- {{How to confirm the change worked — test command, manual check, MCP query, log probe.}}

---

### F2 — {{short title}}

{{... repeat the block above for every finding ...}}
