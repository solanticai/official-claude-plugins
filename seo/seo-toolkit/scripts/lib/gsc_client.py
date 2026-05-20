"""Google Search Console client for seo-toolkit.

Wraps the GSC Search Analytics API using OAuth credentials stored in the
encrypted vault under provider ``gsc``.

Usage::

    from scripts.lib.gsc_client import query_search_analytics

    rows = query_search_analytics(
        site_url="https://example.com.au/",
        start_date="2026-02-20",
        end_date="2026-05-20",
        dimensions=["query", "page"],
        row_limit=1000,
    )
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

from .seo_vault import get_secret, set_secret

_GSC_SCOPE = "https://www.googleapis.com/auth/webmasters.readonly"


def _get_credentials():
    """Build and (if necessary refresh) Google OAuth credentials from the vault."""
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request

    passphrase = os.environ.get("SEO_VAULT_PASSPHRASE", "")
    if not passphrase:
        raise RuntimeError(
            "SEO_VAULT_PASSPHRASE not set — cannot read GSC credentials from vault."
        )

    refresh_token = get_secret("gsc", "refresh_token", passphrase)
    access_token = get_secret("gsc", "access_token", passphrase)
    client_id = get_secret("gsc", "client_id", passphrase)
    client_secret = get_secret("gsc", "client_secret", passphrase)

    if not refresh_token:
        raise RuntimeError(
            "GSC refresh token not found. Run /seo-toolkit:seo-connect gsc to authenticate."
        )

    creds = Credentials(
        token=access_token,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=[_GSC_SCOPE],
    )

    if not creds.valid:
        creds.refresh(Request())
        # Persist refreshed access token
        set_secret("gsc", "access_token", creds.token, passphrase)
        if creds.expiry:
            expiry = creds.expiry
            if expiry.tzinfo is None:
                expiry = expiry.replace(tzinfo=timezone.utc)
            set_secret("gsc", "access_token_expires_at", expiry.isoformat(), passphrase)

    return creds


def query_search_analytics(
    site_url: str,
    start_date: str,
    end_date: str,
    dimensions: list[str] | None = None,
    row_limit: int = 1000,
    start_row: int = 0,
) -> list[dict[str, Any]]:
    """Query the GSC Search Analytics API.

    Args:
        site_url:   The verified GSC property URL (e.g. ``"https://example.com.au/"``).
        start_date: ISO date string ``"YYYY-MM-DD"``.
        end_date:   ISO date string ``"YYYY-MM-DD"``.
        dimensions: List of dimensions to group by. Valid values: ``"query"``,
                    ``"page"``, ``"country"``, ``"device"``, ``"searchAppearance"``.
                    Defaults to ``["query"]``.
        row_limit:  Maximum rows to return (max 25 000 per request).
        start_row:  Pagination offset.

    Returns:
        List of row dicts. Each row contains ``keys`` (list of dimension values)
        plus ``clicks``, ``impressions``, ``ctr``, ``position`` fields.
    """
    from googleapiclient.discovery import build

    if dimensions is None:
        dimensions = ["query"]

    creds = _get_credentials()
    service = build("searchconsole", "v1", credentials=creds, cache_discovery=False)

    body: dict[str, Any] = {
        "startDate": start_date,
        "endDate": end_date,
        "dimensions": dimensions,
        "rowLimit": row_limit,
        "startRow": start_row,
    }

    response = (
        service.searchanalytics()
        .query(siteUrl=site_url, body=body)
        .execute()
    )
    return response.get("rows", [])
