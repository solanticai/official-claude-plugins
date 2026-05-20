---
name: resource-snapshot
description: Generate a one-shot markdown report of the Claude process tree, MCP servers, orphans, and total memory — no dashboard required
allowed-tools: Bash
effort: low
---

# Resource Snapshot

## Skill Metadata
- **Skill ID:** resource-snapshot
- **Category:** Developer Tools / Observability
- **Output:** Markdown report (stdout)
- **Complexity:** Low
- **Estimated Completion:** < 15 seconds

---

## Description

Prints the same data the `/resource-dashboard` shows, but as a one-shot markdown report for use inside a chat or a CI log. No server required.

---

## Usage

```
/resource-snapshot
```

This skill takes no arguments. `$ARGUMENTS` is intentionally ignored — the snapshot is always the full enumeration.

---

## Requirements

- **Python 3.8+** must be on `PATH`. The bundled enumerator script (`scripts/process_inspector.py`) uses only the standard library — no `pip install` needed.
- **Bash** for invocation. On Windows, this runs under Git Bash, WSL, or the Claude Code shell harness.

---

## Execution

Run with **Bash**:

### Step 1 — Enumerate

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/process_inspector.py" > /tmp/resource-snapshot.json
```

### Step 2 — Render

Produce markdown in this order:

1. **Totals** — claude processes, MCP servers, orphans, codex processes, total memory MB.
2. **Claude process tree** — table of PID, label, parent PID, memory MB, sorted by memory descending.
3. **MCP servers** — table of PID, parent PID, parent label, memory MB, orphan flag.
4. **Orphan warning** — if `orphans > 0`, list each orphan's PID and command line and note that the Stop hook will clean them up on the next session end, or the dashboard's Kill button can remove them immediately.
5. **Codex (informational)** — count and total memory; include the note that Codex is launched by the `openai.chatgpt` VS Code extension at VS Code startup.

Do the rendering in the conversation — read the JSON file you wrote and format as markdown tables.

---

## Notes

- Cross-platform: works on Windows, macOS, and Linux with stdlib Python.
- No side effects.
