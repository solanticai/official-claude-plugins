"""Unit tests for scripts/lib/ppc_auth.py.

The Google/Meta SDK calls are fully mocked — these tests verify the vault
plumbing and decision logic, not live network behaviour.
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest
from freezegun import freeze_time

from lib.ppc_auth import (
    GOOGLE_SCOPES_ALL,
    META_SCOPES,
    AuthError,
    PPCAuth,
    _parse_iso,
)
from lib.vault import PPCVault


class TestParseIso:
    def test_with_z(self):
        dt = _parse_iso("2026-04-11T10:00:00Z")
        assert dt == datetime(2026, 4, 11, 10, 0, 0, tzinfo=timezone.utc)

    def test_with_offset(self):
        dt = _parse_iso("2026-04-11T10:00:00+10:00")
        assert dt is not None
        assert dt.tzinfo is not None

    def test_naive_gets_utc_tz(self):
        dt = _parse_iso("2026-04-11T10:00:00")
        assert dt is not None
        assert dt.tzinfo == timezone.utc

    def test_none_returns_none(self):
        assert _parse_iso(None) is None
        assert _parse_iso("") is None

    def test_invalid_returns_none(self):
        assert _parse_iso("not-a-date") is None


class TestScopes:
    def test_google_scopes_include_everything(self):
        assert "https://www.googleapis.com/auth/adwords" in GOOGLE_SCOPES_ALL
        assert any("tagmanager" in s for s in GOOGLE_SCOPES_ALL)
        assert any("analytics" in s for s in GOOGLE_SCOPES_ALL)

    def test_meta_scopes(self):
        assert "ads_management" in META_SCOPES
        assert "ads_read" in META_SCOPES


class TestFromEnv:
    def test_missing_path_raises(self, monkeypatch):
        monkeypatch.delenv("PPC_VAULT_PATH", raising=False)
        monkeypatch.setenv("PPC_VAULT_PASSPHRASE", "x")
        with pytest.raises(AuthError):
            PPCAuth.from_env()

    def test_missing_passphrase_raises(self, monkeypatch):
        monkeypatch.setenv("PPC_VAULT_PATH", "/tmp/x")
        monkeypatch.delenv("PPC_VAULT_PASSPHRASE", raising=False)
        with pytest.raises(AuthError):
            PPCAuth.from_env()

    def test_happy_path(self, monkeypatch, tmp_vault_path):
        monkeypatch.setenv("PPC_VAULT_PATH", str(tmp_vault_path))
        monkeypatch.setenv("PPC_VAULT_PASSPHRASE", "x")
        auth = PPCAuth.from_env()
        assert auth.vault.path == tmp_vault_path


class TestRequireVault:
    def test_missing_vault_raises_authfile_error(self, tmp_vault_path, passphrase):
        vault = PPCVault(tmp_vault_path, passphrase)
        auth = PPCAuth(vault)
        with pytest.raises(AuthError, match="oauth-setup"):
            auth._require_vault()


class TestGoogleAccountLookup:
    def test_missing_account_raises(
        self, tmp_vault_path, passphrase, sample_vault_data
    ):
        vault = PPCVault(tmp_vault_path, passphrase)
        vault.save(sample_vault_data)
        auth = PPCAuth(vault)
        with pytest.raises(AuthError, match="No Google account 'missing'"):
            auth._get_google_account("missing")

    def test_present_account(self, tmp_vault_path, passphrase, sample_vault_data):
        vault = PPCVault(tmp_vault_path, passphrase)
        vault.save(sample_vault_data)
        auth = PPCAuth(vault)
        account = auth._get_google_account("default")
        assert account["email"] == "john@anthril.com"


class TestGetGoogleCredentials:
    @patch("google.auth.transport.requests.Request")
    @patch("google.oauth2.credentials.Credentials")
    def test_refresh_when_expired(
        self,
        mock_creds_cls,
        mock_request,
        tmp_vault_path,
        passphrase,
        sample_vault_data,
    ):
        # Set access token expiry to far in the past
        sample_vault_data["google"]["accounts"]["default"][
            "access_token_expires_at"
        ] = "2000-01-01T00:00:00+00:00"
        vault = PPCVault(tmp_vault_path, passphrase)
        vault.save(sample_vault_data)

        mock_instance = MagicMock()
        mock_instance.token = "ya29.new-access-token"
        mock_instance.expiry = datetime(2030, 1, 1, tzinfo=timezone.utc)
        mock_creds_cls.return_value = mock_instance

        auth = PPCAuth(vault)
        result = auth.get_google_credentials("default")

        mock_instance.refresh.assert_called_once()
        assert result is mock_instance
        # Vault should contain the new token
        reloaded = PPCVault(tmp_vault_path, passphrase).load()
        assert (
            reloaded["google"]["accounts"]["default"]["access_token"]
            == "ya29.new-access-token"
        )

    @patch("google.auth.transport.requests.Request")
    @patch("google.oauth2.credentials.Credentials")
    @freeze_time("2026-04-11 10:00:00")
    def test_no_refresh_when_fresh(
        self,
        mock_creds_cls,
        mock_request,
        tmp_vault_path,
        passphrase,
        sample_vault_data,
    ):
        # Set expiry 2 hours in the future — no refresh needed
        sample_vault_data["google"]["accounts"]["default"][
            "access_token_expires_at"
        ] = "2026-04-11T12:00:00+00:00"
        vault = PPCVault(tmp_vault_path, passphrase)
        vault.save(sample_vault_data)

        mock_instance = MagicMock()
        mock_creds_cls.return_value = mock_instance

        auth = PPCAuth(vault)
        auth.get_google_credentials("default")
        mock_instance.refresh.assert_not_called()

    def test_missing_refresh_token_raises(
        self, tmp_vault_path, passphrase, sample_vault_data
    ):
        sample_vault_data["google"]["accounts"]["default"]["refresh_token"] = None
        vault = PPCVault(tmp_vault_path, passphrase)
        vault.save(sample_vault_data)
        auth = PPCAuth(vault)
        with pytest.raises(AuthError, match="no refresh token"):
            auth.get_google_credentials("default")


class TestGetMetaAccessToken:
    def test_missing_account_raises(
        self, tmp_vault_path, passphrase, sample_vault_data
    ):
        vault = PPCVault(tmp_vault_path, passphrase)
        vault.save(sample_vault_data)
        auth = PPCAuth(vault)
        with pytest.raises(AuthError, match="No Meta account 'missing'"):
            auth.get_meta_access_token("missing")

    @freeze_time("2026-04-11 00:00:00")
    def test_fresh_token_returned_as_is(
        self, tmp_vault_path, passphrase, sample_vault_data
    ):
        vault = PPCVault(tmp_vault_path, passphrase)
        vault.save(sample_vault_data)
        auth = PPCAuth(vault)
        token = auth.get_meta_access_token("default")
        assert token == "EAABtest-long-token"

    @freeze_time("2026-06-11 00:00:00")
    def test_expired_token_raises(
        self, tmp_vault_path, passphrase, sample_vault_data
    ):
        vault = PPCVault(tmp_vault_path, passphrase)
        vault.save(sample_vault_data)
        auth = PPCAuth(vault)
        with pytest.raises(AuthError, match="expired"):
            auth.get_meta_access_token("default")

    @freeze_time("2026-06-08 00:00:00")
    @patch("httpx.get")
    def test_near_expiry_reexchanges(
        self, mock_httpx, monkeypatch, tmp_vault_path, passphrase, sample_vault_data
    ):
        vault = PPCVault(tmp_vault_path, passphrase)
        vault.save(sample_vault_data)
        monkeypatch.setenv("CLAUDE_PLUGIN_OPTION_META_APP_ID", "111")
        monkeypatch.setenv("CLAUDE_PLUGIN_OPTION_META_APP_SECRET", "secret")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "EAABnew-long-token",
            "expires_in": 60 * 24 * 3600,
        }
        mock_httpx.return_value = mock_response

        auth = PPCAuth(vault)
        token = auth.get_meta_access_token("default")
        assert token == "EAABnew-long-token"

        # Vault should be rewritten
        reloaded = PPCVault(tmp_vault_path, passphrase).load()
        assert (
            reloaded["meta"]["accounts"]["default"]["long_lived_user_token"]
            == "EAABnew-long-token"
        )


class TestGetGoogleAdsClient:
    def test_missing_account_raises(
        self, tmp_vault_path, passphrase, sample_vault_data
    ):
        vault = PPCVault(tmp_vault_path, passphrase)
        vault.save(sample_vault_data)
        auth = PPCAuth(vault)
        with pytest.raises(AuthError, match="No Google Ads account"):
            auth.get_google_ads_client("does-not-exist")

    def test_missing_developer_token_raises(
        self, monkeypatch, tmp_vault_path, passphrase, sample_vault_data
    ):
        monkeypatch.delenv("GOOGLE_ADS_DEVELOPER_TOKEN", raising=False)
        monkeypatch.delenv("CLAUDE_PLUGIN_OPTION_GOOGLE_ADS_DEVELOPER_TOKEN", raising=False)
        vault = PPCVault(tmp_vault_path, passphrase)
        vault.save(sample_vault_data)
        auth = PPCAuth(vault)

        with patch.object(auth, "get_google_credentials") as mock_creds:
            fake_creds = MagicMock()
            fake_creds.client_id = "123"
            fake_creds.refresh_token = "1//refresh"
            mock_creds.return_value = fake_creds
            with pytest.raises(AuthError, match="developer token"):
                auth.get_google_ads_client("acme")
