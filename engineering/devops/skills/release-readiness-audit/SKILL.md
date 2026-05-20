---
name: release-readiness-audit
description: Pre-production go/no-go gate. Given a branch or diff, assesses migration safety, rollback path, config drift, runbook coverage, monitoring coverage, and deploy strategy fit. Static, live, and runtime (canary smoke) modes.
argument-hint: [--base main]
allowed-tools: Read Grep Glob Write Edit Bash(bash:*) Agent
effort: high
---

# Release Readiness Audit

## When to use

Run this skill when the user mentions:
- Release readiness, pre-deploy check, go/no-go
- Migration safety, destructive DDL review
- Rollback plan, revert safety
- Canary, blue-green, rolling deploy strategy
- Feature-flag coverage for a release

Integrative skill — pulls signal from CI status, Postgres schema, feature-flag config, and git history. Assesses migration safety (destructive DDL vs additive-only, backfill plan, lock duration), rollback path (forward-only changes flagged, feature-flag coverage, revert safety), config and secrets drift, runbook existence for new code paths, monitoring coverage for the new surface, and deploy strategy fit. Produces a go/no-go verdict with pre-deploy checklist, post-deploy checklist, and a rollback procedure document.

## Before You Start

1. **Determine operating mode.** `--live` requires a staging environment reachable via env (`STAGING_URL`, `PROD_URL`, `DB_STAGING_URL`). `--runtime` runs a canary smoke test against a non-prod target — refuses prod without `--i-really-mean-prod`.
2. **Identify the change scope.** Run `scripts/diff-scope.sh --base <branch>` to list changed files, migrations, env var additions, new external calls, new dependencies.
3. **Load `.release-ignore`** for suppressions (e.g., a known destructive migration that has a separately-documented backfill).

## User Context

$ARGUMENTS

Change scope: !`bash "${CLAUDE_PLUGIN_ROOT}/skills/release-readiness-audit/scripts/diff-scope.sh"`

---

## Audit Phases

### Phase 1: Change Scope

Catalogue (from `diff-scope.sh`):

- Changed files by category (code / migrations / config / CI / docs / infra)
- DB migration files introduced
- New env vars (vs `.env.example` or similar)
- New external API calls (grep for `fetch`, `axios`, `requests.get`, etc., in the diff)
- New dependencies (diff `package.json`, `requirements.txt`, `go.mod`)
- Breaking API changes (changed route signatures, renamed fields)

### Phase 2: Migration Safety

For every migration file in the diff:

- **Destructive DDL?** `DROP TABLE`, `DROP COLUMN`, `ALTER COLUMN TYPE`, `RENAME` on non-empty tables, `NOT NULL` additions without default, `CHECK` additions that existing rows would violate → CRITICAL.
- **Backfill plan?** Does a backfill script or separate step exist for new NOT NULL columns?
- **Lock risk?** `ALTER TABLE` without `CONCURRENTLY`? Long-running migration on a large table?
- **Index creation?** `CREATE INDEX CONCURRENTLY` vs plain `CREATE INDEX`?
- **Additive-only path?** Best practice: expand, migrate reads, contract — three separate deploys.

If Supabase MCP is configured (and user opts in), query for row counts of affected tables in `--live` mode to size the risk.

### Phase 3: Rollback Path

For every change:
- **Code revert?** A simple `git revert` works if state hasn't mutated.
- **State change?** If the migration is destructive or the change writes new data in a new shape, forward-only — record the recovery plan (restore from backup? migrate back?).
- **Feature flag?** Is the change behind a flag so it can be turned off without a redeploy?
- **API consumer impact?** If an API contract changed, can external consumers handle both old and new responses during the roll-forward window?

Emit one rollback entry per material change into `rollback-procedure.md`.

### Phase 4: Config & Secrets Drift

- New env vars — are they documented in `.env.example` / README?
- Secrets that need rotation (e.g., a new third-party API key)?
- Config file changes — does staging/prod need updating before deploy?

### Phase 5: Runbook & Monitoring Coverage

- For every new code path (new route, new background job, new external integration), is there a runbook entry?
- For every new failure mode implicit in the change (new external dep = new outage cause), is there an alert?
- Query the observability-audit output if available (`observability-audit.json`) for gap signal.

### Phase 6: Deploy Strategy Fit

Shape the recommendation based on change type:

- **Backwards-incompatible API change** → expand/contract via two deploys; feature-flag consumers
- **DB destructive migration** → canary the migration (one replica first, then promote)
- **High-blast-radius change (auth, payments)** → canary with slow ramp + instant rollback gate
- **Additive-only code change** → rolling deploy OK
- **Dependency upgrade with shared deps** → blue-green recommended

Compare against what CI currently does; flag mismatches.

### Phase 7: Runtime Canary (opt-in)

If `--runtime` and a canary target is configured:
1. Deploy the change to a canary pod / preview environment.
2. Run the skill's built-in smoke test battery:
   - `GET /healthz` → 200
   - `GET /` → 200 with body non-empty
   - `GET /api/version` → matches expected new version
   - Trace-ID propagation check
3. Record pre/post metrics (error rate, p95 latency) from an observability endpoint (Prometheus or DD).
4. If the new error rate > 2× baseline OR p95 latency > 1.5× baseline → NO-GO.
5. Attach results to `canary-smoke-results.md`.

### Phase 8: Reporting

Render `release-readiness-audit.md` and `rollback-procedure.md` from templates.

Verdict decision:
- Any CRITICAL finding → **NO-GO**
- Any HIGH finding without documented mitigation → **NO-GO**
- All HIGH findings mitigated, MEDIUM findings documented → **GO WITH CAVEATS**
- All findings ≤ MEDIUM, runbook + alerts cover new paths → **GO**

---

## Scoring

Scored as a binary go/no-go on each of seven gates:

| Gate | Pass condition |
|---|---|
| G1. Migration safety | No destructive DDL without documented plan |
| G2. Rollback path | Every change has a documented rollback |
| G3. Config drift | New env vars documented and staged |
| G4. Runbook coverage | New code paths have runbook entries |
| G5. Monitoring coverage | New failure modes have alerts |
| G6. Deploy strategy fit | Strategy matches change shape |
| G7. Canary smoke (if `--runtime`) | Smoke tests pass within error/latency thresholds |

**Verdict:** GO / GO WITH CAVEATS / NO-GO.

---

## Important Principles

- **Destructive DDL without additive path is CRITICAL.** `DROP COLUMN` is a one-way door.
- **Forward-only is a red flag.** If the only recovery is "restore from backup", surface it.
- **Feature flags mean you can roll forward fast.** But only if the flag is wired up before the code is shipped.
- **"We tested it in staging" is not a rollback plan.**
- **A broken runbook link is worse than no runbook.**
- **Canary doesn't replace review.** It catches regressions, not design flaws.
- **Never run runtime tests against prod without explicit `--i-really-mean-prod`.**
- **Australian English. DD/MM/YYYY. Markdown-first.**

---

## Edge Cases

1. **Release from a release branch (not `main`).** Use `--base <release-branch>`; detect and note.
2. **Empty diff.** "No changes detected" — emit the shortest report and exit.
3. **Hotfix.** `$ARGUMENTS --hotfix` downgrades the skill to a stripped-down checklist focusing on rollback + monitoring only.
4. **Multi-service release.** Ask the user which services are in scope; audit each.
5. **Data migration (not DDL).** Runs separately from deploy; note as a "migration-only release".
6. **Rollback of a previous release.** Audit the revert as its own release — same gates.
7. **Canary smoke test requires prod data access.** Refuse; canary should exercise synthetic traffic.
