#!/usr/bin/env python3
"""ppc-google-ads MCP server entry point.

Exposes ~25 tools for Google Ads campaign management. Every tool reads
credentials from the encrypted ppc-manager vault via
``scripts/lib/ppc_auth.PPCAuth.from_env()``.
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
from mcp_servers.google_ads.tools import (  # noqa: E402
    accounts,
    campaigns,
    ad_groups,
    ads,
    keywords,
    reporting,
    targeting,
    budgets,
    bidding,
    assets,
)

logger = get_server_logger("ppc-google-ads")

mcp = FastMCP("ppc-google-ads")

_auth: PPCAuth | None = None


def get_auth() -> PPCAuth:
    global _auth
    if _auth is None:
        _auth = PPCAuth.from_env()
        logger.info("ppc-google-ads MCP server: PPCAuth initialised")
    return _auth


accounts.register(mcp, get_auth)
campaigns.register(mcp, get_auth)
ad_groups.register(mcp, get_auth)
ads.register(mcp, get_auth)
keywords.register(mcp, get_auth)
reporting.register(mcp, get_auth)
targeting.register(mcp, get_auth)
budgets.register(mcp, get_auth)
bidding.register(mcp, get_auth)
assets.register(mcp, get_auth)


def main() -> None:  # pragma: no cover
    logger.info("Starting ppc-google-ads MCP server")
    mcp.run()


if __name__ == "__main__":  # pragma: no cover
    main()
