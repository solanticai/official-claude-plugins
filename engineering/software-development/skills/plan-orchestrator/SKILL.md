---
name: plan-orchestrator
description: Turns a bullet list of tasks/issues/bugs into one ordered plan with full coverage verification. Fans out specialist sub-agents in parallel. Designed for Claude Code Plan Mode. Read-only — produces a plan, never edits.
argument-hint: [bullet list of tasks, issues, notes, or bug reports — one per line, prefixed with * or - or numbered]
allowed-tools: Read Grep Glob Bash Agent
effort: high
---

<!--
Runtime dependencies: bash, python3. The bare `Bash` entry in `allowed-tools`
is required to invoke the helper scripts under `scripts/` (parse-bullets,
classify-tasks, verify-coverage, compile-plan, detect-stack, stop-hook). Bash
is never used to mutate project source — the read-only guarantee is enforced
by the "no Write, no Edit" principle in the body.
-->


# Plan Orchestrator

ultrathink

## Before You Start

1. **Verify Plan Mode is on.** This skill is designed for Plan Mode. If the assistant is not in Plan Mode, continue but warn the user that the final output is a plan, not an executed change set.
2. **Locate the working target.** The orchestrator runs against the current working directory by default. If `$ARGUMENTS` contains a path on its own line (e.g. `target: ./apps/web`), use that as the target root. Otherwise, the cwd is the target.
3. **Detect the stack.** Run `scripts/detect-stack.sh` to pre-populate domain hints (Next.js implies frontend domain, Supabase implies database domain, etc.). This is shared with each sub-agent.
4. **Parse the input bullets.** Pipe `$ARGUMENTS` through `scripts/parse-bullets.py` to produce a JSON task list with one entry per bullet, each with a stable ID (`T1`, `T2`, ...) and the original text.
5. **Classify each task.** Pipe the parsed task JSON through `scripts/classify-tasks.py` to assign each task one or more domain tags from the controlled vocabulary in `reference.md` §1. Heuristic-only — agents will refine.

## User Context

$ARGUMENTS

Detected stack: !`bash "${CLAUDE_PLUGIN_ROOT}/skills/plan-orchestrator/scripts/detect-stack.sh" .`

Parsed tasks: !`echo "$ARGUMENTS" | python3 "${CLAUDE_PLUGIN_ROOT}/skills/plan-orchestrator/scripts/parse-bullets.py"`

Domain classification: !`echo "$ARGUMENTS" | python3 "${CLAUDE_PLUGIN_ROOT}/skills/plan-orchestrator/scripts/parse-bullets.py" | python3 "${CLAUDE_PLUGIN_ROOT}/skills/plan-orchestrator/scripts/classify-tasks.py"`

---

## Orchestration Phases

Execute every phase in order. Read-only guarantee: this skill never modifies source files. The output is a structured plan, not a refactor.

---

### Phase 1: Input Validation & Task Inventory (no score)

**Objective:** Confirm the input is a usable bullet list and every task has a stable ID.

1. If `parse-bullets.py` returns an empty array, ABORT and tell the user: "No bullets detected after the slash command. Paste tasks as `* item` / `- item` / `1. item`, one per line." Do not invent tasks.
2. If `parse-bullets.py` returns fewer than 2 tasks, the orchestrator is overkill — tell the user to either add more tasks or just describe the change directly without the slash command. Continue if they confirm.
3. Print the task inventory to the user as a numbered list with their assigned IDs. This is the contract — every ID listed here MUST appear in the final plan.
4. Cap: if more than 40 tasks, ask the user to split into batches. The orchestration overhead becomes counterproductive past ~40 items.

---

### Phase 2: Domain Routing (no score)

**Objective:** Group tasks by domain and decide how many sub-agents to spawn.

1. Read the classifier output. Each task has 1+ domain tags from: `frontend`, `backend`, `database`, `infrastructure`, `testing`, `security`, `documentation`.
2. Build the routing table: domain → list of task IDs. Tasks with multiple domains get routed to **all** their domains (each agent reports on the slice relevant to it).
3. Decide agent count using these rules:
   - One agent per domain with at least one task.
   - If a single domain has more than 8 tasks, split into multiple workers within that domain (`backend-investigator-A`, `backend-investigator-B`).
   - Hard cap: 8 parallel agents total. If routing would exceed 8, merge the smallest domains into the most-related larger one (e.g., `documentation` merges into the largest non-doc domain).
4. Show the user the agent dispatch table before spawning. Do not ask for confirmation in Plan Mode — proceed.

---

### Phase 3: Parallel Sub-Agent Investigation

**Objective:** Each sub-agent investigates its assigned tasks against the actual codebase and returns a structured report.

**Spawn all sub-agents in parallel** by emitting multiple `Agent` tool calls in a single assistant message. Each call uses the matching `subagent_type`. The full prompt scaffold the orchestrator fills in for each agent lives in `reference.md` §3, and the per-task report shape it expects back is defined in §4.

| Domain | `subagent_type` |
|---|---|
| frontend | `frontend-investigator` |
| backend | `backend-investigator` |
| database | `database-investigator` |
| infrastructure | `infrastructure-investigator` |
| testing | `testing-investigator` |
| security | `security-investigator` |
| documentation | `documentation-investigator` |

Each sub-agent prompt MUST include:

1. The target directory (working root or `target:` from $ARGUMENTS).
2. The full bullet list of tasks assigned to it, with their stable IDs (e.g. `T3`, `T7`).
3. The detected stack output.
4. The exact instruction to **return a markdown report following `templates/agent-report-template.md`** with one section per assigned task ID. Every assigned ID must appear in the agent's report — partial coverage is a failure.
5. The reminder to use any connected MCP servers relevant to its domain (Supabase, Stripe, Cloudflare, GitHub, Sentry, Vercel, Figma, etc.) for live introspection. Sub-agents inherit the session's MCP connections.
6. The read-only guarantee — investigation only, no file edits.

Wait for all sub-agents to return. If any agent fails, fall back to running the missing tasks through `coverage-sweeper`.

---

### Phase 4: Coverage Verification

**Objective:** Confirm every input task ID has at least one corresponding section across all sub-agent reports.

1. Concatenate every sub-agent report into a single buffer (separated by `\n\n---\n\n`).
2. Pipe the buffer plus the parsed task JSON through `scripts/verify-coverage.py`. The script accepts `--tasks <path>` and reads the buffer from stdin, returns JSON with `{covered: [...], missing: [...], duplicates: [...]}` and exits non-zero if `missing` is non-empty. The exact regex used for heading detection (`^###\s+(T\d+)\b`) is documented in `reference.md` §5 — agents that put the ID elsewhere are treated as missing.
3. **If `missing` is empty:** proceed to Phase 5.
4. **If `missing` is non-empty:** spawn `coverage-sweeper` (a single agent) with ONLY the missing task IDs and their original text. When it returns, append its report to the buffer and re-run verification. Allow at most 2 sweeper rounds — if tasks are still missing, surface them in the final plan as `UNRESOLVED — investigate manually` rather than fabricating coverage.
5. **Duplicates** (same task covered by multiple agents) are not failures — they're expected for cross-cutting tasks. Note them so the compiler can deduplicate.

---

### Phase 5: Plan Compilation

**Objective:** Produce a single ordered plan from the agent reports.

1. Pipe the verified report buffer plus the task JSON through `scripts/compile-plan.py`. The script:
   - Parses each agent report's per-task sections.
   - Groups findings by task ID first (so the user sees every input bullet addressed in order), then by file (so changes to the same file are batched), then by risk tier.
   - Emits the final plan in the structure of `templates/plan-template.md`. The deterministic section order is documented in `reference.md` §6, and the hard caps that gate Phases 1–4 are listed in `reference.md` §7.
2. The compiled plan must include:
   - Header with run metadata (timestamp, agent count, task count, coverage status).
   - **Task coverage table** — one row per input task ID with a green/yellow/red marker.
   - **Per-task plan blocks** in input order — each contains: original bullet text, contributing agents, summary, proposed steps with file:line evidence, risks, suggested verification.
   - **Aggregated change set by file** — every file touched, with the merged set of changes from all task blocks.
   - **Cross-cutting concerns** section — anything that affects multiple files or multiple domains.
   - **Suggested execution order** — a topologically reasonable sequence (db migrations first, then backend, then frontend, then docs/tests).
   - **Unresolved items** — anything still missing after Phase 4 sweepers.
3. Present the compiled plan as the assistant's response. In Plan Mode, this becomes the argument to `ExitPlanMode`.

---

### Phase 6: Stop-Hook Reconciliation (background)

**Objective:** Catch the case where the skill aborts mid-flight and leaves orphaned state.

The Stop hook (`hooks/hooks.json` → `scripts/stop-hook.sh`) checks for any orphaned state markers under `/tmp/plan-orchestrator-*` from previous runs of this session. If a marker exists without a matching `*.complete` flag, the hook prints a warning to stderr so the user knows the prior orchestrator run never finalised. The hook is advisory only — it never blocks the conversation.

The skill's normal happy-path writes a marker on entry (Phase 1) and the matching `.complete` flag on Phase 5 success, both via Bash so they work in Plan Mode.

If `/tmp` is not writable (locked-down environments, read-only filesystems), the marker write degrades silently — Phase 1 continues without writing, and the stop hook simply finds nothing to surface. The orchestrator never depends on the marker for correctness; it is purely advisory state for the next session.

---

## Important Principles

- **Every input bullet appears in the final plan.** This is non-negotiable. Coverage verification (Phase 4) enforces it; the sweeper agent fills gaps; truly unresolved items are surfaced explicitly, never silently dropped.
- **Every plan step has evidence.** File path + line number, schema name, command output, or MCP query result. "Update the auth flow" is not a plan step — "Update `apps/web/src/middleware.ts:14` to call `getSession()` before redirect" is.
- **Read-only.** No `Write`, no `Edit`, no `git commit`, no DB writes. The plan describes the changes; the user (or a follow-up session outside Plan Mode) applies them.
- **Sub-agents inherit MCP access.** Each agent's prompt explicitly reminds it to use connected MCP servers. Agents do not invent MCP responses.
- **Dynamic agent count, not fixed.** Empty domains get no agent. Overloaded domains get split. Cap at 8.
- **Australian English** in narrative, **markdown-first** in outputs, **evidence-backed** in every claim — consistent with the rest of the `software-development` plugin.
- **Fail loud.** If `parse-bullets.py` finds nothing, abort. If MCPs fail mid-investigation, the relevant agent reports the failure rather than fabricating findings. If the verifier can't reconcile coverage, surface the gap.

---

## Edge Cases

1. **Empty $ARGUMENTS** — abort with the bullet-format reminder. Do not invent tasks.
2. **Single-task input** — ask the user if they want orchestration overhead or a direct answer. Default to direct answer if no response.
3. **Cross-domain tasks** — get routed to multiple agents. The compiler deduplicates by `(task_id, file)` pairs in the final plan.
4. **Tasks that name a specific MCP** (e.g. "check Stripe webhook handlers") — route to the matching domain (`backend` for Stripe), and the agent's prompt nudges it toward the named MCP.
5. **Tasks that reference a path that doesn't exist** — the relevant agent reports `path-not-found` rather than guessing. Surfaces in the plan as a verification gap.
6. **Monorepo** — domain agents work over the entire repo by default. If `target: ./apps/web` is in the args, the target is scoped to that subtree.
7. **No MCPs connected** — agents fall back to filesystem-only investigation and explicitly note in their reports which MCP would have improved their coverage.
8. **Sub-agent timeout/failure** — orchestrator catches the failure, routes the affected task IDs to `coverage-sweeper`, and notes the failure in the final plan's "Unresolved" section if sweep also fails.
