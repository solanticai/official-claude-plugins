---
name: db-bootstrap
description: Interactive wizard — dispatches to the right database-design skill given the user's starting point (narrative / existing schema / domain spec).
argument-hint: [--from-narrative | --from-existing-schema | --from-domain-spec]
---

# DB Bootstrap

Interactive wizard for getting started with database-design.

## Flow

1. **Welcome + intent check.** Ask via AskUserQuestion:
   - "What do you have to start from?"
     - Just a description of the application (narrative)
     - An existing Postgres / Supabase schema (audit + improve)
     - A formal domain specification document
     - A list of business entities and their relationships

2. **Dispatch:**
   - **Narrative** → invoke `/database-design:business-data-model-designer`
   - **Existing schema** → invoke `/database-design:postgres-schema-audit`
   - **Domain spec** → invoke `/database-design:supabase-schema-bootstrap`
   - **Entity list** → invoke `/database-design:erd-generator`

3. **Always follow with** (after the first skill completes):
   - Ask: do you need RLS? → `/database-design:rls-policy-designer`
   - Ask: do you need a migration plan? → `/database-design:migration-plan-builder`
   - Ask: do you need an index review? → `/database-design:index-strategy-planner`

## Behavioural Rules

- **Don't run all skills automatically.** Each is heavy; ask before invoking next.
- **Confirm Supabase MCP availability** before any skill that needs it.
- **Pass context forward.** The schema produced by step 2 informs step 3.
- **Australian English throughout.**

## Error Handling

- **Supabase MCP unavailable** — proceed with user-pasted schema text; flag the degraded mode.
- **No starting input** — dispatch to `business-data-model-designer` with an intake conversation.
- **Multiple skills needed in one session** — surface that this is a heavy session; recommend saving intermediate outputs as files for review.
