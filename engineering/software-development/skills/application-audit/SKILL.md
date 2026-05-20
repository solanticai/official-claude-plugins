---
name: application-audit
description: Multi-agent audit for Next.js + React + Supabase apps. Ten specialist auditors run in parallel, findings get validated, and a ranked evidence-backed report is written to `.anthril/audits/<ID>/REPORT.md`. Read-only on source.
argument-hint: "[target-dir] (optional, defaults to cwd) [--refresh-profile]"
allowed-tools: Read Grep Glob Bash Agent Write
effort: high
---

<!--
Runtime dependencies: bash, python3, jq. The orchestrator delegates parsing,
freshness checks, and report compilation to scripts under `scripts/`. The bare
`Bash` entry in `allowed-tools` is required to invoke the dozen helpers — it is
never used to mutate project source (the read-only guarantee is enforced by
"writes only to `.anthril/`" below).
-->


# Application Audit

ultrathink

## Before You Start

1. **Locate the working target.** This skill runs against the current working directory by default. If `$ARGUMENTS` contains a path on its own line (e.g. `target: ./apps/web`), use that as the target root. Otherwise the cwd is the target.
2. **Check for `--refresh-profile`** in `$ARGUMENTS`. If present, force the profile-builder agent to regenerate `.anthril/preset-profile.md` even when one exists.
3. **Stay strictly read-only on project source.** This skill writes ONLY to `.anthril/` under the target. No edits to application code, configs, migrations, or anything outside the `.anthril/` folder.
4. **Stack is permissive, not strict.** The canonical preset is Next.js 15 + React 19 + TypeScript Strict + Supabase + Tailwind. If the detected stack diverges (Next 14, Drizzle instead of `supabase-js`, no Tailwind, etc.) the skill continues, the profile records the *actual* versions, and affected auditors flag reduced confidence. Never hard-fail on stack mismatch.
5. **Self-answer before asking.** If `claude-memex` is connected or a `.memex/` wiki exists, every auditor should consult it before filing an open question.

## User Context

$ARGUMENTS

Detected stack: !`bash "${CLAUDE_PLUGIN_ROOT}/skills/application-audit/scripts/detect-stack.sh" .`

Prerequisites & MCPs: !`bash "${CLAUDE_PLUGIN_ROOT}/skills/application-audit/scripts/check-prerequisites.sh" .`

Memex availability: !`bash "${CLAUDE_PLUGIN_ROOT}/skills/application-audit/scripts/check-memex.sh" .`

Existing `.anthril/` state: !`bash "${CLAUDE_PLUGIN_ROOT}/skills/application-audit/scripts/check-anthril-state.sh" .`

---

## Phase 1: Discovery & Precheck (no score)

**Objective:** Establish stack, prerequisites, and the audit workspace.

1. Read the User Context block above. The four shell commands have already populated stack, prerequisites, memex availability, and existing `.anthril/` state.
2. If the stack output shows neither Next.js, React, nor Supabase, ABORT with: "This skill targets Next.js + React + Supabase apps. Detected: <summary>. If you want to run anyway, re-invoke with `--allow-stack-drift` (treats all auditors as low-confidence)."
3. If the stack matches partially (e.g. Next 14 instead of 15, no Tailwind), continue in **permissive mode**: print a one-line warning and pass `permissive_mode=true` to every auditor in Phase 4.
4. Run `init-anthril.sh` to scaffold (idempotent):
   ```
   .anthril/
   ├── preset-profile.md            (created in Phase 2)
   ├── audits/
   ├── audits/latest/               (symlink-or-copy target, populated in Phase 7)
   ├── questions/
   ├── questions/.resolved/
   └── README.md                    (one-line "managed by application-audit skill")
   ```
5. Generate the audit ID by running `generate-audit-id.sh`. Format: `YYYYMMDD-HHMM` (sorts chronologically). Capture as `AUDIT_ID`.
6. Create `.anthril/audits/$AUDIT_ID/` and `.anthril/audits/$AUDIT_ID/agent-reports/`.

---

## Phase 2: Profile Bootstrap or Refresh

**Objective:** Ensure `.anthril/preset-profile.md` is current. The profile is the single canonical context object every auditor reads first.

1. **If `.anthril/preset-profile.md` does NOT exist** (or `--refresh-profile` was passed):
   - Dispatch the `application-audit-profile-builder` sub-agent. Pass: `target_dir`, `audit_id`, `permissive_mode`, the detected stack output, the path to `templates/preset-profile-template.md`, and `mode=create`.
   - Wait for completion. Verify the file now exists.
2. **If it exists**, run `check-profile-freshness.sh`. The script compares declared versions in the profile against the actual `package.json`, `tsconfig.json`, `next.config.*`, `tailwind.config.*`, and Supabase client imports.
   - If the script exits 0: profile is current. Skip rebuild.
   - If it exits 10 (stale): re-dispatch `application-audit-profile-builder` with `mode=update`. The agent preserves any text between `<!-- HUMAN-EDIT-START -->` / `<!-- HUMAN-EDIT-END -->` markers.
3. Read the profile into context. Every auditor in Phase 4 receives its path.

---

## Phase 3: Memex Integration Probe

**Objective:** Tell the auditors how (or whether) to self-answer questions before filing them.

The `check-memex.sh` output sets one of:

- `MEMEX_MODE=plugin` — `claude-memex` plugin available; auditors should call the `memex:doc-query` skill from within their dispatch.
- `MEMEX_MODE=wiki` — no plugin, but `.memex/index.md` exists. Auditors read it directly with `Read`/`Glob`.
- `MEMEX_MODE=none` — no memex; auditors skip the self-answer step and go straight to filing a question.

Pass `MEMEX_MODE` to every auditor in Phase 4.

---

## Phase 4: Parallel Auditor Fan-Out

**Objective:** Each auditor investigates its domain against the actual codebase and writes a structured report to `.anthril/audits/$AUDIT_ID/agent-reports/<agent-name>.md`.

**Spawn nine sub-agents in parallel** in a single assistant message with nine `Agent` tool calls. The validator runs in Phase 6, NOT here.

| `subagent_type` | Domain |
|---|---|
| `application-audit-frontend-auditor` | Rendering modes, `use client` boundaries, Suspense, React 19 Actions, manual memoisation, bundle analysis, scripts, images, fonts, Tailwind scanning, design tokens, dark mode |
| `application-audit-backend-auditor` | Supabase SSR auth setup, Edge Functions, mutation boundaries, schema migrations, type generation, load testing, OpenTelemetry instrumentation |
| `application-audit-bug-finder` | Cross-cutting defects: uncaught promises, missing error boundaries, stale revalidation assumptions, route-handler freshness bugs, async hydration mismatches |
| `application-audit-cross-cutting-security-auditor` | RLS audit (per-op), API key separation, storage policies, CSP/headers, server-action CSRF, env var exposure, input sanitisation |
| `application-audit-client-connection-auditor` | Browser Data API usage, request dedup, client-instantiation patterns, Realtime subscription lifecycle |
| `application-audit-server-client-auditor` | Two-client SSR pattern, middleware Proxy matcher, auth-refresh churn, auth-aware caching, server-side data shifts |
| `application-audit-postgres-auditor` | Connection mode (direct/Supavisor session/transaction), prepared statements in transaction mode, ORM wiring, query telemetry, index alignment, bloat |
| `application-audit-leak-detection-auditor` | Realtime cleanup, hardcoded secrets, exposed API keys, unmasked logging, PII in error responses |
| `application-audit-connection-limit-auditor` | Pool size vs PostgREST headroom, dual-pooler stacking, idle-session monitoring, alert coverage |

Each `Agent` invocation MUST include in its prompt:

1. `target_dir` (resolved absolute path)
2. `audit_id` and the absolute path to its required output file: `.anthril/audits/<AUDIT_ID>/agent-reports/<agent-name>.md`
3. `profile_path`: `.anthril/preset-profile.md`
4. `permissive_mode`: true/false
5. `memex_mode`: `plugin` | `wiki` | `none`
6. `connected_mcps`: list from prerequisites output
7. The reminder: **every finding gets `### F<N> — <title>`** so the validator can parse. No nested ID headings.
8. The open-question protocol: if the agent cannot resolve a question via memex/MCP/code reading, it MUST file `.anthril/questions/<agent-name>-<n>.md` (using `templates/question-template.md`) instead of fabricating.
9. Read-only guarantee — no `Write` outside `.anthril/`, no `Edit` ever.

When all nine return, proceed to Phase 5.

---

## Phase 5: Open-Questions Gate

**Objective:** Halt the run cleanly if any auditor filed unresolved questions.

1. Run `collect-open-questions.sh` against `.anthril/questions/`. The script returns JSON: `{ pending: [{ agent, file, question }], total: N }`.
2. **If `total === 0`:** proceed directly to Phase 6.
3. **If `total > 0`:**
   - Print a markdown summary to the user with the structure:
     ```
     ## ⏸ Audit paused — N open questions need answers

     ### <agent-name>
     - **Q:** <question>
       File to answer in: `.anthril/questions/<agent-name>-<n>.md`

     ### <next-agent>
     ...

     **To resume:** answer the questions in-place (replace the `## Answer` placeholder),
     then run `/audit-proceed <agent-name>` for one agent, or `/audit-proceed all`
     to resume every paused auditor.
     ```
   - **Do NOT run the validator. Do NOT write the final report.** Exit the skill.
   - When the user runs `/audit-proceed`, that command re-enters this skill at Phase 4 for the named agents only, then re-runs Phase 5 until clear.

---

## Phase 6: Validation

**Objective:** A single audit-validator agent cross-checks all nine reports for contradictions, duplicate findings, severity drift, and fabricated evidence.

1. Dispatch `application-audit-validator` with these inputs:
   - `reports_dir`: `.anthril/audits/$AUDIT_ID/agent-reports/` (the directory of the nine per-agent reports — no concatenation needed; the validator's script walks the directory itself)
   - `profile_path`: `.anthril/preset-profile.md`
   - `target_dir`: as resolved in Phase 1
   - `audit_id`: `$AUDIT_ID`
   - `validation_md_out`: `.anthril/audits/$AUDIT_ID/validation.md`
   - `validation_json_out`: `.anthril/audits/$AUDIT_ID/validation.json`
2. The validator's workflow has two phases (it owns both):
   - First it runs `validate-findings.py --reports-dir <reports_dir> --out <intermediate.json>` to parse every agent report into a structured JSON **intermediate** (no semantic checks — just heading and field extraction).
   - Then the validator agent reads the intermediate back, re-verifies each cited file:line and MCP query, dedupes across agents, calibrates severity, assigns cross-agent IDs (`AA-001`, ...), and writes the **final** `validation.md` (human-readable) and `validation.json` (matching `templates/findings-schema.json`).
3. The final `validation.json` summarises:
   - **Confirmed** — high-confidence, evidence-backed findings ready for the report
   - **Rejected** — fabricated paths, missing evidence, out-of-scope, duplicates
   - **Cross-domain conflicts** — e.g. frontend says contract stable, backend flags breakage
   - **Severity normalisation** — every confirmed finding gets a calibrated severity from {CRITICAL, HIGH, MEDIUM, LOW, INFO}

If the validator returns no confirmed findings, surface a warning and continue — the report will say "no actionable findings detected" rather than fabricating.

---

## Phase 7: Synthesis

**Objective:** Produce a single ranked, evidence-backed report at `.anthril/audits/$AUDIT_ID/REPORT.md`.

1. Run `compile-report.py` with:
   - `--validation .anthril/audits/$AUDIT_ID/validation.json`
   - `--reports-dir .anthril/audits/$AUDIT_ID/agent-reports/`
   - `--profile .anthril/preset-profile.md`
   - `--audit-id $AUDIT_ID`
   - `--target $TARGET_DIR` (the absolute path you resolved in Phase 1)
   - `--template ${CLAUDE_PLUGIN_ROOT}/skills/application-audit/templates/audit-report-template.md`
   - `--out .anthril/audits/$AUDIT_ID/REPORT.md`
2. Run `render-summary.py --validation .anthril/audits/$AUDIT_ID/validation.json --audit-id $AUDIT_ID --out .anthril/audits/$AUDIT_ID/REPORT.json` to produce the JSON sidecar (matches `templates/findings-schema.json`).
3. Update `.anthril/audits/latest/`:
   - Remove existing `latest/` contents.
   - Copy `REPORT.md`, `REPORT.json`, `validation.md` into `.anthril/audits/latest/`.
   - Write `.anthril/audits/latest/AUDIT_ID` containing the literal id (so `/audit-proceed` can recover it).

The report structure (driven by `audit-report-template.md`):

- **Run header** — audit ID, timestamp, target, profile snapshot, permissive flag
- **Executive summary** — top 10 findings ranked by severity × confidence × scope
- **Per-domain sections** — one per auditor; verified findings only
- **Cross-cutting risks** — from validation
- **Suggested remediation order** — security/correctness first, then fundamentals (rendering, caching, server/client boundaries), then performance (bundle, scripts, images), then measured optimisation (queries, indexes, pool sizing)
- **Open questions resolved during this run** — for transparency
- **Rejected findings appendix** — what the validator threw out and why

---

## Phase 8: Report-Back & Next Steps

**Objective:** Show the user a short, actionable summary and point them at the right follow-up.

1. Print to the user:
   ```
   ✅ Audit complete — .anthril/audits/<AUDIT_ID>/REPORT.md

   <total findings> findings: <C> CRITICAL, <H> HIGH, <M> MEDIUM, <L> LOW, <I> INFO
   Validator confidence: <pct>%

   Top 5 fixes:
   1. <severity> — <title>           (<agent>, <file:line>)
   2. ...

   Next steps:
   - Read the full report: .anthril/audits/<AUDIT_ID>/REPORT.md
   - Compile an executable action plan: /audit-compile-plan
   - Step through items one at a time: /audit-work
   - Or generate a richer implementation plan: /software-development:plan-orchestrator <paste top findings as bullets>
   - Re-audit after fixes: re-run this skill (a new audit ID will be generated)
   ```
2. Do not auto-spawn `plan-orchestrator` or `/audit-compile-plan`. The user decides whether to act.
3. End the run. The skill never modifies project source — the user (or a follow-up session, e.g. `/audit-work`) applies any changes.

The companion commands `/audit-compile-plan` and `/audit-work` (defined in `commands/`) turn the validated `findings[]` into a stateful, resumable remediation loop — see their command files for the full contract.

---

## Important Principles

- **Read-only on source.** No `Write`, `Edit`, or destructive bash anywhere outside `.anthril/`. The skill describes; the user (or a follow-up) acts.
- **Every finding has evidence.** Every `path/file.ext:N` reference in any report comes from a tool call the agent actually made. Validator rejects findings without verifiable evidence.
- **Permissive on stack mismatch.** Document drift, flag reduced confidence, never hard-fail.
- **Self-answer before asking.** If memex is available, every auditor consults it first. Open questions are a last resort.
- **Open questions halt the run.** If any auditor is uncertain, the skill pauses cleanly. The user resumes via `/audit-proceed`. No fabricated findings.
- **Sub-agents inherit MCP access.** Auditors call the Supabase MCP for schema, the Vercel MCP for runtime logs, etc. Each auditor's prompt names the relevant MCPs. If an MCP is unreachable, the auditor lists it under `MCPs unreachable:` in its report header.
- **Australian English** in narrative; **markdown-first** in outputs; **evidence-backed** in every claim.
- **Deterministic IDs.** Audit ID = `YYYYMMDD-HHMM`. Findings = `F1`, `F2`, ... per auditor (the validator namespaces them in the final report).

---

## Edge Cases

1. **No `.anthril/` write permission** — abort immediately with: "Cannot write to `.anthril/`. Check filesystem permissions; this skill only writes there."
2. **Audit ID collision** (a `YYYYMMDD-HHMM` folder already exists) — append `-1`, `-2`, ... until unique. Report the suffix to the user.
3. **All nine agents file open questions** — Phase 5 still halts cleanly; the user answers and resumes. The validator never runs with partial coverage.
4. **A single agent times out or errors** — record the failure as a synthetic question in `.anthril/questions/<agent>-timeout.md` and let Phase 5 halt. Do not proceed without the agent's coverage.
5. **No connected MCPs** — auditors fall back to filesystem-only investigation. Each report's header should list every MCP that would have improved its coverage under `MCPs unreachable: not connected`.
6. **Memex available but query fails** — auditor degrades to filesystem-only and notes the failure in its report. Does not file a memex-failure question.
7. **Profile-builder fails on first run** — abort. Without a profile, auditors lack the canonical context object. Tell the user to inspect the profile-builder's output and re-run.
8. **`--refresh-profile` on a run with no existing profile** — equivalent to a normal first run; the flag is a no-op rather than an error.
9. **Resume command names a non-existent agent** — `/audit-proceed` lists the valid auditor names back to the user and exits without dispatching.
10. **`.anthril/audits/latest/AUDIT_ID` missing during resume** — `/audit-proceed` walks `.anthril/audits/` for the most recent ID by alphabetical sort and warns the user about the recovery.
