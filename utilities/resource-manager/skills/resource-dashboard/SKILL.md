---
name: resource-dashboard
description: Launch a localhost browser dashboard showing live Claude process tree, memory use, MCP servers, and orphan count
argument-hint: [--port 8765]
allowed-tools: Bash
effort: low
---

# Resource Dashboard

## Skill Metadata
- **Skill ID:** resource-dashboard
- **Category:** Developer Tools / Observability
- **Output:** Browser dashboard on `http://127.0.0.1:8765`
- **Complexity:** Low
- **Estimated Completion:** < 30 seconds

---

## Description

Starts the Resource Manager dashboard as a background localhost HTTP server (`127.0.0.1` only, no external exposure) and opens it in the default browser. The dashboard shows:

- Live Claude process tree (Desktop, Code CLI, VS Code extension, subprocess types)
- MCP server processes with parent/orphan status
- Total memory consumed by Claude-family + MCP + Codex
- MCP servers registered in user/project/plugin configs, with scope
- A rolling memory chart (last 2 minutes)
- A one-click "Kill all orphans" control (only ever kills MCP servers whose Claude parent has died)

The server keeps running after the skill exits. Use `/resource-dashboard-stop` to shut it down.

---

## Usage

```
/resource-dashboard
/resource-dashboard --port 9000
```

---

## Requirements

- **Python 3.8+** on `PATH` — the dashboard server is `scripts/dashboard_server.py` (stdlib only).
- **curl** for health-checking the bind port.
- **Bash** invocation environment.
- Platform-specific:
  - **Windows** — `powershell` (for detached launch and browser open).
  - **macOS** — `open`.
  - **Linux** — `xdg-open`, `nohup`.

---

## Execution

You are the dashboard launcher. Run these steps in order using **Bash**:

### Step 1: Parse arguments

Read `$ARGUMENTS`. Default `PORT=8765`. If the user passed `--port N`, use `N`.

### Step 2: Check if already running

```bash
if curl -s --max-time 1 "http://127.0.0.1:${PORT}/api/health" > /dev/null; then
  echo "Dashboard already running at http://127.0.0.1:${PORT}"
  # Proceed to open browser.
fi
```

### Step 3: Launch detached

On **Windows** (Git Bash / PowerShell):

```bash
powershell -NoProfile -Command "Start-Process -WindowStyle Hidden -FilePath python -ArgumentList @('\"${CLAUDE_PLUGIN_ROOT}/scripts/dashboard_server.py\"','--port','${PORT}')"
```

On **macOS / Linux**:

```bash
nohup python "${CLAUDE_PLUGIN_ROOT}/scripts/dashboard_server.py" --port "${PORT}" > /dev/null 2>&1 &
disown
```

### Step 4: Wait for port to open (max 5 s)

The 5-iteration cap matches the dashboard server's typical cold-start time on a slow VM (~3 s) plus headroom — anything beyond 5 s is a real failure, not a slow start.

```bash
for i in 1 2 3 4 5; do  # 5s cap: server cold-start budget
  if curl -s --max-time 1 "http://127.0.0.1:${PORT}/api/health" > /dev/null; then break; fi
  sleep 1
done
```

### Step 5: Open the browser

- Windows: `powershell -NoProfile -Command "Start-Process 'http://127.0.0.1:${PORT}'"`
- macOS: `open "http://127.0.0.1:${PORT}"`
- Linux: `xdg-open "http://127.0.0.1:${PORT}"`

### Step 6: Report

Print the URL and a one-line note: `Run /resource-dashboard-stop to shut it down.`

---

## Safety

- The dashboard binds to `127.0.0.1` only — it is **not** reachable from other machines.
- The kill endpoint refuses any PID that is not (a) classified as an MCP server and (b) flagged as orphan. Non-MCP PIDs and MCP servers with a live Claude parent return HTTP 403.
- No authentication is required because the bind is local-only and single-user.
