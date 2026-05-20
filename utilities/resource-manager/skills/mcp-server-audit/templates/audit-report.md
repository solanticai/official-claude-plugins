# MCP Server Audit — `{{target_dir}}` — {{date}}

## Summary

| Metric | Value |
|---|---:|
| Registered servers | {{total_servers}} |
| Enabled | {{enabled_count}} |
| Disabled | {{disabled_count}} |
| User-scope | {{user_scope_count}} |
| Project-scope | {{project_scope_count}} |
| Plugin-scope | {{plugin_scope_count}} |
| Duplicates (across scopes) | {{duplicate_count}} |
| Live MCP child processes (this session) | {{live_child_count}} |
| Memory held by MCP children (MB) | {{mcp_memory_mb}} |

## Server table

| Name | Scope | Status | Live | Memory (MB) | Config path |
|---|---|---|---:|---:|---|
{{server_rows}}

## Recommendations

{{recommendations}}

{{#if duplicate_count}}
## Duplicate warnings

{{duplicate_list}}
{{/if}}

## Next step

Run with explicit approval per change. This skill will read each target file, show the surrounding JSON, then apply the proposed patch with your approval.
