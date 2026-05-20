#!/usr/bin/env python3
"""
transaction-boundary-check.py — Detect transaction wrappers around write calls.

Usage:
  python3 transaction-boundary-check.py <file-or-dir> [--format json|text]

Scans source files for transaction boundaries and reports whether write calls
are wrapped in one. The detection is heuristic and line-range based:
a write call is considered "in_transaction" if it appears inside a block
that begins with a known transaction opener and has not yet closed.

Supported openers (ORM/stack):
  - Prisma:      prisma.$transaction(
  - Supabase:    rpc('begin'...) NOT supported — Supabase txns must use PL/pgSQL RPC fns
  - Knex:        knex.transaction(
  - Drizzle:     db.transaction(
  - TypeORM:     transaction(/runInTransaction(
  - Kysely:      .transaction().execute(
  - SQLAlchemy:  session.begin(/with session:/engine.begin(
  - Django ORM:  transaction.atomic(
  - ActiveRecord:ActiveRecord::Base.transaction
  - Laravel:     DB::transaction(
  - gorm:        db.Transaction(
  - sqlx(Go):    tx, err := db.Begin
  - Raw SQL:     BEGIN; ... COMMIT;

Always exits 0. Never aborts on parse errors.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

EXCLUDE_DIRS = {
    "node_modules", ".next", ".turbo", "dist", "build", "target",
    ".venv", "venv", "coverage", ".git", "__pycache__",
}

SOURCE_EXTS = {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".py", ".rb", ".php", ".go"}

TX_OPENERS = [
    re.compile(r"prisma\.\$transaction\s*\("),
    re.compile(r"knex\.transaction\s*\("),
    re.compile(r"\bdb\.transaction\s*\("),
    re.compile(r"\.transaction\(\)\.execute\s*\("),
    re.compile(r"transaction\.atomic\s*\("),
    re.compile(r"with\s+transaction\.atomic\b"),
    re.compile(r"session\.begin\s*\("),
    re.compile(r"engine\.begin\s*\("),
    re.compile(r"with\s+session\.begin\b"),
    re.compile(r"ActiveRecord::Base\.transaction\b"),
    re.compile(r"\.transaction\s+do\b"),  # Rails .transaction do
    re.compile(r"DB::transaction\s*\("),
    re.compile(r"\brunInTransaction\s*\("),
    re.compile(r"\btransaction\s*\(\s*function"),
    re.compile(r"db\.Transaction\s*\("),  # gorm
    re.compile(r"\btx,\s*err\s*:=\s*\w+\.Begin\b"),  # sqlx
    re.compile(r"^\s*BEGIN\s*;", re.I),
]

TX_CLOSERS = [
    re.compile(r"^\s*COMMIT\s*;", re.I),
    re.compile(r"^\s*ROLLBACK\s*;", re.I),
]

WRITE_HINTS = [
    re.compile(r"\.insert\s*\("),
    re.compile(r"\.upsert\s*\("),
    re.compile(r"\.update\s*\("),
    re.compile(r"\.delete\s*\("),
    re.compile(r"\.create\s*\("),
    re.compile(r"\.save\s*\("),
    re.compile(r"\.destroy\s*\("),
    re.compile(r"\bINSERT\b|\bUPDATE\b|\bDELETE\b|\bUPSERT\b", re.I),
]


def walk_sources(root: Path) -> list[Path]:
    out: list[Path] = []
    if root.is_file():
        return [root] if root.suffix in SOURCE_EXTS else []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for name in filenames:
            p = Path(dirpath) / name
            if p.suffix in SOURCE_EXTS:
                out.append(p)
    return out


def scan_file(path: Path, repo_root: Path) -> list[dict[str, Any]]:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return []

    try:
        rel = str(path.relative_to(repo_root)).replace("\\", "/")
    except ValueError:
        rel = str(path).replace("\\", "/")

    lines = text.splitlines()
    tx_depth = 0
    paren_balance = 0
    results: list[dict[str, Any]] = []

    for i, raw in enumerate(lines, start=1):
        line = raw

        # Track tx openers and balance parentheses (rough but effective for JS/TS/Py)
        if tx_depth > 0:
            paren_balance += line.count("(") - line.count(")")
            if paren_balance <= 0:
                tx_depth = max(0, tx_depth - 1)
                paren_balance = 0

        for opener in TX_OPENERS:
            if opener.search(line):
                tx_depth += 1
                paren_balance += line.count("(") - line.count(")")
                break

        for closer in TX_CLOSERS:
            if closer.search(line):
                tx_depth = max(0, tx_depth - 1)

        # Any write hint on this line?
        for wh in WRITE_HINTS:
            if wh.search(line):
                results.append({
                    "file": rel,
                    "line": i,
                    "in_transaction": tx_depth > 0,
                    "snippet": line.strip()[:200],
                })
                break

    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Detect transaction boundaries around writes.")
    parser.add_argument("path")
    parser.add_argument("--root", default=None)
    parser.add_argument("--format", choices=["json", "text"], default="json")
    args = parser.parse_args()

    target = Path(args.path).resolve()
    if not target.exists():
        print(f"ERROR: not found: {target}", file=sys.stderr)
        return 1
    repo_root = Path(args.root).resolve() if args.root else (target if target.is_dir() else target.parent)

    all_results: list[dict[str, Any]] = []
    for src in walk_sources(target):
        try:
            all_results.extend(scan_file(src, repo_root))
        except Exception:
            continue

    if args.format == "json":
        in_tx = sum(1 for r in all_results if r["in_transaction"])
        print(json.dumps({
            "writes": all_results,
            "total": len(all_results),
            "in_transaction": in_tx,
            "outside_transaction": len(all_results) - in_tx,
        }, indent=2))
    else:
        for r in all_results:
            mark = "TX" if r["in_transaction"] else "--"
            print(f"  [{mark}] {r['file']}:{r['line']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
