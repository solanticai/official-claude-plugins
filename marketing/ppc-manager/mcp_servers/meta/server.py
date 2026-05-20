#!/usr/bin/env python3
"""ppc-meta MCP server entry point.

FastMCP server exposing ~20 tools for the Meta Marketing API (ad accounts,
campaigns, ad sets, ads, creatives, audiences, pixels, CAPI, insights).

Built from scratch on top of ``facebook_business`` SDK. Credentials come from
the ppc-manager vault via ``PPCAuth.from_env()``.
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

from fastmcp import FastMCP  # noqa: E402

from lib.ppc_auth import PPCAuth  # noqa: E402
from mcp_servers.common.logger import get_server_logger  # noqa: E402
from mcp_servers.meta.tools import (  # noqa: E402
    accounts,
    campaigns,
    ad_sets,
    ads,
    audiences,
    insights,
    pixels,
    capi,
    targeting_search,
    images,
    pages,
)

logger = get_server_logger("ppc-meta")

mcp = FastMCP("ppc-meta")

_auth: PPCAuth | None = None


def get_auth() -> PPCAuth:
    global _auth
    if _auth is None:
        _auth = PPCAuth.from_env()
        logger.info("ppc-meta MCP server: PPCAuth initialised")
    return _auth


accounts.register(mcp, get_auth)
campaigns.register(mcp, get_auth)
ad_sets.register(mcp, get_auth)
ads.register(mcp, get_auth)
audiences.register(mcp, get_auth)
insights.register(mcp, get_auth)
pixels.register(mcp, get_auth)
capi.register(mcp, get_auth)
targeting_search.register(mcp, get_auth)
images.register(mcp, get_auth)
pages.register(mcp, get_auth)


def main() -> None:  # pragma: no cover
    logger.info("Starting ppc-meta MCP server")
    mcp.run()


if __name__ == "__main__":  # pragma: no cover
    main()
