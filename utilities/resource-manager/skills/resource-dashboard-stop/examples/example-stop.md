# Example Stop — Resource Dashboard Stop

Three realistic invocations: graceful shutdown succeeds, graceful fails and the PID-file fallback kicks in, and the no-op when no server is running.

---

## 1. Graceful shutdown (HTTP succeeds)

```
/resource-dashboard-stop
```

```
Dashboard on port 8765 stopped.
```

The skill issued `POST http://127.0.0.1:8765/api/shutdown` with a 2-second timeout. The server responded `204 No Content`, finished its in-flight request, and exited cleanly.

---

## 2. HTTP shutdown fails — PID-file fallback

If the dashboard process is hung or the API endpoint is unreachable, the skill falls back to killing the PID recorded in `$CLAUDE_PLUGIN_DATA/dashboard.pid`:

```
/resource-dashboard-stop --port 9000
```

```
Dashboard (pid 24812) stopped via pid-file.
```

On Windows the kill is `taskkill //PID 24812 //F`; on macOS / Linux it is `kill 24812`. The PID-file is removed afterwards so subsequent runs don't try to kill an already-dead PID.

---

## 3. No dashboard running

```
/resource-dashboard-stop
```

```
No dashboard running on port 8765.
```

Idempotent — safe to run when no dashboard is up. No errors, no side effects.

---

## Notes

- The skill never kills MCP servers, child processes, or anything other than the dashboard's own PID. Safe to invoke at any time.
- After this skill exits, `/resource-dashboard` can be re-run to start a fresh server.
