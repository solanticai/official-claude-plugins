"""Small helpers for interpreting Google client_secret JSON files and scopes.

Kept separate from ``ppc_auth.py`` to keep that file focused on runtime
credential lookup.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Tuple

from .ppc_auth import GOOGLE_SCOPES_ALL


class ClientSecretError(Exception):
    """Raised when a Google client_secret.json file is invalid or unreadable."""


def load_client_secret(path: str | Path) -> Dict[str, Any]:
    """Load and minimally validate a Google OAuth client_secret JSON file.

    Returns the dict shape Google ships — the caller can then pass it to
    ``google_auth_oauthlib.flow.InstalledAppFlow.from_client_config``.
    """
    p = Path(path)
    if not p.exists():
        raise ClientSecretError(f"client_secret file not found: {p}")
    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ClientSecretError(f"client_secret file is not valid JSON: {exc}") from exc
    if "installed" not in raw and "web" not in raw:
        raise ClientSecretError(
            "client_secret file is neither 'installed' nor 'web'. "
            "Create a Desktop app OAuth client in GCP."
        )
    return raw


def extract_client_id_secret(client_secret_dict: Dict[str, Any]) -> Tuple[str, str]:
    """Pull out the client_id / client_secret fields from a client_secret JSON."""
    section = client_secret_dict.get("installed") or client_secret_dict.get("web")
    if not section:
        raise ClientSecretError("client_secret JSON missing 'installed'/'web' section")
    client_id = section.get("client_id")
    client_secret = section.get("client_secret")
    if not client_id or not client_secret:
        raise ClientSecretError("client_secret JSON missing client_id or client_secret")
    return client_id, client_secret


def scopes_missing(existing: list[str]) -> list[str]:
    """Return scopes from GOOGLE_SCOPES_ALL that are not in ``existing``."""
    present = set(existing or [])
    return [s for s in GOOGLE_SCOPES_ALL if s not in present]
