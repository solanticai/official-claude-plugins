"""Google Analytics 4 client for seo-toolkit.

Wraps the Google Analytics Data API (GA4) using OAuth credentials stored in
the encrypted vault under provider ``ga4``.

Usage::

    from scripts.lib.ga4_client import run_report

    result = run_report(
        property_id="properties/123456789",
        date_range={"start_date": "2026-02-20", "end_date": "2026-05-20"},
        dimensions=[{"name": "sessionDefaultChannelGroup"}],
        metrics=[{"name": "sessions"}, {"name": "conversions"}],
    )
"""

from __future__ import annotations

import os
from datetime import timezone
from typing import Any

from .seo_vault import get_secret, set_secret

_GA4_SCOPE = "https://www.googleapis.com/auth/analytics.readonly"


def _get_credentials():
    """Build and (if necessary refresh) Google OAuth credentials from the vault."""
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request

    passphrase = os.environ.get("SEO_VAULT_PASSPHRASE", "")
    if not passphrase:
        raise RuntimeError(
            "SEO_VAULT_PASSPHRASE not set — cannot read GA4 credentials from vault."
        )

    refresh_token = get_secret("ga4", "refresh_token", passphrase)
    access_token = get_secret("ga4", "access_token", passphrase)
    client_id = get_secret("ga4", "client_id", passphrase)
    client_secret = get_secret("ga4", "client_secret", passphrase)

    if not refresh_token:
        raise RuntimeError(
            "GA4 refresh token not found. Run /seo-toolkit:seo-connect ga4 to authenticate."
        )

    creds = Credentials(
        token=access_token,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=[_GA4_SCOPE],
    )

    if not creds.valid:
        creds.refresh(Request())
        set_secret("ga4", "access_token", creds.token, passphrase)
        if creds.expiry:
            expiry = creds.expiry
            if expiry.tzinfo is None:
                expiry = expiry.replace(tzinfo=timezone.utc)
            set_secret("ga4", "access_token_expires_at", expiry.isoformat(), passphrase)

    return creds


def run_report(
    property_id: str,
    date_range: dict[str, str],
    dimensions: list[dict[str, str]],
    metrics: list[dict[str, str]],
    limit: int = 10_000,
) -> dict[str, Any]:
    """Run a GA4 Data API report.

    Args:
        property_id: GA4 property in the format ``"properties/XXXXXXXXX"``.
        date_range:  Dict with ``start_date`` and ``end_date`` keys (``"YYYY-MM-DD"``).
        dimensions:  List of dimension dicts, e.g. ``[{"name": "sessionSource"}]``.
        metrics:     List of metric dicts, e.g. ``[{"name": "sessions"}]``.
        limit:       Maximum rows to return.

    Returns:
        Full API response dict with ``dimensionHeaders``, ``metricHeaders``,
        and ``rows`` fields.
    """
    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    from google.analytics.data_v1beta.types import (
        DateRange,
        Dimension,
        Metric,
        RunReportRequest,
    )

    creds = _get_credentials()
    client = BetaAnalyticsDataClient(credentials=creds)

    request = RunReportRequest(
        property=property_id,
        date_ranges=[DateRange(**date_range)],
        dimensions=[Dimension(**d) for d in dimensions],
        metrics=[Metric(**m) for m in metrics],
        limit=limit,
    )
    response = client.run_report(request)

    # Convert protobuf response to a plain dict for downstream processing
    rows = []
    for row in response.rows:
        rows.append(
            {
                "dimensions": [dv.value for dv in row.dimension_values],
                "metrics": [mv.value for mv in row.metric_values],
            }
        )

    return {
        "dimension_headers": [h.name for h in response.dimension_headers],
        "metric_headers": [h.name for h in response.metric_headers],
        "rows": rows,
        "row_count": response.row_count,
    }
