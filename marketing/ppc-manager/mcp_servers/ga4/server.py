#!/usr/bin/env python3
"""ppc-ga4 MCP server entry point.

FastMCP server exposing ~12 tools for Google Analytics 4 Admin API and Data API
operations. Every tool reads credentials from the encrypted ppc-manager vault
via ``scripts/lib/ppc_auth.PPCAuth.from_env()``.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

_PLUGIN_ROOT = Path(__file__).resolve().parents[2]
_SCRIPTS_DIR = _PLUGIN_ROOT / "scripts"
for p in (str(_PLUGIN_ROOT), str(_SCRIPTS_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

os.environ.setdefault("OAUTHLIB_RELAX_TOKEN_SCOPE", "1")

from fastmcp import FastMCP  # noqa: E402

from lib.ppc_auth import PPCAuth  # noqa: E402
from mcp_servers.common.logger import get_server_logger  # noqa: E402
from mcp_servers.ga4.tools import admin, reporting, events  # noqa: E402

logger = get_server_logger("ppc-ga4")

mcp = FastMCP("ppc-ga4")

_auth: PPCAuth | None = None


def get_auth() -> PPCAuth:
    global _auth
    if _auth is None:
        _auth = PPCAuth.from_env()
        logger.info("ppc-ga4 MCP server: PPCAuth initialised")
    return _auth


admin.register(mcp, get_auth)
reporting.register(mcp, get_auth)
events.register(mcp, get_auth)


def main() -> None:  # pragma: no cover
    logger.info("Starting ppc-ga4 MCP server")
    mcp.run()


if __name__ == "__main__":  # pragma: no cover
    main()
