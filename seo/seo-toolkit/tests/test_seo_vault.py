"""Minimal pytest suite for seo_vault — roundtrip and removal tests.

These tests exercise the full encrypt/decrypt cycle and the remove_provider
helper using a temporary vault file so no real vault is touched.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Add scripts/ to import path so lib.seo_vault is importable without install
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from lib.seo_vault import (
    derive_key,
    get_secret,
    read_vault,
    remove_provider,
    set_secret,
    write_vault,
)

_TEST_PASSPHRASE = "test-passphrase-do-not-use-in-prod"


# ---------------------------------------------------------------------------
# Test: roundtrip — set a secret and read it back
# ---------------------------------------------------------------------------


def test_roundtrip(tmp_path: Path) -> None:
    """set_secret followed by get_secret returns the original value."""
    vault_file = tmp_path / "tokens.enc"

    set_secret("serpapi", "api_key", "sk-test-1234", _TEST_PASSPHRASE, vault_path=vault_file)

    retrieved = get_secret("serpapi", "api_key", _TEST_PASSPHRASE, vault_path=vault_file)
    assert retrieved == "sk-test-1234"


def test_roundtrip_multiple_fields(tmp_path: Path) -> None:
    """Multiple fields for a single provider are stored and retrieved independently."""
    vault_file = tmp_path / "tokens.enc"

    set_secret("dataforseo", "login", "user@example.com", _TEST_PASSPHRASE, vault_path=vault_file)
    set_secret(
        "dataforseo", "password", "s3cret-pass", _TEST_PASSPHRASE, vault_path=vault_file
    )

    assert (
        get_secret("dataforseo", "login", _TEST_PASSPHRASE, vault_path=vault_file)
        == "user@example.com"
    )
    assert (
        get_secret("dataforseo", "password", _TEST_PASSPHRASE, vault_path=vault_file)
        == "s3cret-pass"
    )


def test_missing_key_returns_none(tmp_path: Path) -> None:
    """get_secret returns None for a key that was never set."""
    vault_file = tmp_path / "tokens.enc"

    set_secret("serpapi", "api_key", "sk-abc", _TEST_PASSPHRASE, vault_path=vault_file)

    result = get_secret("serpapi", "nonexistent_key", _TEST_PASSPHRASE, vault_path=vault_file)
    assert result is None


def test_missing_provider_returns_none(tmp_path: Path) -> None:
    """get_secret returns None when the provider has never been written."""
    vault_file = tmp_path / "tokens.enc"

    # Vault does not exist yet
    result = get_secret("ahrefs", "api_key", _TEST_PASSPHRASE, vault_path=vault_file)
    assert result is None


# ---------------------------------------------------------------------------
# Test: remove_provider — set then remove, verify gone
# ---------------------------------------------------------------------------


def test_remove_provider(tmp_path: Path) -> None:
    """remove_provider deletes all credentials for a provider."""
    vault_file = tmp_path / "tokens.enc"

    set_secret("moz", "access_id", "mozid-123", _TEST_PASSPHRASE, vault_path=vault_file)
    set_secret("moz", "secret", "mozsecret-456", _TEST_PASSPHRASE, vault_path=vault_file)

    # Confirm they're there
    assert get_secret("moz", "access_id", _TEST_PASSPHRASE, vault_path=vault_file) == "mozid-123"

    remove_provider("moz", _TEST_PASSPHRASE, vault_path=vault_file)

    # Both keys should be gone
    assert get_secret("moz", "access_id", _TEST_PASSPHRASE, vault_path=vault_file) is None
    assert get_secret("moz", "secret", _TEST_PASSPHRASE, vault_path=vault_file) is None


def test_remove_provider_does_not_affect_others(tmp_path: Path) -> None:
    """Removing one provider leaves other providers intact."""
    vault_file = tmp_path / "tokens.enc"

    set_secret("serpapi", "api_key", "serp-key", _TEST_PASSPHRASE, vault_path=vault_file)
    set_secret("ahrefs", "api_key", "ahrefs-key", _TEST_PASSPHRASE, vault_path=vault_file)

    remove_provider("serpapi", _TEST_PASSPHRASE, vault_path=vault_file)

    assert get_secret("serpapi", "api_key", _TEST_PASSPHRASE, vault_path=vault_file) is None
    assert (
        get_secret("ahrefs", "api_key", _TEST_PASSPHRASE, vault_path=vault_file) == "ahrefs-key"
    )


def test_remove_nonexistent_provider_raises(tmp_path: Path) -> None:
    """remove_provider raises KeyError when the provider does not exist."""
    vault_file = tmp_path / "tokens.enc"

    # Create a vault with one provider
    set_secret("serpapi", "api_key", "sk", _TEST_PASSPHRASE, vault_path=vault_file)

    with pytest.raises(KeyError, match="ahrefs"):
        remove_provider("ahrefs", _TEST_PASSPHRASE, vault_path=vault_file)


# ---------------------------------------------------------------------------
# Test: wrong passphrase raises ValueError
# ---------------------------------------------------------------------------


def test_wrong_passphrase_raises(tmp_path: Path) -> None:
    """Reading the vault with the wrong passphrase raises ValueError."""
    vault_file = tmp_path / "tokens.enc"

    set_secret("psi", "api_key", "psi-key", _TEST_PASSPHRASE, vault_path=vault_file)

    with pytest.raises(ValueError, match="decrypt"):
        read_vault("wrong-passphrase", vault_path=vault_file)


# ---------------------------------------------------------------------------
# Test: vault metadata
# ---------------------------------------------------------------------------


def test_vault_has_version_and_updated_at(tmp_path: Path) -> None:
    """Written vault contains version and updated_at metadata fields."""
    vault_file = tmp_path / "tokens.enc"

    set_secret("serpapi", "api_key", "key", _TEST_PASSPHRASE, vault_path=vault_file)

    data = read_vault(_TEST_PASSPHRASE, vault_path=vault_file)
    assert data["version"] == 1
    assert "updated_at" in data
    assert data["updated_at"]  # not empty
