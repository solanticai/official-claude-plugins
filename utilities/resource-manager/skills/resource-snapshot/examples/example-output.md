# Example Output — Resource Snapshot

This file shows a realistic snapshot rendering. Generated with `/resource-snapshot` on a workstation running two concurrent Claude Code sessions plus three MCP servers.

---

# Resource Snapshot — 2026-04-25 14:32 UTC

## Totals

| Metric | Value |
|---|---:|
| Claude processes | 4 |
| MCP servers | 3 |
| Orphan MCP servers | 1 |
| Codex processes | 1 |
| Total memory (MB) | 1,842 |

## Claude process tree

| PID | Label | Parent PID | Memory (MB) |
|---:|---|---:|---:|
| 18432 | claude-code (lumioh) | 18419 | 612 |
| 18540 | claude-code (subagent) | 18432 | 287 |
| 19120 | claude-code (plugins-repo) | 18419 | 498 |
| 19284 | claude-code (subagent) | 19120 | 224 |

## MCP servers

| PID | Parent PID | Parent label | Memory (MB) | Orphan |
|---:|---:|---|---:|:---:|
| 18610 | 18432 | claude-code (lumioh) | 86 | — |
| 19245 | 19120 | claude-code (plugins-repo) | 71 | — |
| 14012 | 1 | init | 64 | ⚠ |

## Orphan warning

1 orphan MCP server detected:

- **PID 14012** — `node /opt/mcp-supabase/dist/index.js --stdio`
  - Parent process is `init` (1) — the original Claude session has exited but the MCP wasn't cleaned up.
  - Action: the Stop hook will clean this up on the next session end. To remove immediately, use the `/resource-dashboard` Kill button.

## Codex (informational)

- 1 process · 64 MB. Codex is launched by the `openai.chatgpt` VS Code extension at VS Code startup, not by Claude Code.

---

_Snapshot taken in 0.31s. Cross-platform: works on Windows, macOS, Linux with stdlib Python only._
