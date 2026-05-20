"""Helpers for Meta (Facebook) Graph API calls used during OAuth and setup.

Kept separate from ``ppc_auth.py`` to keep that file focused on credential
lookup. These helpers do NOT depend on the vault.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import httpx

GRAPH_BASE = "https://graph.facebook.com/v22.0"


class MetaAPIError(Exception):
    """Raised when a Graph API call fails."""


def exchange_long_lived_token(app_id: str, app_secret: str, short_token: str) -> Dict[str, Any]:
    """Exchange a short-lived user access token for a long-lived one.

    Returns the Graph API payload, which includes ``access_token`` and
    ``expires_in``.
    """
    response = httpx.get(
        f"{GRAPH_BASE}/oauth/access_token",
        params={
            "grant_type": "fb_exchange_token",
            "client_id": app_id,
            "client_secret": app_secret,
            "fb_exchange_token": short_token,
        },
        timeout=20.0,
    )
    if response.status_code != 200:
        raise MetaAPIError(
            f"Long-lived token exchange failed: {response.status_code} {response.text[:300]}"
        )
    return response.json()


def exchange_code_for_token(
    app_id: str, app_secret: str, redirect_uri: str, code: str
) -> Dict[str, Any]:
    """Exchange an OAuth authorisation code for a short-lived access token."""
    response = httpx.get(
        f"{GRAPH_BASE}/oauth/access_token",
        params={
            "client_id": app_id,
            "client_secret": app_secret,
            "redirect_uri": redirect_uri,
            "code": code,
        },
        timeout=20.0,
    )
    if response.status_code != 200:
        raise MetaAPIError(
            f"Code exchange failed: {response.status_code} {response.text[:300]}"
        )
    return response.json()


def get_user_ad_accounts(access_token: str) -> List[Dict[str, Any]]:
    """Return the ad accounts accessible to the current user token."""
    response = httpx.get(
        f"{GRAPH_BASE}/me/adaccounts",
        params={
            "access_token": access_token,
            "fields": "id,account_id,name,currency,timezone_name,account_status",
            "limit": 100,
        },
        timeout=20.0,
    )
    if response.status_code != 200:
        raise MetaAPIError(
            f"me/adaccounts failed: {response.status_code} {response.text[:300]}"
        )
    return response.json().get("data", [])


def get_user_info(access_token: str) -> Dict[str, Any]:
    """Return basic user info (id, name)."""
    response = httpx.get(
        f"{GRAPH_BASE}/me",
        params={"access_token": access_token, "fields": "id,name"},
        timeout=20.0,
    )
    if response.status_code != 200:
        raise MetaAPIError(
            f"me failed: {response.status_code} {response.text[:300]}"
        )
    return response.json()


def validate_token(access_token: str) -> Optional[Dict[str, Any]]:
    """Call a minimal endpoint to check whether a token is still valid.

    Returns ``None`` if the token is invalid, otherwise the user info dict.
    """
    try:
        return get_user_info(access_token)
    except MetaAPIError:
        return None
