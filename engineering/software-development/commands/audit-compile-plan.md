---
name: audit-compile-plan
description: Compile a validated `application-audit` run into an executable action plan (action-plan.json + ACTION-PLAN.md). Defaults to the latest audit; pass an audit ID to target a specific run.
argument-hint: "[audit-id]"
---

# /audit-compile-plan

You are compiling the output of a finished `application-audit` run into a single, ranked action plan that the user can step through with `/audit-work`.

## Usage

```
/audit-compile-plan
/audit-compile-plan 20260425-1430
```

When called with no argument, target `.anthril/audits/latest/`. When called with an audit ID, target `.anthril/audits/<id>/`.

## Inputs

- `$ARGUMENTS` — optional audit ID.
- `.anthril/audits/<id>/validation.json` — the validator's calibrated findings (required input).

## Outputs

- `.anthril/audits/<id>/action-plan.json` — mutable state ledger consumed by `/audit-work`. Conforms to `templates/action-plan-schema.json`.
- `.anthril/audits/<id>/ACTION-PLAN.md` — human-readable severity-grouped checklist.

## Workflow

### 1. Recover the audit ID

1. If `$ARGUMENTS` is non-empty, treat the first token as the audit ID; verify `.anthril/audits/<id>/validation.json` exists.
2. Otherwise, `Read` `.anthril/audits/latest/AUDIT_ID`. The file holds the current ID on one line.
3. If neither resolves, abort with: "No audit found. Run `/software-development:application-audit` first, or pass an explicit audit ID."

### 2. Verify the run is ready to compile

- `validation.json` must exist and parse as JSON.
- It must contain at least one `findings[]` entry whose `validator_decision.status` is `confirmed` or `merged` — if it's empty, warn the user and emit an empty plan anyway (so the file structure is in place for re-compiles after future audits).
- If `validation.json` is missing, abort with: "Audit `<id>` has not finished validation. Resume the run with `/audit-proceed all` or wait for Phase 6 to complete."

### 3. Run the compiler

Invoke the bundled script:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/application-audit/scripts/compile-action-plan.py" \
  --validation ".anthril/audits/<id>/validation.json" \
  --audit-id "<id>" \
  --target "$(pwd)" \
  --out-json ".anthril/audits/<id>/action-plan.json" \
  --out-md ".anthril/audits/<id>/ACTION-PLAN.md" \
  --merge-existing
```

The `--merge-existing` flag preserves any in-flight state (`status`, `notes`, `files_touched`, `blockers`) on items whose IDs already exist in the prior `action-plan.json`. Without it, every item resets to `pending`. Always pass it on re-compiles; on first compile it's harmless because there's no prior file.

### 4. Report back

Display a one-screen summary to the user:

- Audit ID
- Total items, with severity breakdown (CRITICAL / HIGH / MEDIUM / LOW / INFO)
- Status breakdown if items were carried over (done / in-progress / blocked / pending)
- The next pending item (id, severity, title, phase) so the user knows where `/audit-work` will pick up
- The two file paths written (`action-plan.json` and `ACTION-PLAN.md`)
- A one-liner: "Run `/audit-work` to start the next item, or `/audit-work AA-###` to jump to a specific finding."

## Edge cases

- **Empty findings** — emit an empty plan and tell the user the audit produced no actionable items (often means the validator rejected everything, which is itself a useful signal).
- **Compiler script fails** — surface the stderr verbatim. Do not retry without a code fix.
- **Audit ID supplied but folder missing** — abort with the exact directory path that was looked up.

## Hard rules

- **Writes only to `.anthril/audits/<id>/`.** Never modify project source. Never modify `agent-reports/` or `validation.json` (those are inputs, not outputs).
- **Non-destructive on re-runs.** Always pass `--merge-existing` so progress is never wiped silently.
- **Single source of truth.** The plan derives from `validation.json` only. Do not ingest agent-reports directly — the validator already did that.
