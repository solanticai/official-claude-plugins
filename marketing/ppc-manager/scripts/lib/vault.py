"""Encrypted token vault for ppc-manager.

The vault stores every rotating OAuth secret the plugin needs (Google refresh
tokens, Meta long-lived tokens, access-token caches, per-account labels and
metadata) in a single Fernet-encrypted JSON blob at
``${CLAUDE_PLUGIN_DATA}/tokens.enc``.

Encryption: Fernet (AES-128-CBC + HMAC-SHA256). The Fernet key is derived from
a user-supplied passphrase via PBKDF2-HMAC-SHA256 with 100 000 iterations and a
fixed, plugin-scoped salt.

Writes are atomic: temp file -> fsync -> os.replace. A filelock protects
concurrent writes between the four MCP server processes.

This is the ONLY module that touches crypto. Keep it small and boring.
"""

from __future__ import annotations

import base64
import json
import logging
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from filelock import FileLock, Timeout

logger = logging.getLogger(__name__)

# Fixed, plugin-scoped salt. Not secret — its job is to bind the KDF output to
# this plugin identity so a stolen vault cannot be decrypted by a password
# reused with a different PBKDF2 context.
_SALT = b"solanticai-ppc-manager-v1-salt__"  # must be 32 bytes
assert len(_SALT) == 32, "PBKDF2 salt must be 32 bytes"

_PBKDF2_ITERATIONS = 100_000
_LOCK_TIMEOUT = 30  # seconds


class VaultError(Exception):
    """Base class for all vault errors."""


class VaultFileNotFoundError(VaultError):
    """Raised when the vault file does not exist on disk."""


class VaultDecryptError(VaultError):
    """Raised when the passphrase is wrong or the vault is corrupted."""


def _derive_key(passphrase: str) -> bytes:
    """Derive a Fernet key from the vault passphrase."""
    if not passphrase:
        raise VaultError("Vault passphrase is empty")
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=_SALT,
        iterations=_PBKDF2_ITERATIONS,
    )
    raw = kdf.derive(passphrase.encode("utf-8"))
    return base64.urlsafe_b64encode(raw)


def _empty_vault() -> Dict[str, Any]:
    """Return the canonical empty-vault structure."""
    return {
        "version": 1,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "google": {
            "client_secret": None,
            "accounts": {},
        },
        "google_ads": {
            "accounts": {},
        },
        "meta": {
            "app_secret": None,
            "accounts": {},
        },
    }


class PPCVault:
    """Load, mutate, and persist the encrypted ppc-manager vault.

    Typical usage inside an MCP server::

        vault = PPCVault(
            path=os.environ["PPC_VAULT_PATH"],
            passphrase=os.environ["PPC_VAULT_PASSPHRASE"],
        )
        data = vault.load()          # decrypt + deserialise
        data["google"]["accounts"]["default"]["access_token"] = "..."
        vault.save(data)             # atomic encrypt + write

    ``load()`` memoises — subsequent calls return the cached dict. Call
    ``invalidate()`` to force a re-read from disk. ``save()`` always writes
    through to disk and refreshes the cache.
    """

    def __init__(self, path: str | os.PathLike, passphrase: str):
        self.path = Path(path)
        self._passphrase = passphrase
        self._key = _derive_key(passphrase)
        self._fernet = Fernet(self._key)
        self._cache: Optional[Dict[str, Any]] = None
        self._lock_path = f"{self.path}.lock"

    # ---- public API ----

    def exists(self) -> bool:
        return self.path.exists()

    def load(self, *, force: bool = False) -> Dict[str, Any]:
        """Decrypt and deserialise the vault file.

        Args:
            force: If True, bypass the in-memory cache and re-read from disk.

        Raises:
            VaultFileNotFoundError: if the vault file does not exist.
            VaultDecryptError: if the passphrase is wrong or the blob is corrupt.
        """
        if self._cache is not None and not force:
            return self._cache

        if not self.path.exists():
            raise VaultFileNotFoundError(f"Vault file not found: {self.path}")

        try:
            blob = self.path.read_bytes()
        except OSError as exc:
            raise VaultError(f"Failed to read vault file: {exc}") from exc

        try:
            plaintext = self._fernet.decrypt(blob)
        except InvalidToken as exc:
            raise VaultDecryptError(
                "Failed to decrypt vault. Passphrase is wrong or the vault is corrupt."
            ) from exc

        try:
            data = json.loads(plaintext.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise VaultDecryptError(
                "Vault decrypted but contained invalid JSON."
            ) from exc

        self._cache = data
        return data

    def save(self, data: Dict[str, Any]) -> None:
        """Atomically encrypt and persist the vault.

        Uses a ``filelock`` around the write to prevent races between the four
        MCP server processes. Writes to a temp file, fsyncs it, then
        ``os.replace`` to the final path.
        """
        data = dict(data)  # shallow copy before mutating
        data["updated_at"] = datetime.now(timezone.utc).isoformat()
        if "version" not in data:
            data["version"] = 1

        plaintext = json.dumps(data, indent=2, sort_keys=True).encode("utf-8")
        ciphertext = self._fernet.encrypt(plaintext)

        self.path.parent.mkdir(parents=True, exist_ok=True)

        lock = FileLock(self._lock_path, timeout=_LOCK_TIMEOUT)
        try:
            with lock:
                self._atomic_write(ciphertext)
        except Timeout as exc:
            raise VaultError(
                f"Timed out waiting for vault lock after {_LOCK_TIMEOUT}s"
            ) from exc

        self._cache = data

    def _atomic_write(self, ciphertext: bytes) -> None:
        """Write ciphertext to self.path atomically."""
        # tempfile.mkstemp creates the file mode 0600 on POSIX, which is what
        # we want for a secrets file. Windows ignores the mode bits.
        fd, tmp_path = tempfile.mkstemp(
            prefix=".tokens.", suffix=".enc.tmp", dir=str(self.path.parent)
        )
        try:
            with os.fdopen(fd, "wb") as fh:
                fh.write(ciphertext)
                fh.flush()
                try:
                    os.fsync(fh.fileno())
                except OSError:
                    # Some filesystems (e.g. some Windows network shares)
                    # don't support fsync on file descriptors. Non-fatal.
                    pass
            os.replace(tmp_path, self.path)
            # On POSIX, ensure the file is 0600 after replace.
            try:
                os.chmod(self.path, 0o600)
            except (NotImplementedError, PermissionError, OSError):
                pass
        except Exception:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise

    def init_empty(self) -> Dict[str, Any]:
        """Create and persist an empty vault. Overwrites any existing file."""
        data = _empty_vault()
        self.save(data)
        return data

    def invalidate(self) -> None:
        """Drop the in-memory cache. Next load() will re-read from disk."""
        self._cache = None

    # ---- convenience helpers ----

    def update_google_account(
        self, label: str, account: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Upsert a Google account entry and save."""
        data = self.load() if self.exists() else _empty_vault()
        data.setdefault("google", {}).setdefault("accounts", {})[label] = account
        self.save(data)
        return data

    def update_meta_account(
        self, label: str, account: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Upsert a Meta account entry and save."""
        data = self.load() if self.exists() else _empty_vault()
        data.setdefault("meta", {}).setdefault("accounts", {})[label] = account
        self.save(data)
        return data

    def update_google_ads_account(
        self, label: str, account: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Upsert a Google Ads account entry and save."""
        data = self.load() if self.exists() else _empty_vault()
        data.setdefault("google_ads", {}).setdefault("accounts", {})[label] = account
        self.save(data)
        return data
