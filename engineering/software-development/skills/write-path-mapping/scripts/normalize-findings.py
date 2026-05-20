#!/usr/bin/env python3
"""
normalize-findings.py — Merge partial write-path results into a unified paths JSON.

Usage:
  python3 normalize-findings.py <partial1.json> [partial2.json ...] --out paths.json

Inputs can be:
  - Entry-point lists from sub-agents or ast-entrypoints.py:
      { "entries": [ { entry block }, ... ] }
  - Persistence-call lists from ast-write-calls.py:
      { "calls": [ { file, line, kind, target, snippet }, ... ] }
  - Transaction-boundary reports from transaction-boundary-check.py:
      { "writes": [ { file, line, in_transaction, snippet }, ... ] }
  - Already-normalized paths (merged from prior runs):
      { "paths": [ { full path object }, ... ] }

Output is a single JSON file conforming to templates/paths-schema.json,
with stable IDs assigned (WP-001, WP-002, ...).

This script does NOT invent data. It only merges what the inputs explicitly
provide. Fields like middleware, auth, risks must be filled in by later phases
of the skill (possibly via Agent sub-agents).

Always exits 0 on success; exits 1 only on invalid arguments.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def load_json(p: Path) -> dict[str, Any]:
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print(f"WARNING: could not parse {p}: {e}", file=sys.stderr)
        return {}


def normalize_entry(e: dict[str, Any]) -> dict[str, Any]:
    """Ensure an entry block has all required fields (fill with None/defaults)."""
    return {
        "type": e.get("type") or "http-unknown",
        "file": e.get("file") or "unknown",
        "line": int(e.get("line") or 0),
        "verb": e.get("verb") or "",
        "route": e.get("route"),
        "framework": e.get("framework") or "unknown",
        "handler_name": e.get("handler_name"),
    }


def make_path_skeleton(entry: dict[str, Any], idx: int) -> dict[str, Any]:
    return {
        "id": f"WP-{idx:03d}",
        "entry": normalize_entry(entry),
        "middleware": [],
        "validator": None,
        "auth": {"layer": None, "evidence": None, "rls_policies": []},
        "handler": {
            "file": entry.get("file") or "unknown",
            "line": int(entry.get("line") or 0),
            "delegates_to": [],
        },
        "persistence_targets": [],
        "fan_out_count": 0,
        "downstream_effects": [],
        "risks": [],
        "depth": 1,
        "completeness_score": 0,
    }


def merge_calls_into_paths(paths: list[dict[str, Any]], calls: list[dict[str, Any]]) -> None:
    """Attach calls to the nearest path whose handler file matches.

    Simple heuristic: for each call, attach to every path whose entry.file matches
    the call's file. This is correct for handlers that inline their writes;
    cross-file traces require a dedicated Explore sub-agent.
    """
    by_file: dict[str, list[dict[str, Any]]] = {}
    for p in paths:
        by_file.setdefault(p["entry"]["file"], []).append(p)

    for c in calls:
        file = c.get("file") or ""
        for p in by_file.get(file, []):
            p["persistence_targets"].append({
                "kind": c.get("kind") or "unknown",
                "target": c.get("target"),
                "file": file,
                "line": int(c.get("line") or 0),
                "in_transaction": bool(c.get("in_transaction", False)),
                "snippet": c.get("snippet"),
            })

    # Update fan-out count
    for p in paths:
        p["fan_out_count"] = len(p["persistence_targets"])


def merge_tx_info(paths: list[dict[str, Any]], tx_writes: list[dict[str, Any]]) -> None:
    """Update in_transaction flags on existing targets from tx check output."""
    lookup: dict[tuple[str, int], bool] = {}
    for w in tx_writes:
        lookup[(w.get("file") or "", int(w.get("line") or 0))] = bool(w.get("in_transaction"))

    for p in paths:
        for t in p["persistence_targets"]:
            key = (t.get("file") or "", int(t.get("line") or 0))
            if key in lookup:
                t["in_transaction"] = lookup[key]


def main() -> int:
    parser = argparse.ArgumentParser(description="Merge partial write-path results.")
    parser.add_argument("inputs", nargs="+", help="Partial JSON files to merge")
    parser.add_argument("--out", required=True, help="Output paths JSON file")
    args = parser.parse_args()

    entries: list[dict[str, Any]] = []
    calls: list[dict[str, Any]] = []
    tx_writes: list[dict[str, Any]] = []
    preexisting_paths: list[dict[str, Any]] = []

    for raw in args.inputs:
        p = Path(raw)
        if not p.is_file():
            print(f"WARNING: skipping missing file {raw}", file=sys.stderr)
            continue
        data = load_json(p)
        if not data:
            continue
        if "entries" in data:
            entries.extend(data["entries"])
        if "calls" in data:
            calls.extend(data["calls"])
        if "writes" in data:
            tx_writes.extend(data["writes"])
        if "paths" in data:
            preexisting_paths.extend(data["paths"])

    # Deduplicate entries by (file, line, verb)
    seen_keys: set[tuple[str, int, str]] = set()
    unique_entries: list[dict[str, Any]] = []
    for e in entries:
        key = (e.get("file") or "", int(e.get("line") or 0), e.get("verb") or "")
        if key in seen_keys:
            continue
        seen_keys.add(key)
        unique_entries.append(e)

    # Build path skeletons from entries
    paths: list[dict[str, Any]] = list(preexisting_paths)
    next_idx = len(paths) + 1
    for e in unique_entries:
        paths.append(make_path_skeleton(e, next_idx))
        next_idx += 1

    # Merge calls & transaction info
    merge_calls_into_paths(paths, calls)
    merge_tx_info(paths, tx_writes)

    output = {
        "schema_version": "1.0.0",
        "paths": paths,
        "totals": {
            "paths": len(paths),
            "entries_discovered": len(unique_entries),
            "persistence_targets": sum(len(p["persistence_targets"]) for p in paths),
        },
    }

    out_path = Path(args.out)
    out_path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}  ({len(paths)} paths, {output['totals']['persistence_targets']} targets)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
