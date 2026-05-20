# resource-manager

Monitor and reclaim machine resources used by Claude Desktop, Claude Code sessions, and their MCP servers.

## What's in the box

| Component | Type | What it does |
|-----------|------|-------------|
| `kill-orphan-mcp` | Stop hook | On every Claude Code session end, terminate MCP child processes whose Claude parent has died. Never kills an MCP child with a live parent. Never blocks the turn. Logs to `$CLAUDE_PLUGIN_DATA/orphans.log`. |
| `/resource-dashboard` | Skill | Launch a localhost browser dashboard (`http://127.0.0.1:8765`) showing the live Claude process tree, MCP servers, orphans, total memory, and a rolling memory chart. |
| `/resource-dashboard-stop` | Skill | Gracefully shut the dashboard down. |
| `/mcp-server-audit` | Skill | Enumerate every MCP server registered in user / project / plugin configs, cross-reference against live child processes, and recommend which to disable or move to a narrower scope. Read-only by default. |
| `/resource-snapshot` | Skill | One-shot markdown report of the same process data, no server required. |

## Why

A typical machine running Claude Desktop + Claude Code + VS Code Claude extension spawns ~15–25 Claude-family processes plus one MCP child per session per registered MCP server. Without guardrails, crashed sessions leave orphaned MCP children, and user-scoped MCP servers multiply linearly with open sessions. This plugin gives you visibility and a clean-up path.

## Safety

- The dashboard binds to `127.0.0.1` only. Not reachable from other machines.
- The dashboard's `POST /api/kill/<pid>` endpoint rejects (HTTP 403) any PID that is **not** both (a) classified as an MCP server and (b) flagged as orphan.
- The Stop hook always exits 0. A broken hook cannot block `/stop`.
- No config edits happen automatically. `/mcp-server-audit` recommends patches; the user approves each file edit.
- No external network, no telemetry, no dependencies outside the Python standard library (`psutil` is used if present, with a stdlib fallback path).

## Requirements

- Python 3.8+ on `PATH` (Windows, macOS, Linux).
- Optional: `pip install psutil` for faster process enumeration.
- A modern browser for the dashboard.

## Install

Add the Anthril plugin marketplace and enable `resource-manager`:

```
/plugin marketplace add anthril/official-claude-plugins
/plugin install resource-manager@anthril-claude-plugins
```

Restart Claude Code. The Stop hook begins firing immediately; skills are available via `/resource-dashboard`, etc.

## File layout

```
resource-manager/
├── .claude-plugin/plugin.json
├── hooks/
│   ├── hooks.json
│   └── scripts/{kill-orphan-mcp.sh, kill-orphan-mcp.py}
├── scripts/
│   ├── process_inspector.py   # shared: enumerate + classify Claude-family processes
│   ├── mcp_config_scanner.py  # shared: scan .claude.json / .mcp.json / settings.json
│   └── dashboard_server.py    # stdlib HTTP server
├── assets/dashboard.html      # single-page UI
├── skills/{resource-dashboard,resource-dashboard-stop,mcp-server-audit,resource-snapshot}/SKILL.md
└── settings.json
```
