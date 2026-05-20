# Example Launch — Resource Dashboard

A successful launch on a fresh workstation. The server was not already running; the script started a detached Python process, polled the health endpoint, and opened the browser.

---

## User invocation

```
/resource-dashboard
```

## Expected console output

```
Dashboard launched at http://127.0.0.1:8765 (PID 24812)
Bind: 127.0.0.1 only — not reachable from other machines
Run /resource-dashboard-stop to shut it down.
```

## Expected browser tab

The dashboard opens with three panels:

1. **Process tree** — Claude Desktop (1 root), Claude Code CLI sessions (2), VS Code extension (1), and child subagent processes shown indented.
2. **MCP servers** — 3 healthy MCP servers (parent labels visible) and a warning row for any orphan whose Claude parent has died.
3. **Memory chart** — rolling 2-minute window, sampled at 5 s intervals, separated by Claude family / MCP / Codex.

A "Kill all orphans" button is enabled only when `orphan_count > 0`. Clicking it issues `POST /api/kill-orphans`; the server validates each candidate PID is (a) classified as an MCP server and (b) flagged orphan, refusing any other PID with HTTP 403.

## Custom port

```
/resource-dashboard --port 9000
```

```
Dashboard launched at http://127.0.0.1:9000 (PID 24813)
```

## Already running

If a previous session left the server alive, the launch script detects it via the health check and re-opens the browser without spawning a duplicate:

```
Dashboard already running at http://127.0.0.1:8765
Opening browser...
```

## Shutdown

```
/resource-dashboard-stop
```

Server stopped gracefully (SIGTERM); orphan-kill state is forgotten between runs.
