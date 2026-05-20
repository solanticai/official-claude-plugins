---
name: resource-dashboard-stop
description: Shut down the Resource Manager localhost dashboard server
argument-hint: [--port 8765]
allowed-tools: Bash
effort: low
---

# Resource Dashboard Stop

## Description

Gracefully stops the Resource Manager dashboard (started by `/resource-dashboard`). Sends `POST /api/shutdown`; falls back to killing the PID recorded in the dashboard's pid-file if the HTTP shutdown fails.

---

## Usage

```
/resource-dashboard-stop
/resource-dashboard-stop --port 9000
```

---

## Requirements

- **Bash** invocation environment.
- **curl** for the graceful HTTP shutdown.
- Platform-specific kill fallback:
  - **Windows** (Git Bash / MSYS) — `taskkill`.
  - **macOS / Linux** — `kill`.

---

## Execution

Run with **Bash**:

### Step 1: Parse port

Default `PORT=8765`; override from `$ARGUMENTS` if `--port N` present.

### Step 2: Try graceful shutdown

```bash
if curl -s --max-time 2 -X POST "http://127.0.0.1:${PORT}/api/shutdown" > /dev/null; then
  echo "Dashboard on port ${PORT} stopped."
  exit 0
fi
```

### Step 3: Fallback — kill by pid-file

The dashboard writes its PID to `$CLAUDE_PLUGIN_DATA/dashboard.pid` (or `~/.claude/plugin-data/resource-manager/dashboard.pid`).

```bash
PIDFILE="${CLAUDE_PLUGIN_DATA:-$HOME/.claude/plugin-data/resource-manager}/dashboard.pid"
if [ -f "$PIDFILE" ]; then
  PID=$(cat "$PIDFILE")
  if [ -n "$PID" ]; then
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
      taskkill //PID "$PID" //F > /dev/null 2>&1 || true
    else
      kill "$PID" 2>/dev/null || true
    fi
    rm -f "$PIDFILE"
    echo "Dashboard (pid ${PID}) stopped via pid-file."
    exit 0
  fi
fi

echo "No dashboard running on port ${PORT}."
```

---

## Notes

- Idempotent — safe to run when no dashboard is running.
- Does not touch any non-dashboard processes.
