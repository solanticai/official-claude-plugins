# Plan Orchestrator — Reference

Dense lookup material for the orchestrator. Kept separate from `SKILL.md` so the workflow file stays under 500 lines.

## Table of Contents

- [§1 — Domain Taxonomy](#1--domain-taxonomy)
- [§2 — Classifier Heuristics](#2--classifier-heuristics)
- [§3 — Agent Prompt Scaffold](#3--agent-prompt-scaffold)
- [§4 — Agent Report Schema (per task section)](#4--agent-report-schema-per-task-section)
- [§5 — Coverage Verification Rules](#5--coverage-verification-rules)
- [§6 — Compile-Plan Output Order](#6--compile-plan-output-order)
- [§7 — Hard Caps](#7--hard-caps)

---

## §1 — Domain Taxonomy

The classifier and the agent dispatcher use this controlled vocabulary. Every task gets one or more tags. Tasks with no clear match get the `backend` tag by default, since that's the domain most likely to be a useful starting point for ambiguous work in a typical web app.

| Tag | Scope | Typical signals in the bullet text |
|---|---|---|
| `frontend` | UI components, client routing, styling, browser state, accessibility, animations | "button", "page", "component", "style", "css", "tailwind", "react", "vue", "svelte", "form", "modal", "responsive", "a11y", "lighthouse" |
| `backend` | Server routes, business logic, validation, request handlers, queues, background jobs | "api", "endpoint", "route", "handler", "service", "controller", "validation", "queue", "worker", "cron", "webhook" |
| `database` | Schema, migrations, queries, RLS, indexes, performance, ORM mappings, triggers | "table", "column", "schema", "migration", "rls", "policy", "index", "query", "rpc", "trigger", "supabase", "postgres", "prisma", "drizzle" |
| `infrastructure` | CI/CD, Docker, deployment, environment, secrets, monitoring, logging, hosting | "ci", "cd", "deploy", "docker", "github actions", "vercel", "cloudflare", "env", "secret", "log", "monitor", "alert", "sentry" |
| `testing` | Unit/integration/e2e tests, fixtures, mocks, test utilities, coverage gates | "test", "spec", "unit", "e2e", "playwright", "cypress", "jest", "vitest", "fixture", "mock", "coverage" |
| `security` | Auth, authz, secrets handling, input sanitisation, vulnerability findings, supply chain | "auth", "permission", "rbac", "csrf", "xss", "sqli", "injection", "secret", "token", "vulnerability", "cve", "audit" |
| `documentation` | READMEs, inline docs, API docs, changelogs, ADRs, comments | "readme", "docs", "documentation", "comment", "jsdoc", "tsdoc", "changelog", "adr", "wiki" |

---

## §2 — Classifier Heuristics

`scripts/classify-tasks.py` uses a substring-match against each tag's signal list (case-insensitive, word-boundary-aware). A task gets a tag if it contains any of the tag's signals. A task can get multiple tags. If no tag matches, the task is tagged `backend` and flagged `default-tagged` so the user can see it was a guess.

The heuristic is deliberately simple and replaceable. Sub-agents apply richer judgement during Phase 3 — the classifier just decides which agents to spawn.

---

## §3 — Agent Prompt Scaffold

Every sub-agent invocation in Phase 3 follows this structure (the orchestrator fills in the placeholders):

```
You are the {DOMAIN}-investigator for the plan-orchestrator skill.

TARGET DIRECTORY: {target_dir}

DETECTED STACK:
{stack_output}

ASSIGNED TASKS:
{task_id}: {task_text}
{task_id}: {task_text}
...

YOUR JOB:
1. Investigate the codebase (read-only) to understand each task.
2. For each assigned task ID, propose a concrete, evidence-backed plan with file paths and line numbers.
3. Use any connected MCP servers relevant to your domain to gather live context. Examples:
   - database-investigator: Supabase MCP `execute_sql` (SELECT only), `list_tables`, `get_advisors`.
   - infrastructure-investigator: Cloudflare MCP, Vercel MCP, Sentry MCP.
   - backend-investigator: Stripe MCP for payment-related tasks; Supabase MCP for data-touching endpoints.
   - frontend-investigator: Figma MCP if design references are mentioned.
   Do NOT invent MCP responses. If an MCP is unreachable, note it in the report.
4. Return a markdown report following the structure in
   `${CLAUDE_PLUGIN_ROOT}/skills/plan-orchestrator/templates/agent-report-template.md`.
   Every assigned task ID MUST appear as its own section.
5. NEVER modify files. NEVER run destructive commands. Read, grep, query, report.

OUTPUT:
A single markdown document. No preamble, no narration, no questions back to the orchestrator.
```

The orchestrator does not negotiate with the sub-agent — the prompt is the contract.

---

## §4 — Agent Report Schema (per task section)

Each task block in an agent report should follow this shape so `compile-plan.py` can parse it deterministically:

```markdown
### {TASK_ID} — {short title}

**Original:** {verbatim bullet text}
**Domain:** {domain tag this agent owns}
**Confidence:** {low | medium | high}

**Investigation summary:**
{2–4 sentences on what was checked and what was found}

**Evidence:**
- `path/to/file.ts:42` — {what was observed}
- `path/to/other.sql:108` — {what was observed}
- {MCP query result, if applicable, with the query echoed}

**Proposed steps:**
1. {Step 1, including target file and line}
2. {Step 2}
...

**Risks:**
- {Risk + mitigation}

**Verification:**
- {How to confirm the change worked, e.g. test command, manual check, MCP query}
```

`compile-plan.py` uses regex to split on `### {TASK_ID}` headers — the format is load-bearing.

---

## §5 — Coverage Verification Rules

`scripts/verify-coverage.py` checks:

1. Every `T<N>` from the parsed task list appears at least once as the leading token of an `### ` heading in the concatenated buffer.
2. No `T<N>` appears that wasn't in the input list (catches agents inventing tasks).
3. Heading IDs are extracted with the regex `^###\s+(T\d+)\b` — agents that put the ID elsewhere or use the wrong heading level are treated as missing.

The verifier emits JSON to stdout:

```json
{
  "covered": ["T1", "T2", "T4"],
  "missing": ["T3"],
  "duplicates": ["T1"],
  "spurious": [],
  "coverage_pct": 75.0
}
```

Exit code `0` only when `missing` and `spurious` are both empty.

---

## §6 — Compile-Plan Output Order

`scripts/compile-plan.py` enforces this section order in the final plan:

1. Run header (timestamp, agent count, task count, coverage status).
2. Task coverage table (one row per input task ID).
3. Per-task plan blocks **in original input order** (T1, T2, T3, …).
4. Aggregated change set by file (alphabetically by path).
5. Cross-cutting concerns.
6. Suggested execution order.
7. Unresolved items (only if Phase 4 reported any).

This deterministic order means two runs over the same input produce diffable outputs.

---

## §7 — Hard Caps

| Limit | Value | Why |
|---|---|---|
| Max parallel agents | 8 | Token budget and orchestration overhead |
| Max tasks per single agent | 8 | Above this the agent's report quality degrades |
| Max sweeper rounds | 2 | Prevents infinite loops on genuinely ambiguous tasks |
| Max input tasks | 40 | Hand off to a different workflow at this scale |
| Min input tasks | 2 | Below this the orchestrator overhead isn't worth it |

These caps are enforced in `SKILL.md` Phase 1 and Phase 2.
