"""Unit tests for scripts/lib/vault.py."""

from __future__ import annotations

import json

import pytest

from lib.vault import (
    PPCVault,
    VaultDecryptError,
    VaultFileNotFoundError,
    _derive_key,
    _empty_vault,
)


class TestDeriveKey:
    def test_deterministic(self, passphrase):
        assert _derive_key(passphrase) == _derive_key(passphrase)

    def test_different_passphrases_different_keys(self):
        assert _derive_key("one") != _derive_key("two")

    def test_empty_passphrase_raises(self):
        from lib.vault import VaultError

        with pytest.raises(VaultError):
            _derive_key("")


class TestEmptyVault:
    def test_shape(self):
        data = _empty_vault()
        assert data["version"] == 1
        assert "google" in data and "accounts" in data["google"]
        assert "google_ads" in data and "accounts" in data["google_ads"]
        assert "meta" in data and "accounts" in data["meta"]
        assert "updated_at" in data


class TestPPCVault:
    def test_round_trip(self, tmp_vault_path, passphrase, sample_vault_data):
        vault = PPCVault(tmp_vault_path, passphrase)
        vault.save(sample_vault_data)
        assert tmp_vault_path.exists()

        # fresh instance, same passphrase
        vault2 = PPCVault(tmp_vault_path, passphrase)
        loaded = vault2.load()
        assert loaded["google"]["accounts"]["default"]["email"] == "john@anthril.com"
        assert loaded["google_ads"]["accounts"]["acme"]["customer_id"] == "1234567890"

    def test_wrong_passphrase_raises(self, tmp_vault_path, passphrase, sample_vault_data):
        PPCVault(tmp_vault_path, passphrase).save(sample_vault_data)
        bad = PPCVault(tmp_vault_path, "not the right one")
        with pytest.raises(VaultDecryptError):
            bad.load()

    def test_missing_file_raises(self, tmp_vault_path, passphrase):
        vault = PPCVault(tmp_vault_path, passphrase)
        with pytest.raises(VaultFileNotFoundError):
            vault.load()

    def test_init_empty_creates_file(self, tmp_vault_path, passphrase):
        vault = PPCVault(tmp_vault_path, passphrase)
        data = vault.init_empty()
        assert tmp_vault_path.exists()
        assert data["version"] == 1
        # Decrypt via a fresh instance to prove it persisted correctly
        assert PPCVault(tmp_vault_path, passphrase).load()["version"] == 1

    def test_cache_hit(self, tmp_vault_path, passphrase, sample_vault_data):
        vault = PPCVault(tmp_vault_path, passphrase)
        vault.save(sample_vault_data)
        first = vault.load()
        # Corrupt the file on disk; cache should still return the stale object.
        tmp_vault_path.write_bytes(b"garbage")
        assert vault.load() is first

    def test_cache_force_refresh(self, tmp_vault_path, passphrase, sample_vault_data):
        vault = PPCVault(tmp_vault_path, passphrase)
        vault.save(sample_vault_data)
        vault.load()
        tmp_vault_path.write_bytes(b"garbage")
        with pytest.raises(VaultDecryptError):
            vault.load(force=True)

    def test_save_updates_updated_at(self, tmp_vault_path, passphrase, sample_vault_data):
        vault = PPCVault(tmp_vault_path, passphrase)
        data = dict(sample_vault_data)
        data["updated_at"] = "1999-01-01T00:00:00+00:00"
        vault.save(data)
        reloaded = PPCVault(tmp_vault_path, passphrase).load()
        assert reloaded["updated_at"] != "1999-01-01T00:00:00+00:00"

    def test_atomic_write_no_temp_leftover(
        self, tmp_vault_path, passphrase, sample_vault_data
    ):
        vault = PPCVault(tmp_vault_path, passphrase)
        vault.save(sample_vault_data)
        # No .tmp files should be left behind
        leftover = list(tmp_vault_path.parent.glob(".tokens.*.enc.tmp"))
        assert not leftover

    def test_update_google_account_upserts(
        self, tmp_vault_path, passphrase, sample_vault_data
    ):
        vault = PPCVault(tmp_vault_path, passphrase)
        vault.save(sample_vault_data)
        new_acct = {"label": "client-b", "email": "b@example.com"}
        vault.update_google_account("client-b", new_acct)

        reloaded = PPCVault(tmp_vault_path, passphrase).load()
        assert "default" in reloaded["google"]["accounts"]
        assert reloaded["google"]["accounts"]["client-b"]["email"] == "b@example.com"

    def test_update_meta_account_upserts(
        self, tmp_vault_path, passphrase, sample_vault_data
    ):
        vault = PPCVault(tmp_vault_path, passphrase)
        vault.save(sample_vault_data)
        vault.update_meta_account("agency", {"label": "agency", "user_name": "Agency X"})
        reloaded = PPCVault(tmp_vault_path, passphrase).load()
        assert reloaded["meta"]["accounts"]["agency"]["user_name"] == "Agency X"

    def test_update_google_ads_account_upserts(
        self, tmp_vault_path, passphrase, sample_vault_data
    ):
        vault = PPCVault(tmp_vault_path, passphrase)
        vault.save(sample_vault_data)
        vault.update_google_ads_account(
            "second", {"label": "second", "customer_id": "0000000001"}
        )
        reloaded = PPCVault(tmp_vault_path, passphrase).load()
        assert reloaded["google_ads"]["accounts"]["second"]["customer_id"] == "0000000001"

    def test_save_creates_parent_dir(self, tmp_path, passphrase, sample_vault_data):
        nested = tmp_path / "deep" / "nested" / "tokens.enc"
        PPCVault(nested, passphrase).save(sample_vault_data)
        assert nested.exists()
