"""Encrypted credential vault for seo-toolkit.

Single source of truth for all SEO provider credentials. Wraps a Fernet-
encrypted JSON file at ``${CLAUDE_PLUGIN_DATA}/tokens.enc`` with PBKDF2-HMAC-
SHA256 key derivation (100 000 iterations).

Writes are atomic (write to ``.tmp``, fsync, ``os.replace``) and serialised
via a ``filelock`` to handle concurrent script invocations.

On POSIX the vault file is ``chmod 0600`` after every write.

Public API::

    derive_key(passphrase, salt) -> bytes
    read_vault(passphrase) -> dict
    write_vault(data, passphrase) -> None
    set_secret(provider, key, value, passphrase) -> None
    get_secret(provider, key, passphrase) -> str | None
    remove_provider(provider, passphrase) -> None

CLI (for use from bash hooks)::

    python seo_vault.py set <provider> <key> <value> --passphrase PASS
    python seo_vault.py get <provider> <key> --passphrase PASS
    python seo_vault.py remove <provider> --passphrase PASS
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import platform
import stat
import sys
from pathlib import Path
from typing import Any

try:
    from cryptography.fernet import Fernet, InvalidToken
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
except ImportError as exc:  # pragma: no cover
    sys.exit(f"seo-toolkit: cryptography package not installed — {exc}")

try:
    from filelock import FileLock
except ImportError as exc:  # pragma: no cover
    sys.exit(f"seo-toolkit: filelock package not installed — {exc}")


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Salt is fixed per plugin identity — not a secret; its purpose is to
# domain-separate key derivation so the same passphrase cannot be reused
# trivially across different plugins.
_PBKDF2_SALT: bytes = b"seo-toolkit-v1-vault-salt-2026"
_PBKDF2_ITERATIONS: int = 100_000
_VAULT_VERSION: int = 1


def _default_vault_path() -> Path:
    """Return the default vault path, honouring SEO_VAULT_PATH env var."""
    env = os.environ.get("SEO_VAULT_PATH")
    if env:
        return Path(env)
    data_dir = os.environ.get(
        "CLAUDE_PLUGIN_DATA",
        os.path.join(os.path.expanduser("~"), ".claude", "plugins", "data", "seo-toolkit"),
    )
    return Path(data_dir) / "tokens.enc"


# ---------------------------------------------------------------------------
# Key derivation
# ---------------------------------------------------------------------------


def derive_key(passphrase: str, salt: bytes = _PBKDF2_SALT) -> bytes:
    """Derive a 32-byte Fernet key from *passphrase* using PBKDF2-HMAC-SHA256.

    Args:
        passphrase: The user-supplied vault passphrase.
        salt:       Domain-separation salt. Defaults to the plugin constant.

    Returns:
        URL-safe base64-encoded 32-byte key suitable for ``Fernet()``.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=_PBKDF2_ITERATIONS,
    )
    raw = kdf.derive(passphrase.encode("utf-8"))
    return base64.urlsafe_b64encode(raw)


# ---------------------------------------------------------------------------
# Low-level read / write
# ---------------------------------------------------------------------------


def read_vault(passphrase: str, vault_path: Path | None = None) -> dict[str, Any]:
    """Decrypt and deserialise the vault JSON.

    Args:
        passphrase: Vault passphrase.
        vault_path: Override the default vault path (useful in tests).

    Returns:
        Parsed vault dict.

    Raises:
        FileNotFoundError: Vault file does not exist.
        ValueError:        Decryption failed (wrong passphrase or corrupt file).
    """
    path = vault_path or _default_vault_path()
    if not path.exists():
        raise FileNotFoundError(f"Vault not found at {path}. Run /seo-toolkit:seo-connect first.")

    key = derive_key(passphrase)
    f = Fernet(key)
    try:
        ciphertext = path.read_bytes()
        plaintext = f.decrypt(ciphertext)
    except InvalidToken as exc:
        raise ValueError(
            "Failed to decrypt vault — wrong passphrase or the vault is corrupt."
        ) from exc

    return json.loads(plaintext.decode("utf-8"))


def write_vault(data: dict[str, Any], passphrase: str, vault_path: Path | None = None) -> None:
    """Serialise, encrypt, and atomically write *data* to the vault.

    Args:
        data:       Full vault dict (will have ``version`` and ``updated_at`` injected).
        passphrase: Vault passphrase.
        vault_path: Override the default vault path (useful in tests).
    """
    import datetime

    path = vault_path or _default_vault_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    data["version"] = _VAULT_VERSION
    data["updated_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()

    plaintext = json.dumps(data, indent=2).encode("utf-8")
    key = derive_key(passphrase)
    f = Fernet(key)
    ciphertext = f.encrypt(plaintext)

    lock_path = path.with_suffix(".lock")
    tmp_path = path.with_suffix(".tmp")

    with FileLock(str(lock_path), timeout=10):
        tmp_path.write_bytes(ciphertext)
        # fsync to ensure bytes hit storage before rename
        with open(tmp_path, "rb") as fh:
            os.fsync(fh.fileno())
        os.replace(tmp_path, path)
        # Restrict permissions on POSIX
        if platform.system() != "Windows":
            os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)


# ---------------------------------------------------------------------------
# High-level helpers
# ---------------------------------------------------------------------------


def set_secret(
    provider: str,
    key: str,
    value: str,
    passphrase: str,
    vault_path: Path | None = None,
) -> None:
    """Store *value* under ``vault[provider][key]``.

    Creates the vault if it does not exist yet.

    Args:
        provider:   Top-level provider key (e.g. ``"serpapi"``).
        key:        Field name within the provider (e.g. ``"api_key"``).
        value:      The secret value to store.
        passphrase: Vault passphrase.
        vault_path: Override for tests.
    """
    path = vault_path or _default_vault_path()
    try:
        data = read_vault(passphrase, vault_path=path)
    except FileNotFoundError:
        data = {}

    if provider not in data:
        data[provider] = {}
    data[provider][key] = value
    write_vault(data, passphrase, vault_path=path)


def get_secret(
    provider: str,
    key: str,
    passphrase: str,
    vault_path: Path | None = None,
) -> str | None:
    """Read ``vault[provider][key]``, returning ``None`` if absent.

    Args:
        provider:   Top-level provider key.
        key:        Field name.
        passphrase: Vault passphrase.
        vault_path: Override for tests.

    Returns:
        The stored string value, or ``None``.
    """
    path = vault_path or _default_vault_path()
    try:
        data = read_vault(passphrase, vault_path=path)
    except FileNotFoundError:
        return None
    return data.get(provider, {}).get(key)


def remove_provider(
    provider: str,
    passphrase: str,
    vault_path: Path | None = None,
) -> None:
    """Remove all credentials for *provider* from the vault.

    Args:
        provider:   Top-level provider key to remove.
        passphrase: Vault passphrase.
        vault_path: Override for tests.

    Raises:
        KeyError: Provider not found in vault.
    """
    path = vault_path or _default_vault_path()
    data = read_vault(passphrase, vault_path=path)
    if provider not in data:
        raise KeyError(f"Provider '{provider}' not found in vault.")
    del data[provider]
    write_vault(data, passphrase, vault_path=path)


# ---------------------------------------------------------------------------
# CLI entry point (called from bash hooks)
# ---------------------------------------------------------------------------


def _cli() -> None:
    parser = argparse.ArgumentParser(description="seo-toolkit vault CLI")
    parser.add_argument("--passphrase", required=True, help="Vault passphrase")
    parser.add_argument("--vault-path", help="Override vault file path")

    sub = parser.add_subparsers(dest="command", required=True)

    p_set = sub.add_parser("set", help="Store a secret")
    p_set.add_argument("provider")
    p_set.add_argument("key")
    p_set.add_argument("value")

    p_get = sub.add_parser("get", help="Read a secret")
    p_get.add_argument("provider")
    p_get.add_argument("key")

    p_remove = sub.add_parser("remove", help="Remove a provider")
    p_remove.add_argument("provider")

    args = parser.parse_args()
    vault_path = Path(args.vault_path) if getattr(args, "vault_path", None) else None

    if args.command == "set":
        set_secret(args.provider, args.key, args.value, args.passphrase, vault_path=vault_path)
        print(f"Stored {args.provider}.{args.key}")
    elif args.command == "get":
        value = get_secret(args.provider, args.key, args.passphrase, vault_path=vault_path)
        if value is None:
            print(f"Key not found: {args.provider}.{args.key}", file=sys.stderr)
            sys.exit(1)
        print(value)
    elif args.command == "remove":
        try:
            remove_provider(args.provider, args.passphrase, vault_path=vault_path)
            print(f"Removed provider: {args.provider}")
        except KeyError as exc:
            print(str(exc), file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    _cli()
