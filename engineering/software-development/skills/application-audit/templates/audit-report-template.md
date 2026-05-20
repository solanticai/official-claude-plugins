# Application Audit — {{audit_id}}

| Field | Value |
|---|---|
| **Audit ID** | `{{audit_id}}` |
| **Generated** | {{generated_at}} |
| **Target** | `{{target_dir}}` |
| **Profile** | [.anthril/preset-profile.md](../../preset-profile.md) |
| **Permissive mode** | {{permissive_mode}} |
| **Memex consulted** | {{memex_mode}} |
| **Auditors run** | {{agent_count}} |
| **Findings (confirmed)** | {{confirmed_count}} ({{critical_count}} CRITICAL, {{high_count}} HIGH, {{medium_count}} MEDIUM, {{low_count}} LOW, {{info_count}} INFO) |
| **Findings (rejected)** | {{rejected_count}} |
| **Validator confidence** | {{validator_confidence_pct}}% |

---

## 1. Executive Summary

Top {{top_n}} findings ranked by severity × confidence × scope.

| # | Severity | Domain | Title | Evidence |
|---|---|---|---|---|
{{top_findings_table}}

---

## 2. Findings by Domain

{{per_domain_sections}}

> Each domain section contains the auditor's confirmed findings only, in the
> validator's calibrated severity order. Rejected findings are listed in §6.

---

## 3. Cross-Cutting Risks

Findings that span more than one domain (e.g. an auth-cookie cache leak that
shows up in both server-client and security audits, or a connection-pool issue
that surfaces in both postgres and connection-limit audits).

{{cross_cutting_risks}}

---

## 4. Suggested Remediation Order

Apply fixes in this order to minimise rework and concentrate the early effort
on correctness/security:

1. **Security & correctness** — auth/RLS, service-role exposure, storage policies, function exposure, secret leaks.
2. **Server/client fundamentals** — Next.js 15 caching/rendering decisions, React 19 boundaries, two-client SSR pattern, middleware matcher.
3. **Connection hygiene** — pool sizing, transaction-mode prepared-statements, Realtime subscription lifecycle, dual-pooler stacking.
4. **Initial-load performance** — bundle analysis, third-party scripts, images, fonts, Tailwind scan paths.
5. **Measured DB optimisation** — `pg_stat_statements`-driven index work, bloat, advisor-recommended indexes.

{{remediation_steps}}

---

## 5. Open Questions Resolved During This Run

{{resolved_questions}}

> Empty if no auditor needed to file a question. Each entry shows the original
> question, the user's answer, and the agent that consumed it.

---

## 6. Rejected Findings (Validator Appendix)

For audit transparency. The validator rejected these findings because the
evidence was missing, fabricated, out-of-scope for this run, or duplicated.

{{rejected_findings_table}}

---

## 7. Run Metadata

- **Skill version:** {{skill_version}}
- **Plugin:** `software-development`
- **Auditor reports:** `.anthril/audits/{{audit_id}}/agent-reports/`
- **Validation sidecar:** `.anthril/audits/{{audit_id}}/validation.json`
- **JSON sidecar (this report):** `.anthril/audits/{{audit_id}}/REPORT.json`

> Re-run the audit any time. A new ID is generated on every run; old runs are
> preserved under `.anthril/audits/<id>/` for diffing. The latest run is also
> mirrored at `.anthril/audits/latest/`.
