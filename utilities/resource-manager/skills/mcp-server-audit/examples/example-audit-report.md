# Example Audit Report — MCP Server Audit

A realistic report for a developer with three MCP servers at user scope, two more at project scope (one duplicating a user-scope server), and a plugin-shipped MCP. The audit was run from `C:/Development/some-project`.

---

# MCP Server Audit — `C:/Development/some-project` — 2026-04-25

## Summary

| Metric | Value |
|---|---:|
| Registered servers | 6 |
| Enabled | 5 |
| Disabled | 1 |
| User-scope | 3 |
| Project-scope | 2 |
| Plugin-scope | 1 |
| Duplicates (across scopes) | 1 |
| Live MCP child processes (this session) | 4 |
| Memory held by MCP children (MB) | 312 |

## Server table

| Name | Scope | Status | Live | Memory (MB) | Config path |
|---|---|---|---:|---:|---|
| supabase | user | enabled | 1 | 86 | `~/.claude/settings.json` |
| postgres | user | enabled | 1 | 71 | `~/.claude/settings.json` |
| github | user | enabled | 1 | 92 | `~/.claude/settings.json` |
| supabase | project | enabled | 1 | 63 | `.claude/settings.json` (DUPLICATE) |
| sentry | project | enabled | 0 | 0 | `.claude/settings.json` |
| memex | plugin | disabled | 0 | 0 | `.claude-plugin/memex/settings.json` |

## Recommendations

### 1. Resolve duplicate: `supabase`

The same server name is registered at **user** scope (`~/.claude/settings.json`) and **project** scope (`.claude/settings.json`). Project scope wins, so the user-scope entry never serves this project — but it still spawns a child in any other project that opens. Two live instances are running right now, which is wasted memory.

**Fix**: keep one. Recommended — keep project scope, disable user scope:

```json
// ~/.claude/settings.json — change disabled flag for "supabase"
{
  "mcpServers": {
    "supabase": {
      "command": "...",
      "args": ["..."],
      "disabled": true   // <-- add this
    }
  }
}
```

### 2. Narrow `github`: scope-down to projects that use it

`github` is registered at user scope and runs in every session, but the current session has used it 0 times. If only ~30% of your projects use GitHub, move it to per-project scope.

**Fix**: remove from `~/.claude/settings.json`, add to `.claude/settings.json` in each repo that needs it.

### 3. `sentry` is registered but never spawned this session

It's enabled at project scope but no Claude session in this project has invoked it. Either remove it (if unused) or keep it (if you sometimes need it — it's not costing memory unless invoked).

## Duplicate warnings

- **`supabase`** at both user and project scope — see Recommendation 1.

## Next step

Run with explicit approval per change:

```
> Apply Recommendation 1
```

This skill will read the target file, show the surrounding JSON, then apply the disable flag with your approval.
