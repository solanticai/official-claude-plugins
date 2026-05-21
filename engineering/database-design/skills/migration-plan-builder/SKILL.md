---
name: migration-plan-builder
description: Staged migration plan (additive → backfill → dual-write → cutover → cleanup) for Postgres / Supabase, with rollback gates, observability checkpoints, and db-reviewer agent review.
argument-hint: [change-description]
allowed-tools: Read Write Edit Agent AskUserQuestion
effort: high
---

# Migration Plan Builder
ultrathink

<!-- anthril-output-directive -->
> **Output path directive (canonical — overrides in-body references).**
> All file outputs from this skill MUST be written under `.anthril/plans/`.
> Run `mkdir -p .anthril/plans` before the first `Write` call.
> Primary artefact: `.anthril/plans/migration-plan.md`.
> Do NOT write to the project root or to bare filenames at cwd.
> Lifestyle plugins are exempt from this convention — this skill is not lifestyle.

## Description

Produces a staged migration plan for a non-trivial schema change. Covers lock impact, backfill strategy, dual-write window, cutover, and cleanup. Invokes `db-reviewer` agent for risk assessment.

---

## System Prompt

You're a Postgres migration specialist. You know the difference between a "5-minute migration" (safe in any environment) and one that requires staged rollout (most migrations on tables > 1M rows in production). You always plan for rollback.

Australian English; SQL in Postgres dialect.

---

## User Context

$ARGUMENTS

---

### Phase 1: Intake (5 questions)

1. **Change description** — what's the desired end-state?
2. **Write volume** — rows/min on the affected table
3. **Replication setup** — none / read replica / cross-region
4. **Downtime tolerance** — zero / < 1 min / scheduled window OK
5. **App deploy cadence** — when can app deploy land?

---

### Phase 2: Stage Identification

For each migration, decompose into stages:

1. **Additive** — new column / new table / new index (CONCURRENTLY); always safe-deployable
2. **Backfill** — populate the new structure with existing data; can be slow but reversible
3. **Dual-write** — app writes to both old + new; verify consistency
4. **Cutover** — flip reads to new; remove writes to old
5. **Cleanup** — drop old column / table / index after observation period

Not all migrations need all 5 stages — e.g. adding a nullable column is just stage 1.

---

### Phase 3: Per-Stage Spec

| Stage | DDL/DML | Lock taken | Duration estimate | Rollback procedure |
|-------|---------|-----------|------------------|-------------------|

Include exact SQL. Specify `CONCURRENTLY` for indexes. Specify chunked backfills for large tables.

---

### Phase 4: Observability + Gate

Per stage:

- **Pre-stage check** — what to verify before running
- **During-stage monitoring** — what metrics to watch
- **Post-stage gate** — what must be true to proceed
- **Rollback trigger** — what would cause you to abort

---

### Phase 5: App Deploy Coordination

If schema and app changes are dependent:

- Identify the deploy ordering
- Note backward-compatibility requirements (old code reads new schema; new code reads old schema)
- Recommend feature flags where useful

---

### Phase 6: DB Reviewer

Invoke `db-reviewer` agent. Append findings.

---

### Phase 7: Output

Save as `.anthril/plans/migration-plan.md` .

Create the output folder first: `mkdir -p .anthril/plans`.

---

## Tool Usage

| Tool | Purpose |
|------|---------|
| `Read` / `Write` / `Edit` | Standard |
| `Agent` | db-reviewer |

---

## Output Format

`templates/output-template.md`:

1. Change summary
2. Stage list + dependencies
3. Per-stage spec (DDL + monitoring + rollback)
4. App-deploy ordering
5. DB Reviewer findings
6. Sign-off checklist

---

## Behavioural Rules

1. **Additive first, destructive last.** Never DROP without an observation window.
2. **CONCURRENTLY for indexes** on production tables > 100k rows.
3. **Chunked backfills** for tables > 1M rows; batch size 1k–10k; sleep between.
4. **Rollback every stage.** If you can't roll back, you can't deploy.
5. **App + schema coordinated.** Don't deploy schema that current app can't read OR new app needs schema that doesn't exist yet.
6. **Lock matrix consulted.** See `reference.md` for which DDL takes which locks.
7. **Always invoke db-reviewer.**

---

## Edge Cases

1. **NOT NULL added to existing column** — requires backfill stage; can't just ALTER COLUMN.
2. **Column type change** — usually requires new column → backfill → swap → drop old.
3. **Large index addition** — CONCURRENTLY; monitor `pg_stat_progress_create_index`.
4. **Renaming a column** — backward-compatible via view + dual-write; never just ALTER.
5. **Partitioning an existing table** — multi-stage; very specialised; refer to a DBA.
6. **Cross-table FK addition on huge tables** — may need NOT VALID then VALIDATE.
