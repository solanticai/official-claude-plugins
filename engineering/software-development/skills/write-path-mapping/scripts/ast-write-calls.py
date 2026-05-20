#!/usr/bin/env python3
"""
ast-write-calls.py — Enumerate persistence-layer calls reached from a handler file.

Usage:
  python3 ast-write-calls.py <file-or-dir> [--format json|text]

For a single file, returns all write-call sites matching the persistence matrix
defined in reference.md §4. For a directory, walks it and aggregates results.

Output shape (JSON):
  {
    "calls": [
      {
        "file": "src/services/tasks.ts",
        "line": 58,
        "kind": "supabase-from-insert",
        "target": "operations.tasks",
        "snippet": "await supabase.from('operations.tasks').insert({ ... })"
      },
      ...
    ]
  }

This script is INTENTIONALLY simple and regex-based. For rigorous cross-file
import resolution, the skill should spawn an Explore sub-agent instead.
Always exits 0.
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

SOURCE_EXTS = {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".py", ".rb", ".php", ".go", ".rs"}

# --- Pattern catalogue ---------------------------------------------------------------
# Each pattern:  (regex, kind, target_capture_group_or_None)

PATTERNS: list[tuple[re.Pattern[str], str]] = [
    # Supabase JS
    (re.compile(r"""\.from\(\s*['"]([^'"]+)['"]\s*\)\s*\.insert\b"""), "supabase-from-insert"),
    (re.compile(r"""\.from\(\s*['"]([^'"]+)['"]\s*\)\s*\.upsert\b"""), "supabase-from-upsert"),
    (re.compile(r"""\.from\(\s*['"]([^'"]+)['"]\s*\)\s*\.update\b"""), "supabase-from-update"),
    (re.compile(r"""\.from\(\s*['"]([^'"]+)['"]\s*\)\s*\.delete\b"""), "supabase-from-delete"),
    (re.compile(r"""\.rpc\(\s*['"]([^'"]+)['"]"""), "supabase-rpc"),
    (re.compile(r"""\.storage\.from\(\s*['"]([^'"]+)['"]\s*\)\s*\.(upload|remove|copy|move)\b"""), "supabase-storage-write"),

    # Prisma
    (re.compile(r"""prisma\.(\w+)\.(create|createMany|update|updateMany|upsert|delete|deleteMany)\b"""), "prisma-write"),
    (re.compile(r"""prisma\.\$transaction\b"""), "prisma-transaction"),

    # Drizzle
    (re.compile(r"""\bdb\.(insert|update|delete)\s*\(\s*(\w+)"""), "drizzle-write"),

    # Kysely
    (re.compile(r"""\b(insertInto|updateTable|deleteFrom)\s*\(\s*['"]?(\w+)"""), "kysely-write"),

    # TypeORM
    (re.compile(r"""\.(save|insert|update|delete|softRemove|softDelete)\s*\("""), "typeorm-write"),

    # Mongoose
    (re.compile(r"""\.(save|create|updateOne|updateMany|deleteOne|deleteMany|findOneAndUpdate|findOneAndDelete)\s*\("""), "mongoose-write"),

    # Raw SQL (node-postgres / postgres-js)
    (re.compile(r"""(\.query|\.execute|sql)\s*[\(`]\s*[`'"]?\s*(INSERT|UPDATE|DELETE|UPSERT)\b""", re.I), "raw-sql"),

    # Redis writes
    (re.compile(r"""\.(set|hset|hmset|del|expire|incr|decr|xadd|lpush|rpush|sadd|zadd)\s*\("""), "redis-write"),

    # File writes
    (re.compile(r"""fs\.(writeFile|writeFileSync|appendFile|appendFileSync|rename|unlink)\s*\("""), "fs-write"),
    (re.compile(r"""(PutObjectCommand|putObject|upload)\b.*(S3|s3Client)"""), "s3-write"),

    # External API writes
    (re.compile(r"""fetch\s*\([^)]*\{\s*method\s*:\s*['"](POST|PUT|PATCH|DELETE)['"]""", re.I), "external-api-write"),
    (re.compile(r"""axios\.(post|put|patch|delete)\s*\("""), "external-api-write"),

    # Event emit
    (re.compile(r"""\.(emit|publish|dispatch)\s*\(\s*['"]([^'"]+)['"]"""), "event-emit"),

    # Queue publish
    (re.compile(r"""\.add\s*\(\s*['"]([^'"]+)['"]"""), "queue-publish"),
    (re.compile(r"""SendMessageCommand|sqs\.sendMessage"""), "queue-publish"),

    # Python ORMs
    (re.compile(r"""\.objects\.(create|update|delete|get_or_create|update_or_create|bulk_create)\b"""), "django-orm-write"),
    (re.compile(r"""session\.(add|merge|delete|commit)\b"""), "sqlalchemy-write"),

    # Ruby ActiveRecord / Eloquent / Doctrine
    (re.compile(r"""\.(save|update|destroy|create|update_attributes|upsert)\s*[!(\s]"""), "active-record-write"),
    (re.compile(r"""->(save|update|delete|create|insert)\s*\("""), "eloquent-write"),
    (re.compile(r"""EntityManager.*->(persist|remove|flush)\s*\("""), "doctrine-write"),

    # Go ORMs
    (re.compile(r"""\b(db|tx)\.(Create|Save|Updates|Delete|Upsert)\s*\("""), "gorm-write"),
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
    calls: list[dict[str, Any]] = []
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return calls

    try:
        rel = str(path.relative_to(repo_root)).replace("\\", "/")
    except ValueError:
        rel = str(path).replace("\\", "/")

    lines = text.splitlines()
    for i, line in enumerate(lines, start=1):
        for pat, kind in PATTERNS:
            m = pat.search(line)
            if not m:
                continue
            target = None
            if m.groups():
                # Try to extract the most meaningful capture
                groups = [g for g in m.groups() if g]
                if groups:
                    target = groups[0]
            calls.append({
                "file": rel,
                "line": i,
                "kind": kind,
                "target": target,
                "snippet": line.strip()[:200],
            })
            break  # one match per line is enough
    return calls


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan for persistence-layer write calls.")
    parser.add_argument("path", help="File or directory to scan")
    parser.add_argument("--root", help="Project root (for relative paths)", default=None)
    parser.add_argument("--format", choices=["json", "text"], default="json")
    args = parser.parse_args()

    target = Path(args.path).resolve()
    if not target.exists():
        print(f"ERROR: not found: {target}", file=sys.stderr)
        return 1
    repo_root = Path(args.root).resolve() if args.root else (target if target.is_dir() else target.parent)

    all_calls: list[dict[str, Any]] = []
    for src in walk_sources(target):
        try:
            all_calls.extend(scan_file(src, repo_root))
        except Exception:
            continue

    if args.format == "json":
        print(json.dumps({"calls": all_calls, "count": len(all_calls)}, indent=2))
    else:
        print(f"Found {len(all_calls)} write calls")
        for c in all_calls:
            tgt = f" -> {c['target']}" if c.get("target") else ""
            print(f"  {c['file']}:{c['line']}  [{c['kind']}]{tgt}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
