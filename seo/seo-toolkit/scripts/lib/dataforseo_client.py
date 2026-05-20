"""DataForSEO client for seo-toolkit.

Provides keyword suggestions and search volume lookups via the DataForSEO
Keywords Data API. Credentials (login + password) are read from the encrypted
vault under provider ``dataforseo``.

Location code 2036 = Australia.

Usage::

    from scripts.lib.dataforseo_client import keyword_suggestions, keyword_volume

    suggestions = keyword_suggestions("accounting software", location_code=2036)
    volumes = keyword_volume(["accounting software", "bookkeeping app"], location_code=2036)
"""

from __future__ import annotations

import base64
import os
from typing import Any

import httpx

from .seo_vault import get_secret

_DFS_BASE = "https://api.dataforseo.com/v3"


def _get_auth_header() -> str:
    """Return Basic Auth header value derived from vault credentials."""
    passphrase = os.environ.get("SEO_VAULT_PASSPHRASE", "")
    login = password = ""
    if passphrase:
        login = get_secret("dataforseo", "login", passphrase) or ""
        password = get_secret("dataforseo", "password", passphrase) or ""
    # Fallbacks for scripted usage
    login = login or os.environ.get("DATAFORSEO_LOGIN", "")
    password = password or os.environ.get("DATAFORSEO_PASSWORD", "")
    if not login or not password:
        raise RuntimeError(
            "DataForSEO credentials not found. "
            "Run /seo-toolkit:seo-connect dataforseo to configure them."
        )
    token = base64.b64encode(f"{login}:{password}".encode()).decode()
    return f"Basic {token}"


def _post(endpoint: str, payload: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """POST *payload* to DataForSEO *endpoint*, returning the ``tasks`` list."""
    auth = _get_auth_header()
    with httpx.Client(timeout=60.0) as client:
        response = client.post(
            f"{_DFS_BASE}/{endpoint}",
            json=payload,
            headers={"Authorization": auth, "Content-Type": "application/json"},
        )
        response.raise_for_status()
    body: dict[str, Any] = response.json()
    tasks: list[dict[str, Any]] = body.get("tasks", [])
    return tasks


def keyword_suggestions(
    seed: str,
    location_code: int = 2036,
    language_code: str = "en",
    limit: int = 100,
) -> list[dict[str, Any]]:
    """Return keyword suggestions related to *seed*.

    Args:
        seed:          Seed keyword to expand.
        location_code: DataForSEO location code (2036 = Australia).
        language_code: Language code (default: ``"en"``).
        limit:         Maximum number of suggestions to return.

    Returns:
        List of keyword dicts with ``keyword``, ``search_volume``,
        ``competition``, ``cpc``, and ``keyword_difficulty`` fields.
    """
    payload = [
        {
            "keyword": seed,
            "location_code": location_code,
            "language_code": language_code,
            "limit": limit,
        }
    ]
    tasks = _post("keywords_data/google_ads/keywords_for_keywords/live", payload)
    results: list[dict[str, Any]] = []
    for task in tasks:
        for item in (task.get("result") or []):
            results.extend(item.get("items") or [])
    return results


def keyword_volume(
    keywords: list[str],
    location_code: int = 2036,
    language_code: str = "en",
) -> list[dict[str, Any]]:
    """Return search volume data for a list of exact keywords.

    Args:
        keywords:      List of keywords to look up (max 700 per call).
        location_code: DataForSEO location code (2036 = Australia).
        language_code: Language code (default: ``"en"``).

    Returns:
        List of dicts with ``keyword``, ``search_volume``, ``competition``,
        ``cpc``, and ``keyword_difficulty`` fields.
    """
    payload = [
        {
            "keywords": keywords,
            "location_code": location_code,
            "language_code": language_code,
        }
    ]
    tasks = _post("keywords_data/google_ads/search_volume/live", payload)
    results: list[dict[str, Any]] = []
    for task in tasks:
        for item in (task.get("result") or []):
            results.extend(item.get("items") or [])
    return results
