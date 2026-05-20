---
name: mcp-server-audit
description: Audit MCP server registrations across user, project, and plugin configs — report always-on servers, duplicates, and disable recommendations
argument-hint: [project-path]
allowed-tools: Bash Read
effort: low
---

# MCP Server Audit

## Skill Metadata
- **Skill ID:** mcp-server-audit
- **Category:** Developer Tools / Resource Management
- **Output:** Markdown report with disable recommendations
- **Complexity:** Low
- **Estimated Completion:** 1–2 minutes

---

## Description

Every Claude Code session spawns each **enabled** MCP server as a stdio child process — one process per session per server. Servers registered at **user scope** spawn everywhere; **project scope** only inside that project. Audit the current set-up, cross-reference against live child processes, and recommend which to narrow or disable.

---

## Usage

```
/mcp-server-audit
/mcp-server-audit C:/Development/some-project
```

---

## Requirements

- **Python 3.8+** on `PATH` — `scripts/mcp_config_scanner.py` and `scripts/process_inspector.py` use stdlib only.
- **Bash** invocation environment.
- **Read** access to the user-scope and project-scope MCP config files (`~/.claude/settings.json`, `<project>/.claude/settings.json`, plugin config files under `.claude-plugin/`).

---

## Execution

### Phase 1 — Collect

Run both scanners (Bash):

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/mcp_config_scanner.py" > /tmp/mcp-audit-configs.json
python "${CLAUDE_PLUGIN_ROOT}/scripts/process_inspector.py" > /tmp/mcp-audit-procs.json
```

If `$ARGUMENTS` names a directory, `cd` there before running `mcp_config_scanner.py` so project-scope configs are discovered.

### Phase 2 — Join & classify

For each entry in `entries`:

- Count live MCP-server processes whose `cmdline` references the same `command` + last `args` token (typically a script path). Use `mcp_servers` from the process snapshot.
- Label each as **always-on** (scope=user, not disabled), **project-only**, **plugin-only**, or **disabled**.
- Flag **duplicates** listed in the `duplicates` field — same server name at multiple scopes means it may double-start.

### Phase 3 — Report

Output markdown:

1. **Summary**: totals (enabled, disabled, user-scope, project-scope, plugin-scope), duplicate count, live MCP child count, total memory held by MCP children.
2. **Server table** — one row per registered server:
   - Name
   - Scope
   - Enabled / disabled
   - Live instances
   - Memory (sum of live instances)
   - Config path
3. **Recommendations section** — for each always-on server with ≥ 2 live instances or no live use in current session:
   - Exact config file to edit
   - One-line patch: add `"disabled": true` (show the surrounding JSON context from the actual file using `Read`).
   - Alternative: move from user scope to project scope, with before/after snippets.
4. **Duplicate warnings** — if the same server name appears at multiple scopes, explain precedence and recommend collapsing to a single scope.

### Phase 4 — Offer to apply

Do **not** edit configs automatically. Ask the user which recommendations they want to apply; then perform `Read`-then-`Edit` patches with their explicit approval for each file.

---

## Safety

- Read-only by default. Never edits config files without explicit user approval per file.
- Never kills live MCP processes. That's what `/resource-dashboard` and the Stop hook are for.
