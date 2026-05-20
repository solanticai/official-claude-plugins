"""Single source of truth for ppc-manager authentication.

Every MCP server (``ppc-gtm``, ``ppc-ga4``, ``ppc-google-ads``, ``ppc-meta``)
and every standalone script imports from this module. It wraps the vault with
typed helpers that:

- Return live, just-in-time-refreshed ``google.oauth2.credentials.Credentials``
  objects.
- Build configured Google Ads clients.
- Return live Meta access tokens, re-exchanging long-lived tokens when they
  are within 5 days of expiry.
- Produce ready-to-use ``googleapiclient.discovery`` handles for GTM and GA4
  admin.

Refresh writes go back through the vault under a file lock (see
``vault.py``). Tokens never leak to stdout or to the transcript — see
``masking_logger.py``.

The public surface is the ``PPCAuth`` class; every helper is a method on it.
Do not add module-level state.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from .masking_logger import get_logger
from .vault import PPCVault, VaultError, VaultFileNotFoundError

logger = get_logger(__name__)

VAULT_VERSION = 1

# Combined scope list for a single Google OAuth consent that covers GTM, GA4,
# and Google Ads. Keep this list sorted and in sync with oauth_google.py +
# skills/oauth-setup/reference.md.
GOOGLE_SCOPES_ALL = [
    "https://www.googleapis.com/auth/adwords",
    "https://www.googleapis.com/auth/analytics.edit",
    "https://www.googleapis.com/auth/analytics.readonly",
    "https://www.googleapis.com/auth/tagmanager.edit.containers",
    "https://www.googleapis.com/auth/tagmanager.readonly",
]

META_SCOPES = [
    "ads_management",
    "ads_read",
    "business_management",
    "pages_read_engagement",
    "pages_manage_metadata",
]

# Refresh buffers — refresh "slightly early" to avoid racing the actual expiry.
GOOGLE_ACCESS_TOKEN_BUFFER_SECONDS = 60
META_TOKEN_REEXCHANGE_DAYS = 5


class AuthError(Exception):
    """Raised when auth lookup or refresh fails for an application reason."""


class PPCAuth:
    """Facade over the encrypted vault providing typed credential accessors.

    Typical usage in an MCP server::

        auth = PPCAuth.from_env()
        creds = auth.get_google_credentials("default")
        service = auth.get_gtm_service("default")
    """

    def __init__(self, vault: PPCVault):
        self.vault = vault

    @classmethod
    def from_env(cls) -> "PPCAuth":
        """Build a ``PPCAuth`` from ``PPC_VAULT_PATH`` and ``PPC_VAULT_PASSPHRASE``.

        Both environment variables are injected by the MCP server registration
        in ``.mcp.json`` via ``${user_config.ppc_vault_passphrase}``.
        """
        path = os.environ.get("PPC_VAULT_PATH")
        passphrase = os.environ.get("PPC_VAULT_PASSPHRASE")
        if not path:
            raise AuthError("PPC_VAULT_PATH environment variable is not set")
        if not passphrase:
            raise AuthError("PPC_VAULT_PASSPHRASE environment variable is not set")
        return cls(PPCVault(path, passphrase))

    # ------------------------------------------------------------------
    # Generic vault navigation
    # ------------------------------------------------------------------

    def _require_vault(self) -> Dict[str, Any]:
        try:
            return self.vault.load()
        except VaultFileNotFoundError as exc:
            raise AuthError(
                "Credential vault not found. Run /ppc-manager:oauth-setup first."
            ) from exc
        except VaultError as exc:
            raise AuthError(str(exc)) from exc

    def _get_google_account(self, label: str) -> Dict[str, Any]:
        data = self._require_vault()
        account = data.get("google", {}).get("accounts", {}).get(label)
        if not account:
            raise AuthError(
                f"No Google account '{label}' in vault. "
                "Run /ppc-manager:oauth-setup to add it."
            )
        return account

    def _get_google_client_secret(self) -> Optional[str]:
        data = self._require_vault()
        return data.get("google", {}).get("client_secret")

    def _get_meta_account(self, label: str) -> Dict[str, Any]:
        data = self._require_vault()
        account = data.get("meta", {}).get("accounts", {}).get(label)
        if not account:
            raise AuthError(
                f"No Meta account '{label}' in vault. "
                "Run /ppc-manager:oauth-setup to add it."
            )
        return account

    def _get_google_ads_account(self, label: str) -> Dict[str, Any]:
        data = self._require_vault()
        account = data.get("google_ads", {}).get("accounts", {}).get(label)
        if not account:
            raise AuthError(
                f"No Google Ads account '{label}' in vault. "
                "Run /ppc-manager:oauth-setup to add it."
            )
        return account

    # ------------------------------------------------------------------
    # Google (GTM, GA4, Google Ads share one refresh token)
    # ------------------------------------------------------------------

    def get_google_credentials(self, account: str = "default"):
        """Return live ``google.oauth2.credentials.Credentials``.

        If the cached access token is within ``GOOGLE_ACCESS_TOKEN_BUFFER_SECONDS``
        of expiry, refresh it via the refresh token, write the new access token
        back to the vault, and return the updated object.
        """
        # Imported here so the module stays importable without the Google libs
        # present (e.g. during vault unit tests).
        from google.oauth2.credentials import Credentials as GoogleCredentials
        from google.auth.transport.requests import Request

        entry = self._get_google_account(account)
        client_secret = self._get_google_client_secret()
        client_id = entry.get("client_id")
        if not client_secret or not client_id:
            raise AuthError(
                "Google client_id/client_secret missing from vault. "
                "Run /ppc-manager:oauth-setup to reconnect."
            )

        refresh_token = entry.get("refresh_token")
        if not refresh_token:
            raise AuthError(
                f"Google account '{account}' has no refresh token. "
                "Re-run /ppc-manager:oauth-setup."
            )

        expires_at = _parse_iso(entry.get("access_token_expires_at"))
        now = datetime.now(timezone.utc)
        needs_refresh = (
            expires_at is None
            or expires_at <= now + timedelta(seconds=GOOGLE_ACCESS_TOKEN_BUFFER_SECONDS)
        )

        creds = GoogleCredentials(
            token=entry.get("access_token"),
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret,
            scopes=entry.get("scopes") or GOOGLE_SCOPES_ALL,
        )

        if needs_refresh or not entry.get("access_token"):
            logger.info("Refreshing Google access token for account '%s'", account)
            creds.refresh(Request())
            self._write_google_refresh(account, creds)

        return creds

    def _write_google_refresh(self, account: str, creds) -> None:
        """Persist a refreshed access token back to the vault."""
        data = self.vault.load()
        entry = data["google"]["accounts"][account]
        entry["access_token"] = creds.token
        expiry = getattr(creds, "expiry", None)
        if expiry is not None:
            if expiry.tzinfo is None:
                # google-auth returns naive UTC; make it explicit.
                expiry = expiry.replace(tzinfo=timezone.utc)
            entry["access_token_expires_at"] = expiry.isoformat()
        self.vault.save(data)

    def get_gtm_service(self, account: str = "default"):
        """Return a ``googleapiclient.discovery.Resource`` for Tag Manager v2."""
        from googleapiclient.discovery import build

        creds = self.get_google_credentials(account)
        return build("tagmanager", "v2", credentials=creds, cache_discovery=False)

    def get_ga4_admin_client(self, account: str = "default"):
        """Return a ``google.analytics.admin_v1beta.AnalyticsAdminServiceClient``."""
        from google.analytics.admin_v1beta import AnalyticsAdminServiceClient

        creds = self.get_google_credentials(account)
        return AnalyticsAdminServiceClient(credentials=creds)

    def get_ga4_data_client(self, account: str = "default"):
        """Return a ``google.analytics.data_v1beta.BetaAnalyticsDataClient``."""
        from google.analytics.data_v1beta import BetaAnalyticsDataClient

        creds = self.get_google_credentials(account)
        return BetaAnalyticsDataClient(credentials=creds)

    def get_google_ads_client(self, account_label: str = "default"):
        """Return a configured ``google.ads.googleads.client.GoogleAdsClient``.

        ``account_label`` is a Google Ads account label (e.g. 'acme_ltd'). The
        label maps to a linked Google account in the vault and to an optional
        MCC login_customer_id.
        """
        from google.ads.googleads.client import GoogleAdsClient

        ads_entry = self._get_google_ads_account(account_label)
        linked_google = ads_entry.get("linked_google_account", "default")
        creds = self.get_google_credentials(linked_google)
        client_secret = self._get_google_client_secret()
        developer_token = os.environ.get("GOOGLE_ADS_DEVELOPER_TOKEN") or os.environ.get(
            "CLAUDE_PLUGIN_OPTION_GOOGLE_ADS_DEVELOPER_TOKEN"
        )
        if not developer_token:
            raise AuthError(
                "Google Ads developer token not configured. "
                "Set it via the ppc-manager userConfig or re-run /ppc-manager:oauth-setup."
            )

        config = {
            "developer_token": developer_token,
            "client_id": creds.client_id,
            "client_secret": client_secret,
            "refresh_token": creds.refresh_token,
            "use_proto_plus": True,
        }
        login_customer_id = ads_entry.get("login_customer_id")
        if login_customer_id:
            config["login_customer_id"] = str(login_customer_id).replace("-", "")
        return GoogleAdsClient.load_from_dict(config)

    # ------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------

    def get_meta_access_token(self, account: str = "default") -> str:
        """Return a live Meta long-lived access token.

        If the token is within ``META_TOKEN_REEXCHANGE_DAYS`` of expiry, hit
        ``/oauth/access_token?grant_type=fb_exchange_token`` to extend it,
        write the new token back to the vault, and return the new value.

        Note: Meta long-lived tokens are re-exchangeable but not permanently
        refreshable. If the existing token has already expired, the user must
        re-run ``/ppc-manager:oauth-setup``.
        """
        import httpx

        entry = self._get_meta_account(account)
        token = entry.get("long_lived_user_token")
        if not token:
            raise AuthError(
                f"Meta account '{account}' has no long-lived token. "
                "Run /ppc-manager:oauth-setup to connect."
            )

        expires_at = _parse_iso(entry.get("long_lived_user_token_expires_at"))
        now = datetime.now(timezone.utc)
        if expires_at is not None and expires_at <= now:
            raise AuthError(
                f"Meta token for account '{account}' expired on {expires_at.isoformat()}. "
                "Re-run /ppc-manager:oauth-setup."
            )
        if expires_at is None or expires_at - now > timedelta(days=META_TOKEN_REEXCHANGE_DAYS):
            return token

        logger.info("Re-exchanging Meta long-lived token for account '%s'", account)
        app_id = os.environ.get("CLAUDE_PLUGIN_OPTION_META_APP_ID")
        app_secret = os.environ.get("CLAUDE_PLUGIN_OPTION_META_APP_SECRET")
        if not app_id or not app_secret:
            data = self.vault.load()
            app_secret = data.get("meta", {}).get("app_secret") or app_secret
        if not app_id or not app_secret:
            raise AuthError(
                "Cannot re-exchange Meta token — app_id/app_secret not configured."
            )

        response = httpx.get(
            "https://graph.facebook.com/v22.0/oauth/access_token",
            params={
                "grant_type": "fb_exchange_token",
                "client_id": app_id,
                "client_secret": app_secret,
                "fb_exchange_token": token,
            },
            timeout=20.0,
        )
        if response.status_code != 200:
            raise AuthError(
                f"Meta token re-exchange failed: {response.status_code} {response.text[:200]}"
            )
        payload = response.json()
        new_token = payload.get("access_token")
        if not new_token:
            raise AuthError(f"Meta re-exchange returned no access_token: {payload}")
        expires_in = int(payload.get("expires_in", 60 * 24 * 3600))
        new_expiry = (now + timedelta(seconds=expires_in)).isoformat()

        data = self.vault.load()
        data["meta"]["accounts"][account]["long_lived_user_token"] = new_token
        data["meta"]["accounts"][account]["long_lived_user_token_expires_at"] = new_expiry
        self.vault.save(data)
        return new_token

    def get_meta_api_init(self, account: str = "default"):
        """Return a ``FacebookAdsApi`` instance initialised with the long-lived token."""
        from facebook_business.api import FacebookAdsApi

        token = self.get_meta_access_token(account)
        app_id = os.environ.get("CLAUDE_PLUGIN_OPTION_META_APP_ID", "")
        app_secret = (
            os.environ.get("CLAUDE_PLUGIN_OPTION_META_APP_SECRET")
            or (self.vault.load().get("meta", {}) or {}).get("app_secret", "")
        )
        return FacebookAdsApi.init(
            app_id=app_id,
            app_secret=app_secret,
            access_token=token,
            api_version="v22.0",
        )


# ---------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------


def _parse_iso(value: Optional[str]) -> Optional[datetime]:
    """Parse an ISO-8601 timestamp, tolerating a trailing 'Z' and missing tz."""
    if not value:
        return None
    try:
        if value.endswith("Z"):
            value = value[:-1] + "+00:00"
        dt = datetime.fromisoformat(value)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt
