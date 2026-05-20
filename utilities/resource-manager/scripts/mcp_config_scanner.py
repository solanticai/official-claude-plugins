"""Scan every Claude / Claude Code config that can register an MCP server.

Looks at user-level and project-level configs and reports each registered
server with its scope so the ``/mcp-server-audit`` skill can recommend
which to disable.
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any


@dataclass
class McpEntry:
    name: str
    command: str
    args: list[str]
    scope: str          # user | project | plugin
    disabled: bool
    config_path: str
    project_root: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _load_json(path: Path) -> dict[str, Any] | None:
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


def _extract_servers(data: dict[str, Any]) -> dict[str, Any]:
    """``.mcp.json`` uses the top-level shape; settings.json nests under ``mcpServers``."""
    if not isinstance(data, dict):
        return {}
    if "mcpServers" in data and isinstance(data["mcpServers"], dict):
        return data["mcpServers"]
    if "servers" in data and isinstance(data["servers"], dict):
        return data["servers"]
    return {}


def _emit(data: dict[str, Any], scope: str, path: Path, project_root: str = "") -> list[McpEntry]:
    out: list[McpEntry] = []
    servers = _extract_servers(data)
    for name, spec in servers.items():
        if not isinstance(spec, dict):
            continue
        out.append(
            McpEntry(
                name=name,
                command=str(spec.get("command") or ""),
                args=[str(a) for a in spec.get("args") or []],
                scope=scope,
                disabled=bool(spec.get("disabled", False)),
                config_path=str(path),
                project_root=project_root,
            )
        )
    return out


def _scan_user_configs(home: Path) -> list[McpEntry]:
    out: list[McpEntry] = []
    for candidate in [home / ".claude.json", home / ".claude" / "settings.json", home / ".claude" / "settings.local.json"]:
        if not candidate.exists():
            continue
        data = _load_json(candidate)
        if data:
            out.extend(_emit(data, "user", candidate))
    return out


def _scan_project(root: Path) -> list[McpEntry]:
    out: list[McpEntry] = []
    for rel in [".mcp.json", ".claude/settings.json", ".claude/settings.local.json"]:
        p = root / rel
        if not p.exists():
            continue
        data = _load_json(p)
        if data:
            out.extend(_emit(data, "project", p, project_root=str(root)))
    return out


def _walk_up_for_projects(cwd: Path) -> list[Path]:
    roots: list[Path] = []
    seen: set[Path] = set()
    cur = cwd.resolve()
    while True:
        if cur in seen:
            break
        seen.add(cur)
        # Treat any directory that has .claude/ or .mcp.json as a project root.
        if (cur / ".claude").is_dir() or (cur / ".mcp.json").is_file():
            roots.append(cur)
        parent = cur.parent
        if parent == cur:
            break
        cur = parent
    return roots


def _scan_plugin_caches(home: Path) -> list[McpEntry]:
    out: list[McpEntry] = []
    plugins_cache = home / ".claude" / "plugins" / "cache"
    if not plugins_cache.is_dir():
        return out
    for mcp_json in plugins_cache.rglob(".mcp.json"):
        data = _load_json(mcp_json)
        if data:
            out.extend(_emit(data, "plugin", mcp_json))
    return out


def scan(cwd: Path | None = None) -> dict[str, Any]:
    home = Path(os.path.expanduser("~"))
    cwd = cwd or Path.cwd()

    entries: list[McpEntry] = []
    entries.extend(_scan_user_configs(home))
    for root in _walk_up_for_projects(cwd):
        entries.extend(_scan_project(root))
    entries.extend(_scan_plugin_caches(home))

    # Detect duplicates (same name registered at multiple scopes).
    by_name: dict[str, list[McpEntry]] = {}
    for e in entries:
        by_name.setdefault(e.name, []).append(e)
    duplicates = {name: [e.to_dict() for e in lst] for name, lst in by_name.items() if len(lst) > 1}

    return {
        "cwd": str(cwd),
        "home": str(home),
        "entries": [e.to_dict() for e in entries],
        "duplicates": duplicates,
        "counts": {
            "total": len(entries),
            "enabled": sum(1 for e in entries if not e.disabled),
            "disabled": sum(1 for e in entries if e.disabled),
            "user_scope": sum(1 for e in entries if e.scope == "user"),
            "project_scope": sum(1 for e in entries if e.scope == "project"),
            "plugin_scope": sum(1 for e in entries if e.scope == "plugin"),
        },
    }


if __name__ == "__main__":
    json.dump(scan(), sys.stdout, indent=2)
    sys.stdout.write("\n")
