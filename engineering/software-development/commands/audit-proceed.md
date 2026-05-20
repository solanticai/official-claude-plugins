---
name: audit-proceed
description: Resume an `application-audit` run after answering open questions filed under `.anthril/questions/`. Pass `all` or one or more agent names.
argument-hint: "<all | agent-name> [agent-name ...]"
---

# /audit-proceed

ultrathink

You are resuming a paused `application-audit` run. The skill paused at Phase 5 because one or more auditors filed open questions to `.anthril/questions/<agent-name>-<n>.md`. The user has now answered those questions and invoked this command to continue the audit.

## Usage

```
/audit-proceed all
/audit-proceed frontend-auditor
/audit-proceed postgres-auditor connection-limit-auditor
```

Valid agent names (the bare role name; no `application-audit-` prefix needed in this command):

- `frontend-auditor`
- `backend-auditor`
- `bug-finder`
- `cross-cutting-security-auditor`
- `client-connection-auditor`
- `server-client-auditor`
- `postgres-auditor`
- `leak-detection-auditor`
- `connection-limit-auditor`

## Workflow

### 1. Recover the audit ID

1. `Read` `.anthril/audits/latest/AUDIT_ID`. The file contains a single audit ID on one line.
2. If the file is missing, `Glob` `.anthril/audits/*/agent-reports/` and pick the alphabetically last directory under `.anthril/audits/` that is not `latest/`. Warn the user that the marker was missing and you've inferred the audit ID by sort order.
3. If `.anthril/audits/` is empty, abort: "No prior audit found. Start a fresh audit with `/software-development:application-audit` instead."

### 2. Resolve which agents to re-dispatch

`$ARGUMENTS` contains the user's argument list.

- If `$ARGUMENTS` contains the literal word `all`, the target list is every agent that has at least one *answered* question file in `.anthril/questions/`.
- Otherwise, the target list is the set of agent names the user named, intersected with the set of agents that have answered question files.
- If a named agent has no answered question files, surface that to the user and skip it.

To detect "answered" status, run `bash "${CLAUDE_PLUGIN_ROOT}/skills/application-audit/scripts/collect-open-questions.sh" .` — it emits JSON of the *unanswered* questions. Anything in `.anthril/questions/` that is **not** in that JSON is answered and ready to be consumed.

### 3. Re-dispatch the named auditors in parallel

For each target agent, dispatch the matching `application-audit-<name>` subagent type with these inputs (single message, multiple `Agent` tool uses):

- `target_dir` (cwd or whatever was used originally — recover from `.anthril/preset-profile.md`'s "Target" field if present)
- `audit_id` (recovered above)
- `profile_path`: `.anthril/preset-profile.md`
- `permissive_mode`: read from the profile
- `memex_mode`: re-run `bash "${CLAUDE_PLUGIN_ROOT}/skills/application-audit/scripts/check-memex.sh" .`
- `connected_mcps`: same as a normal run
- `resume_question_files`: the absolute paths of the agent's answered question files (so the agent reads them and incorporates the answers verbatim into its remediation)
- The reminder that the agent must **overwrite** its existing report at `.anthril/audits/<id>/agent-reports/<name>.md` rather than appending — the new report supersedes the old one.

### 4. Move resolved questions to `.resolved/`

Once all dispatched auditors return, for each target agent move every answered question file from `.anthril/questions/<agent>-*.md` to `.anthril/questions/.resolved/<agent>-*.md`. Use `Bash` for the move: `mv .anthril/questions/<agent>-N.md .anthril/questions/.resolved/`.

### 5. Re-run the open-questions gate

Run `collect-open-questions.sh` again.

- **If 0 pending:** continue to Phase 6 (validation), Phase 7 (synthesis), Phase 8 (report-back) of the parent skill — invoke them inline by reading `${CLAUDE_PLUGIN_ROOT}/skills/application-audit/SKILL.md` Phase 6 onward and executing those steps.
- **If still pending:** print a fresh halt summary listing the remaining open questions. Tell the user to answer those, then re-run `/audit-proceed`.

### 6. Edge cases

- **Named agent does not exist** — list the valid names and exit. Do not dispatch.
- **No answered files for any named agent** — tell the user which question files are still showing the `(awaiting answer)` placeholder and exit.
- **Audit folder for the recovered ID was deleted** — abort: "Audit `<id>` is no longer on disk. Start a fresh run with `/software-development:application-audit`."

## Hard rules

- **Read-only on project source.** Same as the parent skill — never `Edit`, never `Write` outside `.anthril/`.
- **Resume-only.** This command does not start a new audit. If no prior run exists, point the user at the parent skill.
- **Verbatim user answers.** Auditors must incorporate the user's answers into their remediation steps without paraphrasing key technical claims (versions, file paths, config flags).
