"""Shared auth and helper library for every ppc-manager MCP server and script."""

from .vault import PPCVault, VaultError, VaultFileNotFoundError, VaultDecryptError
from .ppc_auth import (
    PPCAuth,
    AuthError,
    GOOGLE_SCOPES_ALL,
    META_SCOPES,
    VAULT_VERSION,
)

__all__ = [
    "PPCVault",
    "VaultError",
    "VaultFileNotFoundError",
    "VaultDecryptError",
    "PPCAuth",
    "AuthError",
    "GOOGLE_SCOPES_ALL",
    "META_SCOPES",
    "VAULT_VERSION",
]
