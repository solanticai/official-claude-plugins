"""Moz API client for seo-toolkit (stub).

Provides Domain Authority and link metrics via the Moz Links API v2.
Credentials (Access ID + Secret) are read from the encrypted vault under
provider ``moz``.

Usage::

    from scripts.lib.moz_client import domain_authority, link_metrics

    da = domain_authority("example.com.au")
    metrics = link_metrics("https://example.com.au/page/")
"""

from __future__ import annotations

import base64
import os
from typing import Any

import httpx

from .seo_vault import get_secret

_MOZ_BASE = "https://lsapi.seomoz.com/v2"


def _get_auth_header() -> str:
    """Return Basic Auth header derived from vault credentials."""
    passphrase = os.environ.get("SEO_VAULT_PASSPHRASE", "")
    access_id = secret = ""
    if passphrase:
        access_id = get_secret("moz", "access_id", passphrase) or ""
        secret = get_secret("moz", "secret", passphrase) or ""
    access_id = access_id or os.environ.get("MOZ_ACCESS_ID", "")
    secret = secret or os.environ.get("MOZ_SECRET", "")
    if not access_id or not secret:
        raise RuntimeError(
            "Moz credentials not found. Run /seo-toolkit:seo-connect moz to configure them."
        )
    token = base64.b64encode(f"{access_id}:{secret}".encode()).decode()
    return f"Basic {token}"


def _post(endpoint: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Authenticated POST against the Moz Links API."""
    auth = _get_auth_header()
    with httpx.Client(timeout=30.0) as client:
        response = client.post(
            f"{_MOZ_BASE}/{endpoint}",
            json=payload,
            headers={"Authorization": auth, "Content-Type": "application/json"},
        )
        response.raise_for_status()
    return response.json()


def domain_authority(domain: str) -> dict[str, Any]:
    """Return Domain Authority and related metrics for *domain*.

    Args:
        domain: The root domain (e.g. ``"example.com.au"``).

    Returns:
        Dict with ``domain``, ``domain_authority``, ``page_authority``,
        ``spam_score``, ``linking_root_domains``, and ``total_links`` fields.
    """
    data = _post(
        "url_metrics",
        {
            "targets": [domain],
            "scope": "root_domain",
        },
    )
    results: list[dict[str, Any]] = data.get("results", [])
    return results[0] if results else {}


def link_metrics(target: str) -> dict[str, Any]:
    """Return link metrics for a specific *target* URL.

    Args:
        target: Full URL (e.g. ``"https://example.com.au/blog/post/"``).

    Returns:
        Dict with ``url``, ``page_authority``, ``domain_authority``,
        ``spam_score``, ``linking_root_domains``, and ``total_links`` fields.
    """
    data = _post(
        "url_metrics",
        {
            "targets": [target],
            "scope": "page",
        },
    )
    results: list[dict[str, Any]] = data.get("results", [])
    return results[0] if results else {}
