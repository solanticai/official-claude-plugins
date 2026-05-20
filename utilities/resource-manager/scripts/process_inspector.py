"""Enumerate Claude-family processes and classify them.

Single source of truth for the orphan-killer hook, the dashboard server,
and the resource-snapshot skill. Uses ``psutil`` when available and falls
back to platform-native tools (``wmic`` on Windows, ``ps`` elsewhere) so
the plugin works on a fresh machine with no pip installs.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field, asdict
from typing import Any

try:
    import psutil  # type: ignore
    HAVE_PSUTIL = True
except ImportError:
    HAVE_PSUTIL = False


CLAUDE_EXE_NAMES = {"claude.exe", "claude"}
PYTHON_EXE_NAMES = {"python.exe", "python", "python3", "python3.exe"}
NODE_EXE_NAMES = {"node.exe", "node"}
CODEX_EXE_NAMES = {"codex.exe", "codex"}

MCP_PATH_HINTS = (
    "fastmcp_",
    "mcp_server",
    "mcp-server",
    "mcp_servers",
    "/mcp/",
    "\\mcp\\",
    "/MCP/",
    "\\MCP\\",
    "modelcontextprotocol",
)

DESKTOP_INSTALL_HINT = "WindowsApps\\Claude_"
CODE_CLI_HINT = "claude-code"
VSCODE_EXT_HINT = "vscode\\extensions\\anthropic.claude"


@dataclass
class Proc:
    pid: int
    ppid: int
    name: str
    cmdline: str
    label: str
    memory_mb: float
    cpu_percent: float = 0.0
    create_time: float = 0.0
    exe: str = ""
    # Populated after classification:
    is_mcp: bool = False
    is_orphan: bool = False
    parent_label: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _run(cmd: list[str]) -> str:
    try:
        out = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        return out.stdout or ""
    except Exception:
        return ""


def _iter_procs_psutil() -> list[Proc]:
    procs: list[Proc] = []
    for p in psutil.process_iter(
        ["pid", "ppid", "name", "cmdline", "memory_info", "create_time", "exe"]
    ):
        try:
            info = p.info
            name = (info.get("name") or "").strip()
            cmd_list = info.get("cmdline") or []
            cmdline = " ".join(cmd_list) if cmd_list else ""
            mem = info.get("memory_info")
            mem_mb = round((mem.rss if mem else 0) / (1024 * 1024), 1)
            procs.append(
                Proc(
                    pid=info.get("pid") or 0,
                    ppid=info.get("ppid") or 0,
                    name=name,
                    cmdline=cmdline,
                    label="",
                    memory_mb=mem_mb,
                    create_time=info.get("create_time") or 0.0,
                    exe=info.get("exe") or "",
                )
            )
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return procs


def _iter_procs_windows() -> list[Proc]:
    # Fallback using PowerShell CIM — more reliable than wmic on modern Windows.
    ps_script = (
        "Get-CimInstance Win32_Process | "
        "Select-Object ProcessId,ParentProcessId,Name,CommandLine,WorkingSetSize,CreationDate,ExecutablePath | "
        "ConvertTo-Json -Depth 2 -Compress"
    )
    raw = _run(["powershell", "-NoProfile", "-Command", ps_script])
    if not raw.strip():
        return []
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return []
    if isinstance(data, dict):
        data = [data]
    procs: list[Proc] = []
    for row in data:
        try:
            created = row.get("CreationDate") or ""
            ctime = _parse_cim_date(created)
            mem_mb = round((row.get("WorkingSetSize") or 0) / (1024 * 1024), 1)
            procs.append(
                Proc(
                    pid=int(row.get("ProcessId") or 0),
                    ppid=int(row.get("ParentProcessId") or 0),
                    name=(row.get("Name") or "").strip(),
                    cmdline=(row.get("CommandLine") or "").strip(),
                    label="",
                    memory_mb=mem_mb,
                    create_time=ctime,
                    exe=(row.get("ExecutablePath") or "").strip(),
                )
            )
        except Exception:
            continue
    return procs


def _parse_cim_date(value: str) -> float:
    # CIM DateTime JSON form: "/Date(1713776381000)/" on some hosts, or ISO string.
    if not value:
        return 0.0
    m = re.match(r"/Date\((\d+)\)/", value)
    if m:
        return int(m.group(1)) / 1000.0
    try:
        # ISO fallback
        import datetime as _dt
        return _dt.datetime.fromisoformat(value).timestamp()
    except Exception:
        return 0.0


def _iter_procs_posix() -> list[Proc]:
    raw = _run(["ps", "-eo", "pid,ppid,rss,lstart,comm,args", "-ww"])
    procs: list[Proc] = []
    for line in raw.splitlines()[1:]:
        parts = line.strip().split(None, 9)
        if len(parts) < 10:
            continue
        try:
            pid = int(parts[0])
            ppid = int(parts[1])
            rss_kb = int(parts[2])
            # lstart takes 5 tokens (Weekday Mon Day HH:MM:SS Year)
            name = parts[8]
            cmdline = parts[9]
            procs.append(
                Proc(
                    pid=pid,
                    ppid=ppid,
                    name=name,
                    cmdline=cmdline,
                    label="",
                    memory_mb=round(rss_kb / 1024, 1),
                )
            )
        except (ValueError, IndexError):
            continue
    return procs


def enumerate_processes() -> list[Proc]:
    """Return every running process with enough metadata to classify it."""
    if HAVE_PSUTIL:
        try:
            return _iter_procs_psutil()
        except Exception:
            pass
    if sys.platform.startswith("win"):
        return _iter_procs_windows()
    return _iter_procs_posix()


def classify_process(name: str, cmdline: str) -> str:
    """Return a short label describing what the process is."""
    lower_name = name.lower()
    lower_cmd = cmdline.lower()

    if lower_name in CODEX_EXE_NAMES or "openai.chatgpt" in lower_cmd:
        return "codex"

    if lower_name in CLAUDE_EXE_NAMES or "claude.exe" in lower_cmd:
        if "--type=renderer" in lower_cmd:
            return "desktop-renderer"
        if "--type=gpu-process" in lower_cmd:
            return "desktop-gpu"
        if "--type=utility" in lower_cmd:
            if "audio" in lower_cmd:
                return "desktop-audio"
            if "video" in lower_cmd:
                return "desktop-video"
            if "network" in lower_cmd:
                return "desktop-network"
            if "nodeservice" in lower_cmd:
                return "desktop-node-service"
            return "desktop-utility"
        if "--type=crashpad-handler" in lower_cmd:
            return "desktop-crashpad"
        if CODE_CLI_HINT in cmdline or "claude-code\\" in cmdline or "claude-code/" in cmdline:
            return "code-cli"
        if VSCODE_EXT_HINT in cmdline.replace("/", "\\").lower():
            return "code-vscode-ext"
        if DESKTOP_INSTALL_HINT in cmdline:
            return "desktop-main"
        # Fallback Claude executable we can't classify precisely
        return "claude-unknown"

    if lower_name in PYTHON_EXE_NAMES or lower_name in NODE_EXE_NAMES:
        if any(hint.lower() in lower_cmd for hint in MCP_PATH_HINTS):
            return "mcp-server"

    return "other"


def _is_pid_alive(pid: int, snapshot: dict[int, Proc]) -> bool:
    if pid in snapshot:
        return True
    if HAVE_PSUTIL:
        try:
            return psutil.pid_exists(pid)
        except Exception:
            return False
    # Fallback: absence from snapshot is the best we can do.
    return False


def inspect() -> dict[str, Any]:
    """Produce a full snapshot of Claude-family processes + orphan flags."""
    procs = enumerate_processes()
    by_pid: dict[int, Proc] = {}

    for p in procs:
        p.label = classify_process(p.name, p.cmdline)
        if p.label == "mcp-server":
            p.is_mcp = True
        by_pid[p.pid] = p

    # Parent labels + orphan detection for MCP servers
    for p in procs:
        parent = by_pid.get(p.ppid)
        p.parent_label = parent.label if parent else ""
        if p.is_mcp:
            parent_alive = _is_pid_alive(p.ppid, by_pid)
            parent_is_claude = (
                parent is not None
                and parent.label in {"code-cli", "code-vscode-ext", "desktop-main", "claude-unknown"}
            )
            p.is_orphan = not parent_alive or not parent_is_claude

    # Partition results for callers
    claude_family: list[Proc] = [p for p in procs if p.label.startswith(("desktop-", "code-", "claude-"))]
    mcp_servers: list[Proc] = [p for p in procs if p.is_mcp]
    orphans: list[Proc] = [p for p in mcp_servers if p.is_orphan]
    codex: list[Proc] = [p for p in procs if p.label == "codex"]

    total_mem = round(sum(p.memory_mb for p in claude_family + mcp_servers + codex), 1)

    return {
        "generated_at": time.time(),
        "totals": {
            "claude_processes": len(claude_family),
            "mcp_servers": len(mcp_servers),
            "orphans": len(orphans),
            "codex_processes": len(codex),
            "total_memory_mb": total_mem,
        },
        "claude_family": [p.to_dict() for p in claude_family],
        "mcp_servers": [p.to_dict() for p in mcp_servers],
        "orphans": [p.to_dict() for p in orphans],
        "codex": [p.to_dict() for p in codex],
    }


def detect_orphans() -> list[Proc]:
    procs = enumerate_processes()
    by_pid = {p.pid: p for p in procs}
    for p in procs:
        p.label = classify_process(p.name, p.cmdline)
        p.is_mcp = p.label == "mcp-server"
    orphans: list[Proc] = []
    for p in procs:
        if not p.is_mcp:
            continue
        parent = by_pid.get(p.ppid)
        parent_alive = _is_pid_alive(p.ppid, by_pid)
        parent_is_claude = (
            parent is not None
            and parent.label in {"code-cli", "code-vscode-ext", "desktop-main", "claude-unknown"}
        )
        if not parent_alive or not parent_is_claude:
            p.is_orphan = True
            orphans.append(p)
    return orphans


if __name__ == "__main__":
    # CLI invocation: ``python process_inspector.py`` prints JSON snapshot.
    json.dump(inspect(), sys.stdout, indent=2, default=str)
    sys.stdout.write("\n")
