# Resource Snapshot — {{timestamp_utc}}

## Totals

| Metric | Value |
|---|---:|
| Claude processes | {{claude_count}} |
| MCP servers | {{mcp_count}} |
| Orphan MCP servers | {{orphan_count}} |
| Codex processes | {{codex_count}} |
| Total memory (MB) | {{total_memory_mb}} |

## Claude process tree

| PID | Label | Parent PID | Memory (MB) |
|---:|---|---:|---:|
{{claude_rows}}

## MCP servers

| PID | Parent PID | Parent label | Memory (MB) | Orphan |
|---:|---:|---|---:|:---:|
{{mcp_rows}}

{{#if orphan_count}}
## Orphan warning

{{orphan_count}} orphan MCP server(s) detected:

{{orphan_list}}

The Stop hook will clean these up on the next session end. To remove immediately, use the `/resource-dashboard` Kill button.
{{/if}}

## Codex (informational)

- {{codex_count}} process(es) · {{codex_memory_mb}} MB. Codex is launched by the `openai.chatgpt` VS Code extension at VS Code startup, not by Claude Code.

---

_Snapshot taken in {{elapsed_seconds}}s._
