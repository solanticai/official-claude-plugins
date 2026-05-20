"""Integration tests for the full vault lifecycle.

No network, no real secrets. These tests exercise vault.py end-to-end:
fresh vault -> upsert account -> save -> load -> rotate -> save again.
"""

from __future__ import annotations

from lib.vault import PPCVault


def test_full_lifecycle(tmp_path, passphrase):
    path = tmp_path / "tokens.enc"
    vault = PPCVault(path, passphrase)

    # 1. Create an empty vault
    vault.init_empty()
    assert path.exists()
    data = vault.load()
    assert data["google"]["accounts"] == {}

    # 2. Add a Google account
    vault.update_google_account(
        "default",
        {
            "label": "default",
            "email": "john@anthril.com",
            "refresh_token": "1//0g-test",
            "access_token": "ya29.test",
            "scopes": ["https://www.googleapis.com/auth/adwords"],
        },
    )
    reloaded = PPCVault(path, passphrase).load()
    assert "default" in reloaded["google"]["accounts"]

    # 3. Add a Meta account
    vault.update_meta_account(
        "default",
        {
            "label": "default",
            "user_name": "Test User",
            "long_lived_user_token": "EAABtest",
        },
    )
    reloaded = PPCVault(path, passphrase).load()
    assert "default" in reloaded["meta"]["accounts"]

    # 4. Rotate the Google access token
    data = vault.load()
    data["google"]["accounts"]["default"]["access_token"] = "ya29.rotated"
    vault.save(data)
    reloaded = PPCVault(path, passphrase).load()
    assert (
        reloaded["google"]["accounts"]["default"]["access_token"] == "ya29.rotated"
    )

    # 5. Add a second account alongside
    vault.update_google_account(
        "client-b",
        {"label": "client-b", "refresh_token": "1//0g-b"},
    )
    reloaded = PPCVault(path, passphrase).load()
    assert set(reloaded["google"]["accounts"].keys()) == {"default", "client-b"}


def test_passphrase_change_requires_rewrite(tmp_path, sample_vault_data):
    path = tmp_path / "tokens.enc"
    PPCVault(path, "old-passphrase").save(sample_vault_data)

    # A wrong passphrase must not decrypt
    from lib.vault import VaultDecryptError
    import pytest

    with pytest.raises(VaultDecryptError):
        PPCVault(path, "new-passphrase").load()

    # Load with the old passphrase, rewrite with the new one
    data = PPCVault(path, "old-passphrase").load()
    PPCVault(path, "new-passphrase").save(data)
    # Old passphrase must now fail
    with pytest.raises(VaultDecryptError):
        PPCVault(path, "old-passphrase").load()
    # New passphrase works
    reloaded = PPCVault(path, "new-passphrase").load()
    assert reloaded["google"]["accounts"]["default"]["email"] == "john@anthril.com"
