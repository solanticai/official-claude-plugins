"""Typed exceptions used across every ppc-manager MCP server.

Tool handlers raise these so the MCP framework serialises a clean error
object back to Claude rather than a raw traceback.
"""

from __future__ import annotations

from typing import Any, Dict, Optional


class ToolError(Exception):
    """Base class for any MCP tool-level error."""

    def __init__(self, message: str, *, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error": type(self).__name__,
            "message": str(self),
            **({"details": self.details} if self.details else {}),
        }


class APIError(ToolError):
    """Upstream platform API returned an error."""


class NotFoundError(ToolError):
    """Resource does not exist."""


class QuotaError(ToolError):
    """Quota or rate-limit exceeded."""


def wrap_http_error(exc: Exception) -> ToolError:
    """Translate a random SDK/HTTP exception into a typed ToolError.

    Best-effort — used at the top of every tool handler as the fallback
    ``except Exception`` branch so the caller always sees structured errors.
    """
    msg = str(exc) or type(exc).__name__
    lowered = msg.lower()
    if "quota" in lowered or "rate" in lowered or "429" in lowered:
        return QuotaError(msg)
    if "not found" in lowered or "404" in lowered:
        return NotFoundError(msg)
    return APIError(msg)
