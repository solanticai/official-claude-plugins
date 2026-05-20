#!/usr/bin/env python3
r"""validate-findings.py — Parse the nine auditor reports into a structured intermediate JSON.

The audit-validator agent runs this to extract findings from the raw markdown,
then verifies each finding against the actual filesystem and writes
`validation.md` and `validation.json`. This script does the structural parsing
only — the agent does the semantic verification.

Inputs:
  --reports-dir <path>   Directory containing one `<agent-name>.md` per agent.
                         Each agent report follows templates/agent-report-template.md.
  --out <path>           Where to write the JSON intermediate.

Output (file):
  JSON object:
    {
      "agents": [
        {
          "name": "frontend-auditor",
          "report_path": "...",
          "header": { "audit_id": "...", "target": "...", "permissive_mode": ..., "mcps_used": [...], "mcps_unreachable": [...], "memex_consulted": "..." },
          "findings": [
            { "id": "F1", "title": "...", "category": "...", "proposed_severity": "...",
              "confidence": "...", "summary": "...", "evidence": [...],
              "remediation_steps": [...], "risks": [...], "verification": [...],
              "raw_body": "..." }
          ]
        }
      ],
      "stats": { "agents": N, "total_findings": M }
    }

Heading rule (load-bearing):
  Findings are extracted by the regex:
    ^###\s+(F\d+)\b[^\n]*\n
  Anything that doesn't match this is invisible. Auditors are explicitly told
  to use `### F<N> — <title>` for every finding.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Any

# Canonical per-finding heading parser for agent reports. The shape `### F<N>`
# is documented as load-bearing in templates/agent-report-template.md and every
# auditor agent's hard rules. If another script ever needs to parse the same
# headings (today only this script does — compile-report.py consumes the JSON
# intermediate, not the markdown), factor this into a shared helper module
# rather than copy-pasting the regex.
FINDING_RE = re.compile(
    r"^###\s+(F\d+)\b[^\n]*?(?:\s+—\s+(.*?))?\n(?P<body>.*?)(?=^###\s+F\d+\b|\Z)",
    re.MULTILINE | re.DOTALL,
)

HEADER_FIELD_RE = re.compile(
    r"^\*\*(?P<key>[^*]+):\*\*\s+(?P<value>.+?)$",
    re.MULTILINE,
)


def parse_header(text: str) -> Dict[str, Any]:
    """Pull the bold-key bold-value lines out of the report header (everything
    above the first `---` separator that follows the title)."""
    # The header is between the first `# Agent Report` line and the first
    # standalone `---` line. We're forgiving — if the format drifts, pull what
    # we can.
    end_idx = text.find("\n---\n")
    if end_idx == -1:
        # No separator → take the first 2KB.
        scope = text[:2048]
    else:
        scope = text[:end_idx]
    fields: Dict[str, Any] = {}
    for m in HEADER_FIELD_RE.finditer(scope):
        key = m.group("key").strip().lower().replace(" ", "_")
        value = m.group("value").strip()
        # Convert "or 'none'" into [] for list fields.
        list_keys = {"mcps_used", "mcps_unreachable"}
        if key in list_keys:
            if value.lower().strip("\"'") in ("none", "(none)"):
                fields[key] = []
            else:
                # Strip backtick wrapping; split on comma.
                cleaned = value.strip("` ").rstrip("`")
                fields[key] = [p.strip() for p in cleaned.split(",") if p.strip()]
        elif key == "permissive_mode":
            fields[key] = value.lower().strip("`*") in ("true", "yes", "1")
        else:
            fields[key] = value.strip("`*")
    return fields


SECTION_RE = re.compile(
    r"\*\*(?P<key>[A-Z][^*]+?):\*\*",
    re.MULTILINE,
)


def parse_finding_body(body: str) -> Dict[str, Any]:
    """Extract the structured fields from a finding body."""
    fields: Dict[str, Any] = {}

    # Single-line key: value pairs like **Severity (proposed):** HIGH
    inline = {}
    for m in re.finditer(
        r"^\*\*(?P<key>[A-Z][^*]+?):\*\*\s+(?P<value>[^\n]+?)$",
        body,
        re.MULTILINE,
    ):
        key = m.group("key").lower().strip().replace(" ", "_").replace("(", "").replace(")", "")
        inline[key] = m.group("value").strip()

    fields["category"] = inline.get("category", "")
    fields["proposed_severity"] = inline.get("severity_proposed", inline.get("severity", "")).strip("`*").upper()
    fields["confidence"] = inline.get("confidence", "").lower().strip("`*")
    fields["source_notes_ref"] = inline.get("source_notes_ref", "")

    # Multi-line sections.
    def section(name: str) -> str:
        # Match a `**Name:**` heading (anchored on its own line) and capture
        # everything until the next `**X:**` heading or end of body.
        pat = re.compile(
            r"^\*\*" + re.escape(name) + r":\*\*\s*\n(?P<sect>.*?)(?=^\*\*[A-Z][^*]+:\*\*|\Z)",
            re.MULTILINE | re.DOTALL,
        )
        m = pat.search(body)
        return (m.group("sect").strip() if m else "")

    fields["summary"] = section("Investigation summary")

    # Evidence is a bullet list.
    evidence_text = section("Evidence")
    fields["evidence"] = [
        line.lstrip("-* ").strip()
        for line in evidence_text.splitlines()
        if line.strip().startswith(("-", "*"))
    ]

    # Remediation is a numbered list.
    remediation_text = section("Proposed remediation")
    if not remediation_text:
        # Older alias used by the template variants.
        remediation_text = section("Proposed steps")
    fields["remediation_steps"] = [
        re.sub(r"^\s*\d+\.\s+", "", line).strip()
        for line in remediation_text.splitlines()
        if re.match(r"^\s*\d+\.\s+", line)
    ]

    # Risks (bullets).
    risks_text = section("Risks if left unfixed")
    if not risks_text:
        risks_text = section("Risks")
    fields["risks"] = [
        line.lstrip("-* ").strip()
        for line in risks_text.splitlines()
        if line.strip().startswith(("-", "*"))
    ]

    # Verification (bullets).
    verification_text = section("Verification")
    fields["verification"] = [
        line.lstrip("-* ").strip()
        for line in verification_text.splitlines()
        if line.strip().startswith(("-", "*"))
    ]

    return fields


def parse_agent_report(path: Path) -> Dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    name = path.stem
    header = parse_header(text)
    findings: List[Dict[str, Any]] = []
    for m in FINDING_RE.finditer(text):
        fid = m.group(1)
        title = (m.group(2) or "").strip()
        body = m.group("body").strip()
        # Strip trailing horizontal rules.
        body = re.sub(r"(?:\n[\s]*-{3,}[\s]*)+\s*$", "", body).rstrip()
        parsed = parse_finding_body(body)
        parsed.update({
            "id": fid,
            "title": title,
            "raw_body": body,
        })
        findings.append(parsed)
    return {
        "name": name,
        "report_path": str(path),
        "header": header,
        "findings": findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Parse auditor reports into a JSON intermediate.")
    parser.add_argument("--reports-dir", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    if not args.reports_dir.is_dir():
        print(f"ERROR: reports directory does not exist: {args.reports_dir}", file=sys.stderr)
        return 1

    agents = []
    total_findings = 0
    for entry in sorted(args.reports_dir.iterdir()):
        if entry.suffix.lower() != ".md":
            continue
        # Skip the validator's own outputs and the combined-reports working file.
        if entry.name in ("validation.md", ".combined-reports.md"):
            continue
        agent = parse_agent_report(entry)
        agents.append(agent)
        total_findings += len(agent["findings"])

    out = {
        "agents": agents,
        "stats": {"agents": len(agents), "total_findings": total_findings},
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Parsed {len(agents)} agent reports, {total_findings} findings -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
