---
name: audit-work
description: Step through audit action-plan items one at a time — load the next pending finding (or a specific one), implement its remediation, run verification, mark complete. Resumable across sessions.
argument-hint: "[item-id | --status | --skip <id>]"
---

# /audit-work

You are working through a compiled audit action plan, one item at a time. State is persisted in `.anthril/audits/<id>/action-plan.json` so the loop survives session boundaries.

## Usage

```
/audit-work                    # pick the next pending item by execution order
/audit-work AA-007             # jump to a specific item
/audit-work --status           # print progress summary, do not start work
/audit-work --skip AA-012      # mark an item as skipped (with reason from the user)
```

## Workflow

### 1. Locate the action plan

1. `Read` `.anthril/audits/latest/AUDIT_ID` to get the current audit ID.
2. `Read` `.anthril/audits/<id>/action-plan.json`.
3. If either is missing, abort with: "No action plan found. Run `/audit-compile-plan` first."

### 2. Branch on `$ARGUMENTS`

**`--status`** — print a summary table grouped by phase showing every item's id, severity, status, title. Show counts for each status. Stop. Do not modify state.

**`--skip <id>`** — confirm the user wants to skip; ask for a one-line reason; set the item's `status = "skipped"`, append the reason to `notes`, write the file back. Stop.

**`AA-###`** — load that specific item. If its status is already `done`, ask whether to re-open it (set status back to `in_progress`) or to abort. If the id doesn't exist, list valid ids and abort.

**No arg** — pick the first item where `status == "pending"`, ordered by `order` (ascending). If none pending, congratulate the user and surface counts of `blocked` and `skipped` items so they know what's left. Stop.

### 3. Begin work on the item

1. Set `item.status = "in_progress"` and `item.started_at = <UTC ISO timestamp>` and `audit.last_updated_at = <same>`. Persist via atomic write (write `action-plan.json.tmp`, then rename — never write the live file directly).
2. Update `summary.by_status` counts to match.
3. Display the item to the user in this exact shape:
   ```
   ━━━ AA-### · CRITICAL · server-client ━━━
   Title goes here.

   Summary: ...

   Evidence:
     - file:line — observation
     - ...

   Risks if left unfixed:
     - ...

   Remediation steps:
     1. ...
     2. ...

   Verification:
     - ...
   ```

### 4. Implement the remediation

You now have the full toolset (Read, Edit, Write, Bash, Grep, Glob, Agent). Walk through the `remediation_steps` in order:

- Read the files cited in `evidence[]` to confirm the issue is still present.
- Apply edits. For multi-file changes, prefer parallel `Edit` calls.
- If a step requires a migration or a new file, follow the project's existing conventions (do not invent new directories).
- If you need to spawn a sub-agent (e.g. for cross-file impact analysis), use the `Agent` tool with an appropriate `subagent_type`.

**Track every file you touch.** After each `Edit` / `Write`, append the repo-relative path to `item.files_touched` (deduplicated). Update the JSON file at most once per item, at the end of the work-loop in step 6 — don't write after every edit.

### 5. Run the verification

For each entry in `item.verification`, run the check (Bash command, or describe the manual check if it's not executable). If a verification step is descriptive only ("confirm RLS policy exists for delete"), perform the check via Read/Grep and confirm in your written output.

If verification:
- **passes** — proceed to step 6 with `status = "done"`.
- **fails on a recoverable issue** — fix the issue, re-run verification.
- **fails because the remediation was wrong** — set `status = "blocked"`, append the failure to `item.blockers[]` with `{ reason, logged_at }`, surface to the user, and stop. Do not pretend success.

### 6. Persist completion state

Atomically update `action-plan.json`:

- If passed: `item.status = "done"`, `item.completed_at = <UTC ISO timestamp>`, write any `notes` / `files_touched` accumulated.
- If blocked: `item.status = "blocked"`, append blocker.
- Always: refresh `summary.by_status` counts and `audit.last_updated_at`.

Re-render `ACTION-PLAN.md` so the human-readable checklist stays in sync. The simplest approach is to re-invoke `compile-action-plan.py --merge-existing` against the same `validation.json`:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/application-audit/scripts/compile-action-plan.py" \
  --validation ".anthril/audits/<id>/validation.json" \
  --audit-id "<id>" \
  --target "$(pwd)" \
  --out-json ".anthril/audits/<id>/action-plan.json" \
  --out-md ".anthril/audits/<id>/ACTION-PLAN.md" \
  --merge-existing
```

This carries forward the in-memory state we just wrote and refreshes the markdown view in one step.

### 7. Hand off to the next item

Print to the user:

- `✓ AA-### marked done` (or `✗ AA-### blocked: <reason>`)
- A list of files touched (or "no files modified" if it was a no-op verification)
- The next pending item: `Next: AA-### [SEV] — <title>. Run /audit-work to continue.`
- If no pending items remain: `🎉 All items resolved. <N> done · <M> blocked · <K> skipped.`

## Hard rules

- **Atomic writes only.** Always write to `<path>.tmp` and rename. A crash mid-edit must never leave `action-plan.json` in a half-written state.
- **One item per invocation.** Do not chain into the next item automatically — the user may want to review or commit between items.
- **Never silently mark blocked items as done.** If verification fails, the item stays blocked until the user explicitly clears it (by re-running `/audit-work AA-###`).
- **Don't skip the verification.** Even when remediation feels obvious, the validator's `verification` is the contract for "done".
- **Branch creation is the user's call.** This command does not create or switch git branches. Mention any project branch protections (e.g. main is protected) but let the user decide.
- **Respect previous notes.** If `item.notes` already contains content (from a prior session), append rather than overwrite.
