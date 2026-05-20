#!/usr/bin/env python3
"""
mermaid-render.py — Render write-path Mermaid diagrams from a paths JSON file.

Usage:
  python3 mermaid-render.py <paths-json-file> [--out diagrams.md]

Reads a JSON file conforming to templates/paths-schema.json and emits a
markdown block containing four Mermaid diagrams:

  1. System flowchart (flowchart TD) — every entry grouped by domain
  2. Per-endpoint sequence diagrams (sequenceDiagram) — top 20 endpoints
  3. Data-domain write map (flowchart LR) — bipartite entries -> targets
  4. DB trigger/function graph (flowchart LR) — Postgres side effects

Node shapes:
  ( ) standard, [( )] SQL table, [[ ]] cache, (( )) external API,
  > ] file/object store, {{ }} queue/topic, { } decision / auth gate

Color classes by highest risk severity:
  critical (red), high (orange), medium (yellow), ok (green), info (blue)

Always exits 0 even on empty input.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


SEVERITY_ORDER = ["CRITICAL", "HIGH", "MEDIUM", "INFO", "OK"]
CLASS_MAP = {
    "CRITICAL": "critical",
    "HIGH": "high",
    "MEDIUM": "medium",
    "INFO": "info",
    "OK": "ok",
}


def sanitize_id(s: str) -> str:
    """Turn an arbitrary string into a valid Mermaid node id."""
    s = re.sub(r"[^A-Za-z0-9_]", "_", s)
    if not s:
        s = "node"
    if s[0].isdigit():
        s = "n_" + s
    return s[:60]


def sanitize_label(s: str) -> str:
    """Escape characters that break Mermaid labels."""
    if s is None:
        return ""
    return s.replace('"', "'").replace("|", "/").replace("\n", " ")[:80]


def highest_severity(risks: list[dict[str, Any]]) -> str:
    if not risks:
        return "OK"
    severities = {r.get("severity", "INFO").upper() for r in risks}
    for s in SEVERITY_ORDER:
        if s in severities:
            return s
    return "OK"


def target_shape(kind: str, target: str) -> tuple[str, str]:
    """Return (open, close) shape tokens for a persistence target kind."""
    kind = (kind or "").lower()
    if "sql" in kind or "supabase-from" in kind or "orm" in kind or "drizzle" in kind or "prisma" in kind or "typeorm" in kind or "mongoose" in kind or "kysely" in kind or "active-record" in kind or "eloquent" in kind or "doctrine" in kind or "gorm" in kind or "django-orm" in kind or "sqlalchemy" in kind:
        return "[(", ")]"
    if "cache" in kind or "redis" in kind:
        return "[[", "]]"
    if "external-api" in kind or "http-out" in kind:
        return "((", "))"
    if "file" in kind or "s3" in kind or "storage" in kind or "fs-write" in kind:
        return "[\\", "/]"
    if "queue" in kind or "publish" in kind or "topic" in kind:
        return "{{", "}}"
    if "event" in kind:
        return "((", "))"
    return "[", "]"


def render_system_flowchart(paths: list[dict[str, Any]]) -> str:
    lines = ["```mermaid", "flowchart TD"]
    # Class defs
    lines.extend([
        "    classDef critical fill:#ff6b6b,stroke:#c00,color:#fff;",
        "    classDef high fill:#ffa94d,stroke:#d97706,color:#fff;",
        "    classDef medium fill:#ffe066,stroke:#d4a017,color:#333;",
        "    classDef info fill:#a5d8ff,stroke:#1971c2,color:#0b3d66;",
        "    classDef ok fill:#b2f2bb,stroke:#2f9e44,color:#0b3d1e;",
    ])

    # Group by domain (top-level folder of entry.file)
    domains: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for p in paths:
        entry = p.get("entry") or {}
        file = entry.get("file", "unknown") or "unknown"
        parts = file.split("/")
        domain = parts[0] if len(parts) > 1 else "root"
        domains[domain].append(p)

    entry_ids: dict[str, str] = {}
    target_ids: dict[str, str] = {}

    for domain, items in sorted(domains.items()):
        sub_id = sanitize_id(f"dom_{domain}")
        lines.append(f"    subgraph {sub_id}[\"{sanitize_label(domain)}\"]")
        for p in items:
            pid = p.get("id", "")
            entry = p.get("entry") or {}
            label = entry.get("route") or entry.get("handler_name") or f"{entry.get('file','?')}:{entry.get('line','?')}"
            verb = entry.get("verb", "")
            full = f"{verb} {label}".strip()
            node_id = sanitize_id(f"e_{pid}_{entry.get('file','')}_{entry.get('line','')}")
            entry_ids[pid] = node_id
            lines.append(f"        {node_id}[\"{sanitize_label(full)}\"]")
        lines.append("    end")

    # Now edges: entry -> auth gate -> target(s)
    for p in paths:
        pid = p.get("id", "")
        node_id = entry_ids.get(pid)
        if not node_id:
            continue
        auth = p.get("auth") or {}
        has_auth = bool(auth.get("layer"))
        if has_auth:
            gate = sanitize_id(f"g_{pid}")
            lines.append(f"    {gate}{{\"auth\"}}")
            lines.append(f"    {node_id} --> {gate}")
            src = gate
        else:
            src = node_id

        targets = p.get("persistence_targets") or []
        for t in targets:
            tname = t.get("target") or t.get("kind") or "unknown"
            tkey = f"{t.get('kind','')}_{tname}"
            if tkey not in target_ids:
                tid = sanitize_id(f"t_{tkey}")
                target_ids[tkey] = tid
                open_s, close_s = target_shape(t.get("kind", ""), tname)
                lines.append(f"    {tid}{open_s}\"{sanitize_label(tname)}\"{close_s}")
            lines.append(f"    {src} --> {target_ids[tkey]}")

        # Apply class to entry based on highest risk
        sev = highest_severity(p.get("risks") or [])
        lines.append(f"    class {node_id} {CLASS_MAP[sev]};")

    lines.append("```")
    return "\n".join(lines)


def render_sequence_diagrams(paths: list[dict[str, Any]], limit: int = 20) -> str:
    # Sort: highest severity first, then by fan_out_count descending
    def sort_key(p):
        sev = highest_severity(p.get("risks") or [])
        sev_rank = SEVERITY_ORDER.index(sev) if sev in SEVERITY_ORDER else len(SEVERITY_ORDER)
        return (sev_rank, -(p.get("fan_out_count") or 0))

    top = sorted(paths, key=sort_key)[:limit]
    if not top:
        return "_No write paths available for sequence diagrams._"

    sections: list[str] = []
    for p in top:
        entry = p.get("entry") or {}
        route = entry.get("route") or entry.get("handler_name") or "?"
        verb = entry.get("verb", "")
        title = f"{verb} {route}".strip()

        lines = ["```mermaid", "sequenceDiagram", f"    title {sanitize_label(title)}"]
        lines.append("    actor U as User")
        lines.append("    participant R as Route")

        middleware = p.get("middleware") or []
        for mw in middleware:
            name = mw.get("name") or mw.get("role") or "mw"
            lines.append(f"    U->>R: {sanitize_label(verb)} {sanitize_label(route)}")
            lines.append(f"    R->>R: {sanitize_label(name)} ({sanitize_label(mw.get('role',''))})")
            break  # just show first mw as the initial hop

        if not middleware:
            lines.append(f"    U->>R: {sanitize_label(verb)} {sanitize_label(route)}")

        validator = p.get("validator")
        if validator:
            lib = validator.get("lib", "validator")
            schema = validator.get("schema", "")
            lines.append(f"    R->>R: {sanitize_label(lib)}.parse({sanitize_label(schema)})")

        auth = p.get("auth") or {}
        if auth.get("layer"):
            lines.append(f"    R->>R: authorize ({sanitize_label(auth.get('layer',''))})")

        handler = p.get("handler") or {}
        for delegate in (handler.get("delegates_to") or [])[:3]:
            lines.append(f"    R->>+S: {sanitize_label(delegate)}")

        targets = p.get("persistence_targets") or []
        for t in targets:
            tname = t.get("target") or t.get("kind") or "?"
            lines.append(f"    R->>DB: {sanitize_label(t.get('kind',''))} {sanitize_label(tname)}")

        for eff in (p.get("downstream_effects") or []):
            kind = eff.get("kind", "effect")
            name = eff.get("name") or eff.get("channel") or eff.get("target") or ""
            lines.append(f"    DB-->>E: {sanitize_label(kind)} {sanitize_label(name)}")

        lines.append("    R-->>U: response")
        lines.append("```")
        sections.append(f"### {title}\n\n" + "\n".join(lines))

    return "\n\n".join(sections)


def render_data_domain_map(paths: list[dict[str, Any]]) -> str:
    lines = ["```mermaid", "flowchart LR"]

    # Build bipartite: entries on left, unique targets on right
    entry_ids: dict[str, str] = {}
    target_ids: dict[str, str] = {}
    edges: list[tuple[str, str]] = []

    lines.append("    subgraph Entries[\"Write Entries\"]")
    for p in paths:
        pid = p.get("id", "")
        entry = p.get("entry") or {}
        label = entry.get("route") or entry.get("handler_name") or f"{entry.get('file','?')}"
        verb = entry.get("verb", "")
        full = f"{verb} {label}".strip()
        nid = sanitize_id(f"en_{pid}")
        entry_ids[pid] = nid
        lines.append(f"        {nid}[\"{sanitize_label(full)}\"]")
    lines.append("    end")

    lines.append("    subgraph Targets[\"Persistence Targets\"]")
    for p in paths:
        for t in p.get("persistence_targets") or []:
            tname = t.get("target") or t.get("kind") or "?"
            tkey = f"{t.get('kind','')}_{tname}"
            if tkey not in target_ids:
                tid = sanitize_id(f"tg_{tkey}")
                target_ids[tkey] = tid
                open_s, close_s = target_shape(t.get("kind", ""), tname)
                lines.append(f"        {tid}{open_s}\"{sanitize_label(tname)}\"{close_s}")
            edges.append((entry_ids[p.get("id", "")], target_ids[tkey]))
    lines.append("    end")

    seen: set[tuple[str, str]] = set()
    for a, b in edges:
        if (a, b) in seen:
            continue
        seen.add((a, b))
        lines.append(f"    {a} --> {b}")

    lines.append("```")
    return "\n".join(lines)


def render_trigger_graph(paths: list[dict[str, Any]]) -> str:
    lines = ["```mermaid", "flowchart LR"]

    # Collect downstream effects of kind db-trigger or trigger-side-effect
    seen: set[str] = set()
    edges: list[tuple[str, str, str]] = []  # (source_table, trigger_fn, target_table)

    for p in paths:
        for t in p.get("persistence_targets") or []:
            src_tbl = t.get("target") or t.get("kind") or ""
            for eff in p.get("downstream_effects") or []:
                kind = (eff.get("kind") or "").lower()
                if "trigger" not in kind and "function" not in kind:
                    continue
                fn_name = eff.get("name") or "trigger_fn"
                target = eff.get("target") or "?"
                edges.append((src_tbl, fn_name, target))

    if not edges:
        lines.append("    empty[No DB triggers or functions detected]")
        lines.append("```")
        return "\n".join(lines)

    for src, fn, tgt in edges:
        src_id = sanitize_id(f"tr_src_{src}")
        fn_id = sanitize_id(f"tr_fn_{fn}")
        tgt_id = sanitize_id(f"tr_tgt_{tgt}")
        if src_id not in seen:
            lines.append(f"    {src_id}[(\"{sanitize_label(src)}\")]")
            seen.add(src_id)
        if fn_id not in seen:
            lines.append(f"    {fn_id}{{{{\"fn: {sanitize_label(fn)}\"}}}}")
            seen.add(fn_id)
        if tgt_id not in seen:
            lines.append(f"    {tgt_id}[(\"{sanitize_label(tgt)}\")]")
            seen.add(tgt_id)
        lines.append(f"    {src_id} --> {fn_id} --> {tgt_id}")

    lines.append("```")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Render write-path Mermaid diagrams.")
    parser.add_argument("paths_json", help="Path to paths JSON file")
    parser.add_argument("--out", default=None, help="Output markdown file (stdout if omitted)")
    args = parser.parse_args()

    src = Path(args.paths_json)
    if not src.is_file():
        print(f"ERROR: not a file: {src}", file=sys.stderr)
        return 1

    try:
        data = json.loads(src.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"ERROR: invalid JSON: {e}", file=sys.stderr)
        return 1

    paths = data.get("paths") or []

    out: list[str] = []
    out.append("## Visual Artifacts\n")
    out.append("### A. System Write Flowchart\n")
    out.append(render_system_flowchart(paths))
    out.append("\n### B. Per-Endpoint Sequence Diagrams (top 20)\n")
    out.append(render_sequence_diagrams(paths))
    out.append("\n### C. Data-Domain Write Map\n")
    out.append(render_data_domain_map(paths))
    out.append("\n### D. DB Trigger / Function Graph\n")
    out.append(render_trigger_graph(paths))

    result = "\n".join(out) + "\n"

    if args.out:
        Path(args.out).write_text(result, encoding="utf-8")
        print(f"Wrote {args.out}")
    else:
        print(result)

    return 0


if __name__ == "__main__":
    sys.exit(main())
