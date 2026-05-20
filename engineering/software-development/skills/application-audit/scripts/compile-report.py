#!/usr/bin/env python3
"""compile-report.py — Render the final REPORT.md from validation.json + agent reports.

Inputs (all required):
  --validation <path>   Path to validation.json (the validator's calibrated output;
                        shape: matches templates/findings-schema.json).
  --reports-dir <path>  Directory of per-agent reports (used for the per-domain
                        sections and to look up bodies for confirmed findings).
  --profile <path>      Path to .anthril/preset-profile.md (for the run header).
  --audit-id <id>       The current audit ID (YYYYMMDD-HHMM[-N]).
  --target <path>       Project root (for the run header).
  --template <path>     Path to templates/audit-report-template.md.
  --out <path>          Where to write REPORT.md.

Output: a single markdown file at --out.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from collections import Counter, OrderedDict, defaultdict
from pathlib import Path
from typing import Dict, List, Any

SEVERITY_ORDER = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]
SEVERITY_RANK = {s: i for i, s in enumerate(SEVERITY_ORDER)}
CONFIDENCE_RANK = {"high": 0, "medium": 1, "low": 2}

DOMAIN_LABELS = OrderedDict([
    ("security", "Cross-cutting Security"),
    ("server-client", "Server / Client SSR"),
    ("client-connection", "Client Connections"),
    ("postgres", "Postgres / ORM"),
    ("connection-limit", "Connection Limits"),
    ("backend", "Backend"),
    ("frontend", "Frontend"),
    ("leak-detection", "Leak Detection"),
    ("bug-finder", "Bugs (Cross-cutting)"),
])


def rank_finding(f: Dict[str, Any]) -> tuple:
    """Sort key: severity, then confidence, then domain, then id."""
    sev = SEVERITY_RANK.get(f.get("severity", "INFO"), 4)
    conf = CONFIDENCE_RANK.get(f.get("confidence", "low"), 2)
    return (sev, conf, f.get("domain", "z"), f.get("id", "AA-999"))


def render_top_table(findings: List[Dict[str, Any]], n: int = 10) -> str:
    """Render only the data rows for the top-findings table — the header lives
    in the template so it doesn't duplicate."""
    if not findings:
        return "| _none_ | _none_ | _none_ | _no findings to rank_ | _none_ |"
    rows = []
    for i, f in enumerate(findings[:n], 1):
        first_evidence = ""
        ev = f.get("evidence") or []
        if ev:
            v = ev[0]
            first_evidence = v.get("value", "") if isinstance(v, dict) else str(v)
        title = f.get("title", "").replace("|", "\\|")
        rows.append(
            f"| {i} | {f.get('severity', '')} | {f.get('domain', '')} | {title} | `{first_evidence}` |"
        )
    return "\n".join(rows)


def render_per_domain_sections(findings: List[Dict[str, Any]]) -> str:
    by_domain: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for f in findings:
        by_domain[f.get("domain", "other")].append(f)

    out: List[str] = []
    for domain_key, label in DOMAIN_LABELS.items():
        bucket = by_domain.get(domain_key, [])
        if not bucket:
            continue
        out.append(f"### {label}")
        out.append("")
        out.append(f"_{len(bucket)} confirmed findings._")
        out.append("")
        for f in sorted(bucket, key=rank_finding):
            out.append(f"#### {f.get('id', '?')} — {f.get('title', '')}  `[{f.get('severity', '?')}]`")
            out.append("")
            if f.get("summary"):
                out.append(f.get("summary", "").strip())
                out.append("")
            ev = f.get("evidence") or []
            if ev:
                out.append("**Evidence:**")
                out.append("")
                for v in ev:
                    val = v.get("value", "") if isinstance(v, dict) else str(v)
                    obs = v.get("observation", "") if isinstance(v, dict) else ""
                    if obs:
                        out.append(f"- `{val}` — {obs}")
                    else:
                        out.append(f"- `{val}`")
                out.append("")
            steps = f.get("remediation_steps") or []
            if steps:
                out.append("**Remediation:**")
                out.append("")
                for i, s in enumerate(steps, 1):
                    out.append(f"{i}. {s}")
                out.append("")
            risks = f.get("risks") or []
            if risks:
                out.append("**Risks if left unfixed:**")
                out.append("")
                for r in risks:
                    out.append(f"- {r}")
                out.append("")
            verif = f.get("verification") or []
            if verif:
                out.append("**Verification:**")
                out.append("")
                for v in verif:
                    out.append(f"- {v}")
                out.append("")
            agents = f.get("agents") or [f.get("agent")] if f.get("agent") else []
            if agents:
                out.append(f"_Reported by: {', '.join(a for a in agents if a)}_")
                out.append("")
        out.append("")
    return "\n".join(out)


def render_cross_cutting(findings: List[Dict[str, Any]]) -> str:
    cross = [f for f in findings if len(f.get("agents") or []) > 1]
    if not cross:
        return "_No cross-cutting findings._"
    lines = []
    for f in sorted(cross, key=rank_finding):
        agents = ", ".join(f.get("agents", []))
        lines.append(f"- **{f.get('id', '?')}** ({f.get('severity', '?')}, {f.get('domain', '?')}) — {f.get('title', '')} _(agents: {agents})_")
    return "\n".join(lines)


def render_remediation_steps(findings: List[Dict[str, Any]]) -> str:
    """Group confirmed findings by phase and emit a flat ordered list."""
    PHASE_FOR_DOMAIN = {
        "security": 1,
        "server-client": 2,
        "client-connection": 3,
        "postgres": 3,
        "connection-limit": 3,
        "backend": 2,
        "frontend": 4,
        "leak-detection": 1,
        "bug-finder": 2,
    }
    PHASE_LABELS = {
        1: "Security & correctness",
        2: "Server/client fundamentals",
        3: "Connection hygiene",
        4: "Initial-load performance",
        5: "Measured DB optimisation",
    }
    by_phase: Dict[int, List[Dict[str, Any]]] = defaultdict(list)
    for f in findings:
        phase = PHASE_FOR_DOMAIN.get(f.get("domain", ""), 5)
        # CRITICAL/HIGH always pull into the earliest phase they belong to.
        by_phase[phase].append(f)

    out = []
    for phase in sorted(by_phase):
        out.append(f"**Phase {phase} — {PHASE_LABELS.get(phase, '')}**")
        out.append("")
        for f in sorted(by_phase[phase], key=rank_finding):
            out.append(f"- {f.get('id', '?')} `[{f.get('severity', '?')}]` — {f.get('title', '')}")
        out.append("")
    return "\n".join(out)


def render_resolved_questions(payload: Dict[str, Any]) -> str:
    questions = payload.get("open_questions_resolved") or []
    if not questions:
        return "_No open questions filed during this run._"
    out = []
    for q in questions:
        out.append(f"- **{q.get('agent', '?')}** — _Q:_ {q.get('question', '')}")
        if q.get("answer"):
            out.append(f"  - _A:_ {q['answer']}")
        if q.get("file"):
            out.append(f"  - _Source:_ `{q['file']}`")
    return "\n".join(out)


def render_rejected_findings(payload: Dict[str, Any]) -> str:
    rej = payload.get("rejected_findings") or []
    if not rej:
        return "_No findings were rejected by the validator._"
    rows = ["| Agent | Title | Reason |", "|---|---|---|"]
    for r in rej:
        rows.append(
            f"| {r.get('agent', '?')} | {r.get('title', '?').replace('|', '\\|')} | {r.get('reason', '?').replace('|', '\\|')} |"
        )
    return "\n".join(rows)


def main() -> int:
    p = argparse.ArgumentParser(description="Compile final audit report.")
    p.add_argument("--validation", required=True, type=Path)
    p.add_argument("--reports-dir", required=True, type=Path)
    p.add_argument("--profile", required=True, type=Path)
    p.add_argument("--audit-id", required=True)
    p.add_argument("--target", required=True)
    p.add_argument("--template", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    args = p.parse_args()

    if not args.validation.exists():
        print(f"ERROR: validation file missing: {args.validation}", file=sys.stderr)
        return 1
    if not args.template.exists():
        print(f"ERROR: template missing: {args.template}", file=sys.stderr)
        return 1

    payload = json.loads(args.validation.read_text(encoding="utf-8"))
    audit_meta = payload.get("audit", {})
    findings = payload.get("findings") or []
    confirmed = [f for f in findings if (f.get("validator_decision") or {}).get("status", "confirmed") in ("confirmed", "merged")]
    confirmed.sort(key=rank_finding)

    sev_counts = Counter(f.get("severity", "INFO") for f in confirmed)

    template = args.template.read_text(encoding="utf-8")

    permissive = audit_meta.get("permissive_mode", False)
    memex_mode = audit_meta.get("memex_mode", "none")
    validator_meta = audit_meta.get("validator", {})

    placeholders = {
        "{{audit_id}}": args.audit_id,
        "{{generated_at}}": dt.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "{{target_dir}}": args.target,
        "{{permissive_mode}}": "true (stack drift detected)" if permissive else "false",
        "{{memex_mode}}": memex_mode,
        "{{agent_count}}": str(len(audit_meta.get("agents_run") or [])),
        "{{confirmed_count}}": str(len(confirmed)),
        "{{rejected_count}}": str(validator_meta.get("rejected_count", len(payload.get("rejected_findings") or []))),
        "{{validator_confidence_pct}}": str(validator_meta.get("confidence_pct", 0)),
        "{{critical_count}}": str(sev_counts.get("CRITICAL", 0)),
        "{{high_count}}": str(sev_counts.get("HIGH", 0)),
        "{{medium_count}}": str(sev_counts.get("MEDIUM", 0)),
        "{{low_count}}": str(sev_counts.get("LOW", 0)),
        "{{info_count}}": str(sev_counts.get("INFO", 0)),
        "{{top_n}}": str(min(10, len(confirmed))),
        "{{top_findings_table}}": render_top_table(confirmed),
        "{{per_domain_sections}}": render_per_domain_sections(confirmed),
        "{{cross_cutting_risks}}": render_cross_cutting(confirmed),
        "{{remediation_steps}}": render_remediation_steps(confirmed),
        "{{resolved_questions}}": render_resolved_questions(payload),
        "{{rejected_findings_table}}": render_rejected_findings(payload),
        "{{skill_version}}": "1.0.0",
    }

    # Single-pass substitution. Any `{{...}}` sequence inside a substituted value
    # (e.g. an auditor titled the finding "{{ refactor }}") will not be re-processed,
    # because re.sub walks the source string once and leaves substituted text alone.
    # Keys must be the bare token (e.g. `audit_id`); the regex matches `{{ key }}`
    # with optional whitespace inside the braces.
    plain_keys = {k.strip("{} ").strip(): v for k, v in placeholders.items()}
    placeholder_re = re.compile(r"\{\{\s*([a-z_]+)\s*\}\}")

    def replace_one(m: "re.Match[str]") -> str:
        key = m.group(1)
        return plain_keys.get(key, m.group(0))

    rendered = placeholder_re.sub(replace_one, template)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(rendered, encoding="utf-8")
    print(f"Wrote {args.out} ({len(confirmed)} confirmed findings, {sev_counts.get('CRITICAL', 0)} CRITICAL)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
