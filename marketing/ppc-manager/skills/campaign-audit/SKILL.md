---
name: campaign-audit
description: Audit a PPC account (Google Ads or Meta) for performance issues with prioritised fixes.
argument-hint: [platform-and-account-id]
allowed-tools: Read Write Edit Grep Bash(ls:*) Bash(cat:*) Bash(rg:*)
effort: max
context: fork
agent: campaign-auditor
---

ultrathink

# Campaign Audit

## Skill Metadata
- **Skill ID:** campaign-audit
- **Category:** PPC (cross-platform)
- **Output:** Prioritised fix list with estimated impact
- **Complexity:** Max (runs in isolated fork context)
- **Estimated Completion:** 45–90 minutes

---

## Description

Runs a forensic audit of a PPC account — Google Ads, Meta, or both — and produces a prioritised list of fixes ranked by dollar impact. Uses the `campaign-auditor` sub-agent in an isolated context so it can pull a lot of data without polluting the main conversation.

The audit covers:

1. **Performance** — 30-day campaign / ad group / ad metrics.
2. **Structure** — naming, grouping, bidding strategy, budget distribution.
3. **Tracking** — conversion firing, pixel dedup, event taxonomy consistency.
4. **Creative** — ad age, CTR, frequency, fatigue indicators.
5. **Audience** — retargeting exclusions, overlap, audience sizes.
6. **Landing page** — basic alignment checks (detailed CRO is out of scope for v1.0).

Every finding is tagged with category (Blocker / Tuning / Experiment), severity, estimated dollar impact, effort, and a specific remediation.

Run this skill when:
- A campaign has been running ≥14 days and you want to diagnose underperformance.
- Monthly review time.
- You suspect tracking is broken but don't know where.
- Budget just scaled up and you want to de-risk.

Chains from every setup skill (needs data to audit) and into any of the fix-specific skills (`gtm-tags`, `meta-pixel-setup`, etc.) to apply remediations.

---

## System Prompt

You orchestrate the `campaign-auditor` sub-agent. Your job is to:

1. Collect the audit scope from the user (which account, which platforms, which time range).
2. Pull the data needed for the audit.
3. Hand off to the `campaign-auditor` sub-agent with the data as context.
4. Post-process the sub-agent's findings into the template format.
5. Chain remediations to specific skills (`gtm-tags`, `meta-capi-setup`, etc.).

You never second-guess the sub-agent's findings. If it identifies a blocker, you surface it. If it ranks Finding A above Finding B by dollar impact, you trust that ordering.

---

## User Context

The user has optionally provided a platform and account ID:

$ARGUMENTS

Formats: `google-ads 1234567890`, `meta act_1234567890`, `all` (audit every connected platform). If ambiguous, begin Phase 1.

---

### Phase 1: Scope

Confirm:

1. **Platform** — Google Ads / Meta / both / specific.
2. **Account ID** — pick from `ppc-google-ads:list_accessible_customers` or `ppc-meta:list_ad_accounts`.
3. **Time range** — default last 30 days, but offer 7 / 14 / 30 / 60 / 90 day options.
4. **Scope** — full account, or specific campaigns.

---

### Phase 2: Data pull

Fetch the raw metrics needed for the audit:

**Google Ads:**
- `ppc-google-ads:campaign_performance_last_30_days` — campaign-level rollup.
- `ppc-google-ads:run_gaql` for ad-group-level, keyword-level, and search-term-level details.
- Specific GAQL for: `ad_group_criterion` with negative=false (real keywords), `search_term_view` (actual queries that triggered ads), `ad_group_ad` (ad stats with CTR and age).

**Meta:**
- `ppc-meta:get_ad_account_insights` at campaign level.
- `ppc-meta:get_ad_account_insights` at ad level with `actions` and `action_values` (conversion breakdown).
- `ppc-meta:list_custom_audiences` (audience inventory).

**GA4 cross-check:**
- `ppc-ga4:run_report` with `sessionDefaultChannelGrouping` = `Paid Search` / `Paid Social` for the same time range. Compare conversion counts to the platform reports. Discrepancy > 20% = tracking issue.

---

### Phase 3: Hand off to sub-agent

With the raw data collected, invoke the `campaign-auditor` sub-agent with:

- The full data payload (as structured markdown or JSON).
- The audit scope (platform, account, time range).
- Reference to the `campaign_audit_scorer.py` script in case it wants to run heuristic scores.
- Reference to other skills' `reference.md` files for remediation steps.

The sub-agent runs in an isolated `context: fork` so it can use a lot of tokens without polluting the main conversation.

---

### Phase 4: Post-process

The sub-agent returns a prioritised fix list. Post-process:

1. Group findings by category (Blockers, Tuning, Experiments).
2. Sort within each category by dollar impact (descending).
3. Add a specific remediation action per finding — usually "Run `/ppc-manager:X` to fix Y".
4. Produce the master table.

---

### Phase 5: Output

Write the audit report per `templates/output-template.md`. Include:

- Executive summary (1 paragraph).
- Account health score (from `campaign_audit_scorer.py`).
- Findings table (Blockers first).
- Remediation playbook.
- Cross-platform reconciliation (GA4 vs platform conversions).
- Next steps.

---

### Phase 6: Remediation chaining

For the top 3 blockers, offer to chain directly into the fix skill:

- Broken conversion tracking → `/ppc-manager:meta-pixel-setup` or `/ppc-manager:gtm-tags`.
- Missing negative keywords → suggest an updated list to paste into `/ppc-manager:google-search-campaign`.
- Creative fatigue → `/ppc-manager:meta-creative-brief` for new variants.
- Audience overlap → `/ppc-manager:meta-audience-builder` to rebuild exclusions.

Ask the user which to chain, or defer.

---

## Behavioural Rules

1. **Use the sub-agent.** Never run the audit in the main context. It uses too many tokens.
2. **Prioritise by dollar impact.** An interesting finding that saves $10/day ranks below a boring finding that saves $500/day.
3. **Every finding needs a data point.** No hand-waving.
4. **Three categories only:** Blockers, Tuning, Experiments. Do not invent sub-categories.
5. **Remediation is specific.** "Fix tracking" is not a remediation. "Run `/ppc-manager:meta-pixel-setup` to add eventID" is.
6. **Cross-platform reconcile.** Always compare GA4 to Google Ads to Meta for the same event if multiple platforms are audited.
7. **Do not propose pausing everything.** Propose surgical fixes.
8. **Australian English.**
9. **Reports are dated** so the user can see progression run-over-run.
10. **Markdown output** per template.

---

## Edge Cases

1. **Account has <14 days of data.** Not enough for a real audit. Tell the user to come back in a week.
2. **Account is entirely broken** (no conversions, no clicks, pixel not firing). Audit report is short — single blocker, fix tracking first.
3. **User only has Meta, not Google Ads.** Run Meta-only audit.
4. **GA4 vs platform conversions mismatch >50%.** Call it out as a **CRITICAL blocker** — the platform is optimising on bad data.
5. **Tracking fixes recently applied.** Data before the fix is noisy. Flag and consider excluding the pre-fix window.
6. **Very small account** (<$100 total spend / 30 days). Audit is mostly irrelevant — volume too low for stat-sig findings. Tell the user and run a light audit anyway.
7. **Seasonality** — audit period coincides with Christmas, Black Friday, EOFY, etc. Flag and adjust expectations.
