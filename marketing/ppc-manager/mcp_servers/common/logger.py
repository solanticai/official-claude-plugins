"""Thin wrapper around ``scripts/lib/masking_logger`` for MCP server use.

Kept separate so MCP servers can import ``mcp_servers.common.logger`` instead
of reaching into ``scripts.lib``. Also gives us a place to add MCP-specific
logging conventions later without touching the shared library.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

_SCRIPTS_LIB = Path(__file__).resolve().parents[2] / "scripts"
if str(_SCRIPTS_LIB) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_LIB))

from lib.masking_logger import get_logger  # noqa: E402


def get_server_logger(name: str) -> logging.Logger:
    """Return a masked-stderr logger for an MCP server tool module."""
    return get_logger(name)
