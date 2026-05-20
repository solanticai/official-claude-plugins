"""Stderr logger with a filter that masks OAuth tokens before they are logged.

All ppc-manager Python code should import ``get_logger`` from this module
instead of calling ``logging.getLogger(__name__)`` directly. That way,
accidental ``logger.info(f"creds={creds}")`` calls never leak refresh tokens
into the transcript or install logs.

Masking rules (applied via regex on the formatted record):

- Any substring matching ``ya29\\.[A-Za-z0-9_-]+`` (Google access tokens)
- Any substring matching ``1//[A-Za-z0-9_-]+`` (Google refresh tokens)
- Any substring matching ``EAAB[A-Za-z0-9_-]+`` (Meta long-lived tokens)
- Any value of a key named ``refresh_token``, ``access_token``,
  ``long_lived_user_token``, ``client_secret``, ``app_secret``, or
  ``developer_token`` inside a JSON-looking fragment.

Masked values are replaced with ``<MASKED:first4...last4>`` so the log still
gives enough context to distinguish tokens without exposing them.
"""

from __future__ import annotations

import logging
import re
import sys
from typing import Match

_TOKEN_PATTERNS = [
    # Google access token (ya29.AbCdEf...)
    re.compile(r"(ya29\.[A-Za-z0-9_-]{8,})"),
    # Google refresh token (1//0gXXX...)
    re.compile(r"(1//[A-Za-z0-9_-]{8,})"),
    # Meta long-lived token (EAABxxx...)
    re.compile(r"(EAAB[A-Za-z0-9_-]{8,})"),
    # Google Ads developer token (30-ish chars of hex-ish)
    re.compile(
        r"(?<![A-Za-z0-9])([A-Za-z0-9_-]{22,26})(?![A-Za-z0-9])",
        # Note: this pattern is wide; it's intentionally paired with keyed
        # masking below to avoid over-masking random identifiers.
    ),
]

_KEY_PATTERNS = [
    re.compile(
        rf'("?{key}"?\s*[:=]\s*")([^"]+)(")',
        re.IGNORECASE,
    )
    for key in (
        "refresh_token",
        "access_token",
        "long_lived_user_token",
        "client_secret",
        "app_secret",
        "developer_token",
        "ppc_vault_passphrase",
    )
]


def _mask_value(value: str) -> str:
    if len(value) <= 8:
        return "<MASKED>"
    return f"<MASKED:{value[:4]}...{value[-4:]}>"


def _mask_match(match: Match[str]) -> str:
    return _mask_value(match.group(1))


def _mask_keyed(match: Match[str]) -> str:
    prefix, value, suffix = match.group(1), match.group(2), match.group(3)
    return f"{prefix}{_mask_value(value)}{suffix}"


def mask_string(s: str) -> str:
    """Apply all masking rules to a free-form string."""
    for pattern in _TOKEN_PATTERNS[:3]:  # skip the over-wide developer-token pattern
        s = pattern.sub(_mask_match, s)
    for pattern in _KEY_PATTERNS:
        s = pattern.sub(_mask_keyed, s)
    return s


class MaskingFilter(logging.Filter):
    """Logging filter that rewrites ``record.msg`` through ``mask_string``."""

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            msg = record.getMessage()
        except Exception:
            return True
        masked = mask_string(msg)
        if masked != msg:
            record.msg = masked
            record.args = ()
        return True


_CONFIGURED = False


def get_logger(name: str) -> logging.Logger:
    """Return a logger that writes masked output to stderr.

    Idempotent — the first call configures the root logger, subsequent calls
    just return named children.
    """
    global _CONFIGURED
    if not _CONFIGURED:
        root = logging.getLogger()
        root.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(
            logging.Formatter(
                fmt="%(asctime)s %(levelname)s %(name)s: %(message)s",
                datefmt="%Y-%m-%dT%H:%M:%S%z",
            )
        )
        handler.addFilter(MaskingFilter())
        root.handlers[:] = [handler]
        _CONFIGURED = True
    return logging.getLogger(name)
