"""Unit tests for scripts/token_validator.py.

Only the pure logic (parse_iso helper, validate() function with mocked auth)
is covered. CLI argument parsing gets a smoke test.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest
from freezegun import freeze_time

from lib.ppc_auth import PPCAuth, AuthError
from lib.vault import PPCVault, VaultFileNotFoundError
from token_validator import _parse_iso, validate


class TestParseIso:
    def test_with_z(self):
        assert _parse_iso("2026-04-11T10:00:00Z") == datetime(
            2026, 4, 11, 10, 0, 0, tzinfo=timezone.utc
        )

    def test_none(self):
        assert _parse_iso(None) is None
        assert _parse_iso("") is None


class TestValidate:
    def test_missing_vault(self, tmp_vault_path, passphrase):
        vault = PPCVault(tmp_vault_path, passphrase)
        auth = PPCAuth(vault)
        results = validate(auth)
        assert len(results) == 1
        assert results[0]["platform"] == "vault"
        assert results[0]["status"] == "missing"

    def test_empty_vault(self, tmp_vault_path, passphrase):
        vault = PPCVault(tmp_vault_path, passphrase)
        vault.init_empty()
        auth = PPCAuth(vault)
        results = validate(auth)
        assert len(results) == 1
        assert results[0]["status"] == "empty"

    @freeze_time("2026-04-11 00:00:00")
    def test_happy_path(
        self, monkeypatch, tmp_vault_path, passphrase, sample_vault_data
    ):
        vault = PPCVault(tmp_vault_path, passphrase)
        vault.save(sample_vault_data)
        monkeypatch.setenv("CLAUDE_PLUGIN_OPTION_GOOGLE_ADS_DEVELOPER_TOKEN", "abc")
        auth = PPCAuth(vault)

        with patch.object(auth, "get_google_credentials") as mock_creds:
            mock_creds.return_value = MagicMock()
            results = validate(auth)

        statuses = {(r["platform"], r.get("account")): r["status"] for r in results}
        assert statuses[("google", "default")] == "ok"
        assert statuses[("google_ads", "acme")] == "ok"
        assert statuses[("meta", "default")] == "ok"

    @freeze_time("2026-06-06 00:00:00")  # 4 days before Meta expiry
    def test_meta_expiring_soon(
        self, monkeypatch, tmp_vault_path, passphrase, sample_vault_data
    ):
        vault = PPCVault(tmp_vault_path, passphrase)
        vault.save(sample_vault_data)
        monkeypatch.setenv("CLAUDE_PLUGIN_OPTION_GOOGLE_ADS_DEVELOPER_TOKEN", "abc")
        auth = PPCAuth(vault)
        with patch.object(auth, "get_google_credentials") as mock_creds:
            mock_creds.return_value = MagicMock()
            results = validate(auth)
        meta = [r for r in results if r["platform"] == "meta"][0]
        assert meta["status"] == "expiring_soon"

    @freeze_time("2026-07-11 00:00:00")  # 1 month after Meta expiry
    def test_meta_expired(
        self, monkeypatch, tmp_vault_path, passphrase, sample_vault_data
    ):
        vault = PPCVault(tmp_vault_path, passphrase)
        vault.save(sample_vault_data)
        monkeypatch.setenv("CLAUDE_PLUGIN_OPTION_GOOGLE_ADS_DEVELOPER_TOKEN", "abc")
        auth = PPCAuth(vault)
        with patch.object(auth, "get_google_credentials") as mock_creds:
            mock_creds.return_value = MagicMock()
            results = validate(auth)
        meta = [r for r in results if r["platform"] == "meta"][0]
        assert meta["status"] == "expired"

    def test_google_ads_missing_developer_token(
        self, monkeypatch, tmp_vault_path, passphrase, sample_vault_data
    ):
        monkeypatch.delenv("GOOGLE_ADS_DEVELOPER_TOKEN", raising=False)
        monkeypatch.delenv("CLAUDE_PLUGIN_OPTION_GOOGLE_ADS_DEVELOPER_TOKEN", raising=False)
        vault = PPCVault(tmp_vault_path, passphrase)
        vault.save(sample_vault_data)
        auth = PPCAuth(vault)
        with patch.object(auth, "get_google_credentials") as mock_creds:
            mock_creds.return_value = MagicMock()
            results = validate(auth)
        ads = [r for r in results if r["platform"] == "google_ads"][0]
        assert ads["status"] == "failed"
        assert "developer" in ads["detail"].lower()
