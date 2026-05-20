"""Localhost-only dashboard for Claude resource usage.

Serves a single-page UI plus a small JSON API backed by ``process_inspector``
and ``mcp_config_scanner``. No external dependencies. Bound to 127.0.0.1.
"""

from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import threading
import time
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

from process_inspector import inspect, HAVE_PSUTIL  # type: ignore
from mcp_config_scanner import scan as scan_mcp  # type: ignore


ASSETS_DIR = _HERE.parent / "assets"
DEFAULT_PORT = 8765


def _pid_file() -> Path:
    base = os.environ.get("CLAUDE_PLUGIN_DATA")
    root = Path(base) if base else Path.home() / ".claude" / "plugin-data" / "resource-manager"
    root.mkdir(parents=True, exist_ok=True)
    return root / "dashboard.pid"


class _Handler(BaseHTTPRequestHandler):
    server_version = "ResourceManagerDashboard/1.0"

    # Silence default access log — noisy in a long-running process.
    def log_message(self, format: str, *args) -> None:  # noqa: A002 - stdlib signature
        return

    def _send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path: Path, content_type: str) -> None:
        try:
            body = path.read_bytes()
        except OSError:
            self.send_error(HTTPStatus.NOT_FOUND, "asset not found")
            return
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802 - stdlib override
        path = urlparse(self.path).path

        if path in {"/", "/index.html"}:
            return self._send_file(ASSETS_DIR / "dashboard.html", "text/html; charset=utf-8")
        if path == "/api/health":
            return self._send_json(HTTPStatus.OK, {
                "ok": True,
                "have_psutil": HAVE_PSUTIL,
                "pid": os.getpid(),
                "uptime_seconds": round(time.time() - self.server.started_at, 1),  # type: ignore[attr-defined]
            })
        if path == "/api/processes":
            try:
                return self._send_json(HTTPStatus.OK, inspect())
            except Exception as exc:
                return self._send_json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": repr(exc)})
        if path == "/api/mcp-audit":
            try:
                return self._send_json(HTTPStatus.OK, scan_mcp())
            except Exception as exc:
                return self._send_json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": repr(exc)})

        self.send_error(HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:  # noqa: N802 - stdlib override
        path = urlparse(self.path).path

        if path.startswith("/api/kill/"):
            return self._handle_kill(path)
        if path == "/api/shutdown":
            return self._handle_shutdown()

        self.send_error(HTTPStatus.NOT_FOUND)

    def _handle_kill(self, path: str) -> None:
        try:
            pid = int(path.rsplit("/", 1)[-1])
        except ValueError:
            return self._send_json(HTTPStatus.BAD_REQUEST, {"error": "invalid pid"})

        snapshot = inspect()
        target = next(
            (p for p in snapshot["mcp_servers"] if int(p["pid"]) == pid),
            None,
        )
        if target is None:
            return self._send_json(HTTPStatus.FORBIDDEN, {"error": "pid is not an MCP server"})
        if not target.get("is_orphan"):
            return self._send_json(HTTPStatus.FORBIDDEN, {"error": "pid is not flagged as orphan"})

        ok = _terminate(pid)
        return self._send_json(
            HTTPStatus.OK if ok else HTTPStatus.INTERNAL_SERVER_ERROR,
            {"pid": pid, "terminated": ok},
        )

    def _handle_shutdown(self) -> None:
        self._send_json(HTTPStatus.OK, {"stopping": True})
        threading.Thread(target=self.server.shutdown, daemon=True).start()  # type: ignore[attr-defined]


def _terminate(pid: int) -> bool:
    if HAVE_PSUTIL:
        try:
            import psutil  # type: ignore
            p = psutil.Process(pid)
            p.terminate()
            try:
                p.wait(timeout=2)
            except psutil.TimeoutExpired:
                p.kill()
            return not psutil.pid_exists(pid)
        except Exception:
            return False
    if sys.platform.startswith("win"):
        try:
            subprocess.run(
                ["taskkill", "/PID", str(pid), "/T", "/F"],
                capture_output=True, timeout=5, check=False,
            )
            return True
        except Exception:
            return False
    try:
        os.kill(pid, signal.SIGTERM)
        time.sleep(1)
        try:
            os.kill(pid, 0)
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        return True
    except Exception:
        return False


def serve(port: int = DEFAULT_PORT) -> None:
    server = ThreadingHTTPServer(("127.0.0.1", port), _Handler)
    server.started_at = time.time()  # type: ignore[attr-defined]

    pid_file = _pid_file()
    pid_file.write_text(str(os.getpid()), encoding="utf-8")

    def _cleanup(*_: object) -> None:
        try:
            pid_file.unlink(missing_ok=True)
        except Exception:
            pass

    try:
        signal.signal(signal.SIGTERM, lambda *_: server.shutdown())
        if hasattr(signal, "SIGBREAK"):
            signal.signal(signal.SIGBREAK, lambda *_: server.shutdown())  # type: ignore[attr-defined]
    except Exception:
        pass

    print(f"Resource Manager dashboard listening on http://127.0.0.1:{port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        _cleanup()


def main() -> int:
    parser = argparse.ArgumentParser(description="Localhost dashboard for Claude resource usage.")
    parser.add_argument("--port", type=int, default=int(os.environ.get("RESOURCE_MANAGER_PORT", DEFAULT_PORT)))
    args = parser.parse_args()
    serve(args.port)
    return 0


if __name__ == "__main__":
    sys.exit(main())
