#!/usr/bin/env python3
"""
ast-entrypoints.py — Optional AST-level entry-point extraction.

Usage:
  python3 ast-entrypoints.py <project-root> [--format json|text]

Behaviour:
  - Walks the project for source files under known entry-point directories.
  - Uses Python's built-in `ast` module for .py files.
  - Uses lightweight regex heuristics for .ts/.tsx/.js/.jsx (tree-sitter optional).
  - Emits one JSON object per discovered entry, matching the `entry` block of
    templates/paths-schema.json.
  - Always exits 0 and prints an empty list if no entries found.
  - If AST parsing fails on a file, the file is skipped silently.

This script is COMPLEMENTARY to find-write-endpoints.sh. It produces richer
typing (captures decorator arguments, imported router names) while the shell
script provides high-recall grep. The skill should prefer this script's output
when available and fall back to the shell script otherwise.
"""

from __future__ import annotations

import argparse
import ast
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

TS_JS_EXTS = {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs"}
PY_EXTS = {".py"}


def walk_sources(root: Path) -> list[Path]:
    out: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for name in filenames:
            p = Path(dirpath) / name
            if p.suffix in TS_JS_EXTS or p.suffix in PY_EXTS:
                out.append(p)
    return out


# --- Python extraction ---------------------------------------------------------------

FASTAPI_DECORATORS = {"post", "put", "patch", "delete"}
DRF_ACTION_METHODS = {"post", "put", "patch", "delete"}


def extract_python_entries(path: Path, root: Path) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    try:
        source = path.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(source, filename=str(path))
    except (SyntaxError, UnicodeDecodeError, OSError):
        return entries

    rel = str(path.relative_to(root)).replace("\\", "/")

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for deco in node.decorator_list:
                verb, framework = _classify_decorator(deco)
                if verb is None:
                    continue
                entries.append({
                    "type": f"http-{verb.lower()}",
                    "file": rel,
                    "line": node.lineno,
                    "verb": verb,
                    "route": _first_string_arg(deco),
                    "framework": framework,
                    "handler_name": node.name,
                })
        # Django view methods (create/update/destroy)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in {"create", "update", "destroy", "perform_create", "perform_update", "perform_destroy"}:
            if "views.py" in rel or "/views/" in rel:
                entries.append({
                    "type": "http-write",
                    "file": rel,
                    "line": node.lineno,
                    "verb": "WRITE",
                    "route": None,
                    "framework": "django",
                    "handler_name": node.name,
                })

    return entries


def _classify_decorator(deco: ast.AST) -> tuple[str | None, str]:
    """Return (VERB, framework) if decorator matches a known write verb, else (None, '')."""
    target = deco
    if isinstance(deco, ast.Call):
        target = deco.func
    if isinstance(target, ast.Attribute):
        attr = target.attr.lower()
        if attr in FASTAPI_DECORATORS:
            return attr.upper(), "fastapi-or-flask"
        if attr == "route" and isinstance(deco, ast.Call):
            # Flask @app.route(methods=['POST'])
            for kw in deco.keywords:
                if kw.arg == "methods" and isinstance(kw.value, (ast.List, ast.Tuple)):
                    for el in kw.value.elts:
                        if isinstance(el, ast.Constant) and isinstance(el.value, str):
                            m = el.value.upper()
                            if m in {"POST", "PUT", "PATCH", "DELETE"}:
                                return m, "flask"
    if isinstance(target, ast.Name):
        name = target.id.lower()
        if name == "shared_task" or name == "task":
            return "TASK", "celery"
    return None, ""


def _first_string_arg(deco: ast.AST) -> str | None:
    if isinstance(deco, ast.Call) and deco.args:
        first = deco.args[0]
        if isinstance(first, ast.Constant) and isinstance(first.value, str):
            return first.value
    return None


# --- TS/JS extraction (regex-based; tree-sitter optional) -----------------------------

NEXT_APP_ROUTE = re.compile(r"^\s*export\s+(?:async\s+)?function\s+(POST|PUT|PATCH|DELETE)\b")
SERVER_ACTION = re.compile(r"""['"]use server['"]""")
EXPRESS_LIKE = re.compile(r"\b(?:app|router|fastify)\.(post|put|patch|delete)\s*\(")
NESTJS_DECORATOR = re.compile(r"@(Post|Put|Patch|Delete|MessagePattern|EventPattern)\s*\(")
TRPC_MUTATION = re.compile(r"\.mutation\s*\(")
HONO_ROUTE = re.compile(r"\bapp\.(post|put|patch|delete)\s*\(")


def extract_tsjs_entries(path: Path, root: Path) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return entries

    rel = str(path.relative_to(root)).replace("\\", "/")

    # Next.js App Router file-conventional routes
    if "/app/" in rel and rel.endswith(("route.ts", "route.tsx", "route.js", "route.jsx")):
        for i, line in enumerate(text.splitlines(), start=1):
            m = NEXT_APP_ROUTE.match(line)
            if m:
                entries.append({
                    "type": f"http-{m.group(1).lower()}",
                    "file": rel,
                    "line": i,
                    "verb": m.group(1),
                    "route": _infer_next_route(rel),
                    "framework": "next-app-router",
                    "handler_name": m.group(1),
                })

    # Server actions (file-level or function-level 'use server')
    if SERVER_ACTION.search(text):
        for i, line in enumerate(text.splitlines(), start=1):
            if "use server" in line:
                entries.append({
                    "type": "next-server-action",
                    "file": rel,
                    "line": i,
                    "verb": "ACTION",
                    "route": None,
                    "framework": "next-app-router",
                    "handler_name": None,
                })
                break

    # Express/Fastify/Hono
    for i, line in enumerate(text.splitlines(), start=1):
        m = EXPRESS_LIKE.search(line)
        if m:
            entries.append({
                "type": f"http-{m.group(1).lower()}",
                "file": rel,
                "line": i,
                "verb": m.group(1).upper(),
                "route": None,
                "framework": "express-like",
                "handler_name": None,
            })

    # NestJS decorators
    for i, line in enumerate(text.splitlines(), start=1):
        m = NESTJS_DECORATOR.search(line)
        if m:
            entries.append({
                "type": f"http-{m.group(1).lower()}",
                "file": rel,
                "line": i,
                "verb": m.group(1).upper(),
                "route": None,
                "framework": "nestjs",
                "handler_name": None,
            })

    # tRPC mutations
    for i, line in enumerate(text.splitlines(), start=1):
        if TRPC_MUTATION.search(line):
            entries.append({
                "type": "trpc-mutation",
                "file": rel,
                "line": i,
                "verb": "MUTATION",
                "route": None,
                "framework": "trpc",
                "handler_name": None,
            })

    return entries


def _infer_next_route(rel: str) -> str:
    # app/api/tasks/route.ts -> /api/tasks
    parts = rel.split("/")
    if "app" in parts:
        idx = parts.index("app")
        route_parts = parts[idx + 1:-1]  # drop "app" and "route.ts"
        return "/" + "/".join(route_parts) if route_parts else "/"
    return rel


# --- Main ----------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="Extract write-path entry points via AST.")
    parser.add_argument("root", help="Project root directory")
    parser.add_argument("--format", choices=["json", "text"], default="json")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"ERROR: not a directory: {root}", file=sys.stderr)
        return 1

    all_entries: list[dict[str, Any]] = []
    for path in walk_sources(root):
        try:
            if path.suffix in PY_EXTS:
                all_entries.extend(extract_python_entries(path, root))
            elif path.suffix in TS_JS_EXTS:
                all_entries.extend(extract_tsjs_entries(path, root))
        except Exception:
            # Never crash on one file — log nothing, skip
            continue

    if args.format == "json":
        print(json.dumps({"entries": all_entries, "count": len(all_entries)}, indent=2))
    else:
        print(f"Found {len(all_entries)} entries")
        for e in all_entries:
            print(f"  {e['file']}:{e['line']}  {e.get('verb', '?')}  {e.get('framework', '?')}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
