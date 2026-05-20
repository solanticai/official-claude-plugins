#!/usr/bin/env python3
"""ppc-gtm MCP server entry point.

FastMCP server that exposes ~15 tools for Google Tag Manager operations.
Every tool reads credentials from the encrypted ppc-manager vault via
``scripts/lib/ppc_auth.PPCAuth.from_env()``.

Environment variables (set by ``.mcp.json``):
    PPC_VAULT_PATH          Path to the encrypted vault.
    PPC_VAULT_PASSPHRASE    Passphrase derived from userConfig.
    PPC_DEFAULT_GOOGLE_ACCOUNT (optional) Default account label.
    PYTHONPATH              Plugin root so ``scripts.*`` is importable.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Make sibling scripts/ importable when invoked via python_shim.sh
_PLUGIN_ROOT = Path(__file__).resolve().parents[2]
_SCRIPTS_DIR = _PLUGIN_ROOT / "scripts"
for p in (str(_PLUGIN_ROOT), str(_SCRIPTS_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

# Relax OAuth scope validation so Google's slightly-wider returned scopes don't
# fail the token refresh check.
os.environ.setdefault("OAUTHLIB_RELAX_TOKEN_SCOPE", "1")

from fastmcp import FastMCP  # noqa: E402

from lib.ppc_auth import PPCAuth  # noqa: E402
from mcp_servers.common.logger import get_server_logger  # noqa: E402
from mcp_servers.gtm.tools import containers, tags, triggers, variables, versions  # noqa: E402

logger = get_server_logger("ppc-gtm")

mcp = FastMCP("ppc-gtm")

_auth: PPCAuth | None = None


def get_auth() -> PPCAuth:
    """Return a lazy-initialised PPCAuth singleton for this server process."""
    global _auth
    if _auth is None:
        _auth = PPCAuth.from_env()
        logger.info("ppc-gtm MCP server: PPCAuth initialised")
    return _auth


# Register all tool modules
containers.register(mcp, get_auth)
tags.register(mcp, get_auth)
triggers.register(mcp, get_auth)
variables.register(mcp, get_auth)
versions.register(mcp, get_auth)


def main() -> None:  # pragma: no cover
    """Entry point when invoked as a script."""
    logger.info("Starting ppc-gtm MCP server")
    mcp.run()


if __name__ == "__main__":  # pragma: no cover
    main()
