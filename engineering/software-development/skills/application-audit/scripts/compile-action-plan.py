#!/usr/bin/env python3
"""compile-action-plan.py — Compile an executable action plan from validation.json.

Reads `.anthril/audits/<id>/validation.json` (the validator's calibrated output) and
emits two artifacts:

  - action-plan.json — machine-readable, mutable state for the /audit-work command.
    Conforms to templates/action-plan-schema.json.
  - ACTION-PLAN.md   — human-readable severity-grouped checklist.

Inputs (all required):
  --validation <path>   Path to validation.json.
  --audit-id <id>       Audit ID (YYYYMMDD-HHMM[-N]).
  --target <path>       Project root (recorded in the plan header).
  --out-json <path>     Where to write action-plan.json.
  --out-md <path>       Where to write ACTION-PLAN.md.

Optional:
  --merge-existing      If --out-json already exists, preserve status / notes /
                        files_touched / blockers per item id; new items get
                        status=pending. Without this flag, an existing file
                        is overwritten.

Sort order mirrors compile-report.py: phase asc, severity asc, confidence asc,
domain asc, id asc — so item.order reflects the recommended remediation sequence.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from collections import Counter, OrderedDict, defaultdict
from pathlib import Path
from typing import Any, Dict, List

SEVERITY_ORDER = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]
SEVERITY_RANK = {s: i for i, s in enumerate(SEVERITY_ORDER)}
CONFIDENCE_RANK = {"high": 0, "medium": 1, "low": 2}

# Mirrors compile-report.py:render_remediation_steps so REPORT.md and
# ACTION-PLAN.md agree on phase ordering.
PHASE_FOR_DOMAIN = {
    "security": 1,
    "leak-detection": 1,
    "server-client": 2,
    "backend": 2,
    "bug-finder": 2,
    "client-connection": 3,
    "postgres": 3,
    "connection-limit": 3,
    "frontend": 4,
}
PHASE_LABELS = {
    1: "Security & correctness",
    2: "Server/client fundamentals",
    3: "Connection hygiene",
    4: "Initial-load performance",
    5: "Measured DB optimisation",
}

DOMAIN_LABELS = OrderedDict([
    ("security", "Cross-cutting Security"),
    ("leak-detection", "Leak Detection"),
    ("server-client", "Server / Client SSR"),
    ("backend", "Backend"),
    ("bug-finder", "Bugs (Cross-cutting)"),
    ("client-connection", "Client Connections"),
    ("postgres", "Postgres / ORM"),
    ("connection-limit", "Connection Limits"),
    ("frontend", "Frontend"),
])

PRESERVED_STATE_KEYS = (
    "status",
    "started_at",
    "completed_at",
    "notes",
    "blockers",
    "files_touched",
    "git_branch",
)


def rank_finding(f: Dict[str, Any]) -> tuple:
    phase = PHASE_FOR_DOMAIN.get(f.get("domain", ""), 5)
    sev = SEVERITY_RANK.get(f.get("severity", "INFO"), 4)
    conf = CONFIDENCE_RANK.get(f.get("confidence", "low"), 2)
    return (phase, sev, conf, f.get("domain", "z"), f.get("id", "AA-999"))


def finding_to_item(f: Dict[str, Any]) -> Dict[str, Any]:
    """Project a validated finding into an action-plan item, with default state."""
    return {
        "id": f.get("id"),
        "agent": f.get("agent"),
        "domain": f.get("domain"),
        "category": f.get("category"),
        "severity": f.get("severity"),
        "confidence": f.get("confidence"),
        "phase": PHASE_FOR_DOMAIN.get(f.get("domain", ""), 5),
        "order": 0,  # filled in after sort
        "title": f.get("title", ""),
        "summary": f.get("summary", ""),
        "evidence": f.get("evidence") or [],
        "remediation_steps": f.get("remediation_steps") or [],
        "risks": f.get("risks") or [],
        "verification": f.get("verification") or [],
        "status": "pending",
        "started_at": None,
        "completed_at": None,
        "notes": "",
        "blockers": [],
        "files_touched": [],
    }


def merge_state(new_item: Dict[str, Any], old_item: Dict[str, Any]) -> Dict[str, Any]:
    """Carry forward mutable state from an existing item with the same id."""
    for key in PRESERVED_STATE_KEYS:
        if key in old_item and old_item[key] not in (None, "", []):
            new_item[key] = old_item[key]
    return new_item


def render_markdown(plan: Dict[str, Any]) -> str:
    audit = plan["audit"]
    summary = plan["summary"]
    items = plan["items"]

    lines: List[str] = []
    lines.append(f"# Action Plan — Audit {audit['id']}")
    lines.append("")
    lines.append(f"_Compiled: {audit['compiled_at']} · Target: `{audit['target']}` · Source: `{audit['source_validation_path']}`_")
    lines.append("")
    lines.append(f"**{summary['total_items']} items** · "
                 f"CRITICAL {summary['by_severity'].get('CRITICAL', 0)} · "
                 f"HIGH {summary['by_severity'].get('HIGH', 0)} · "
                 f"MEDIUM {summary['by_severity'].get('MEDIUM', 0)} · "
                 f"LOW {summary['by_severity'].get('LOW', 0)} · "
                 f"INFO {summary['by_severity'].get('INFO', 0)}")
    lines.append("")
    by_status = summary.get("by_status", {})
    if any(by_status.get(s) for s in ("done", "in_progress", "blocked", "skipped")):
        lines.append(f"_Progress: done {by_status.get('done', 0)} · "
                     f"in-progress {by_status.get('in_progress', 0)} · "
                     f"blocked {by_status.get('blocked', 0)} · "
                     f"skipped {by_status.get('skipped', 0)} · "
                     f"pending {by_status.get('pending', 0)}_")
        lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("Run `/audit-work` to start the next pending item, or `/audit-work AA-###` to jump to a specific finding.")
    lines.append("")

    # Group by phase, then severity within phase.
    by_phase: Dict[int, List[Dict[str, Any]]] = defaultdict(list)
    for item in items:
        by_phase[item.get("phase", 5)].append(item)

    for phase in sorted(by_phase):
        lines.append(f"## Phase {phase} — {PHASE_LABELS.get(phase, '')}")
        lines.append("")
        bucket = by_phase[phase]
        for item in bucket:
            box = {
                "done": "x",
                "in_progress": "~",
                "blocked": "!",
                "skipped": "-",
            }.get(item.get("status", "pending"), " ")
            domain_label = DOMAIN_LABELS.get(item.get("domain", ""), item.get("domain", ""))
            title = item.get("title", "").replace("\n", " ")
            lines.append(f"- [{box}] **{item['id']}** `[{item['severity']}]` _{domain_label}_ — {title}")
        lines.append("")

    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser(description="Compile a validation.json into an action plan.")
    p.add_argument("--validation", required=True, type=Path)
    p.add_argument("--audit-id", required=True)
    p.add_argument("--target", required=True)
    p.add_argument("--out-json", required=True, type=Path)
    p.add_argument("--out-md", required=True, type=Path)
    p.add_argument("--merge-existing", action="store_true",
                   help="Preserve status/notes/files_touched on items that already exist in --out-json.")
    args = p.parse_args()

    if not args.validation.exists():
        print(f"ERROR: validation file missing: {args.validation}", file=sys.stderr)
        return 1

    payload = json.loads(args.validation.read_text(encoding="utf-8"))
    findings = payload.get("findings") or []
    confirmed = [
        f for f in findings
        if (f.get("validator_decision") or {}).get("status", "confirmed") in ("confirmed", "merged")
    ]

    if not confirmed:
        print("WARNING: no confirmed findings in validation.json — emitting empty plan.", file=sys.stderr)

    confirmed.sort(key=rank_finding)
    items = [finding_to_item(f) for f in confirmed]
    for i, item in enumerate(items, 1):
        item["order"] = i

    if args.merge_existing and args.out_json.exists():
        try:
            existing = json.loads(args.out_json.read_text(encoding="utf-8"))
            existing_by_id = {it["id"]: it for it in existing.get("items", []) if it.get("id")}
            for item in items:
                old = existing_by_id.get(item["id"])
                if old:
                    merge_state(item, old)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"WARNING: --merge-existing failed to read prior plan ({exc}); starting fresh.", file=sys.stderr)

    sev_counts = Counter(it["severity"] for it in items)
    status_counts = Counter(it["status"] for it in items)
    now_iso = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    plan = {
        "schema_version": "1.0.0",
        "audit": {
            "id": args.audit_id,
            "compiled_at": now_iso,
            "last_updated_at": now_iso,
            "target": args.target,
            "source_validation_path": str(args.validation),
        },
        "summary": {
            "total_items": len(items),
            "by_severity": {sev: sev_counts.get(sev, 0) for sev in SEVERITY_ORDER},
            "by_status": {st: status_counts.get(st, 0) for st in
                          ("pending", "in_progress", "done", "blocked", "skipped")},
        },
        "items": items,
    }

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    tmp_json = args.out_json.with_suffix(args.out_json.suffix + ".tmp")
    tmp_json.write_text(json.dumps(plan, indent=2), encoding="utf-8")
    tmp_json.replace(args.out_json)

    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.write_text(render_markdown(plan), encoding="utf-8")

    print(f"Wrote {args.out_json} and {args.out_md} "
          f"({len(items)} items · CRITICAL {sev_counts.get('CRITICAL', 0)} "
          f"· HIGH {sev_counts.get('HIGH', 0)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
