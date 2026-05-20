"""Stop hook: terminate MCP server processes whose Claude Code parent died.

Guarantees:
- Never kills a process whose parent is alive and tagged claude-family.
- Never raises — exits 0 under all conditions so it cannot block turn completion.
- Logs each action to ``$CLAUDE_PLUGIN_DATA/orphans.log`` for auditability.
"""

from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# Allow importing the shared inspector whether invoked via bash wrapper or direct.
_HERE = Path(__file__).resolve().parent
_SCRIPTS = _HERE.parent.parent / "scripts"
sys.path.insert(0, str(_SCRIPTS))

try:
    from process_inspector import detect_orphans, HAVE_PSUTIL  # type: ignore
except Exception:  # pragma: no cover - hard fail-safe
    sys.exit(0)


GRACE_SECONDS = 2


def _log_path() -> Path:
    base = os.environ.get("CLAUDE_PLUGIN_DATA")
    if base:
        root = Path(base)
    else:
        root = Path.home() / ".claude" / "plugin-data" / "resource-manager"
    root.mkdir(parents=True, exist_ok=True)
    return root / "orphans.log"


def _log(msg: str) -> None:
    try:
        with _log_path().open("a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().isoformat(timespec='seconds')}] {msg}\n")
    except Exception:
        pass


def _terminate(pid: int) -> bool:
    """Best-effort terminate. Returns True if the process is gone."""
    if HAVE_PSUTIL:
        try:
            import psutil  # type: ignore
            p = psutil.Process(pid)
            p.terminate()
            try:
                p.wait(timeout=GRACE_SECONDS)
            except psutil.TimeoutExpired:
                p.kill()
            return not psutil.pid_exists(pid)
        except Exception:
            return False

    if sys.platform.startswith("win"):
        try:
            subprocess.run(
                ["taskkill", "/PID", str(pid), "/T", "/F"],
                capture_output=True,
                timeout=5,
                check=False,
            )
            return True
        except Exception:
            return False

    try:
        os.kill(pid, signal.SIGTERM)
        time.sleep(GRACE_SECONDS)
        try:
            os.kill(pid, 0)
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        return True
    except Exception:
        return False


def main() -> int:
    try:
        orphans = detect_orphans()
    except Exception as exc:
        _log(f"detect_orphans failed: {exc!r}")
        return 0

    if not orphans:
        return 0

    cleaned = 0
    freed_mb = 0.0
    for proc in orphans:
        ok = _terminate(proc.pid)
        if ok:
            cleaned += 1
            freed_mb += proc.memory_mb
            _log(
                f"killed orphan pid={proc.pid} ppid={proc.ppid} "
                f"label={proc.label} mem={proc.memory_mb}MB cmd={proc.cmdline[:160]}"
            )
        else:
            _log(f"failed to kill orphan pid={proc.pid} cmd={proc.cmdline[:160]}")

    if cleaned:
        message = f"Resource Manager: cleaned {cleaned} orphan MCP server{'s' if cleaned != 1 else ''}, freed ~{freed_mb:.0f} MB"
        print(json.dumps({"systemMessage": message}))

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        # Absolute last-resort safety net.
        sys.exit(0)
