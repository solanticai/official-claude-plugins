#!/usr/bin/env python3
"""Interactive Google OAuth flow for ppc-manager.

Run this script to connect a Google account that covers GTM, GA4, and Google
Ads in a single consent. Tokens are written to the encrypted vault at
``$PPC_VAULT_PATH`` using the passphrase ``$PPC_VAULT_PASSPHRASE``.

Usage:
    python oauth_google.py --client-secret /path/to/client_secret.json
    python oauth_google.py --client-secret /path/to/client_secret.json --account client-a
    python oauth_google.py --reauth default   # refresh scopes for an existing account

The script spawns a one-shot local HTTP server on a random port, opens the
system browser, catches the OAuth redirect, exchanges the code, and exits.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

# Allow running as a standalone script without PYTHONPATH gymnastics.
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from lib.google_helpers import (  # noqa: E402
    ClientSecretError,
    extract_client_id_secret,
    load_client_secret,
)
from lib.masking_logger import get_logger  # noqa: E402
from lib.ppc_auth import GOOGLE_SCOPES_ALL  # noqa: E402
from lib.vault import PPCVault, VaultFileNotFoundError  # noqa: E402

logger = get_logger("oauth_google")


def run(
    client_secret_path: str,
    account_label: str,
    vault_path: str,
    vault_passphrase: str,
    no_browser: bool = False,
    port: int = 0,
) -> Dict[str, Any]:
    """Run the Google OAuth flow and write the result to the vault."""
    # Delay heavy imports until we know we need them; keeps the CLI snappy for
    # --help and lets unit tests stub the module out cleanly.
    from google_auth_oauthlib.flow import InstalledAppFlow

    # Relax strict scope validation — Google sometimes returns a superset of
    # what you requested and the oauthlib default raises on that.
    os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"

    try:
        client_secret = load_client_secret(client_secret_path)
    except ClientSecretError as exc:
        logger.error("Failed to load client_secret: %s", exc)
        raise SystemExit(2)

    client_id, client_secret_str = extract_client_id_secret(client_secret)
    logger.info("Loaded client_secret for client_id=%s", client_id[:12] + "...")

    flow = InstalledAppFlow.from_client_config(client_secret, GOOGLE_SCOPES_ALL)
    logger.info("Starting local loopback OAuth flow on port=%s", port or "auto")
    creds = flow.run_local_server(
        port=port,
        open_browser=not no_browser,
        access_type="offline",
        prompt="consent",
        authorization_prompt_message=(
            "ppc-manager: opening your browser to authorise Google access..."
        ),
        success_message=(
            "ppc-manager: Google OAuth complete. You can close this browser tab."
        ),
    )

    if not creds.refresh_token:
        logger.error(
            "Google flow returned no refresh_token. Ensure access_type=offline "
            "and prompt=consent, and that this is a Desktop OAuth client."
        )
        raise SystemExit(3)

    # Try to fetch the user's email for the account label metadata.
    email = _fetch_user_email(creds)
    expiry = _isoformat(creds.expiry)

    vault = PPCVault(vault_path, vault_passphrase)
    try:
        data = vault.load()
    except VaultFileNotFoundError:
        data = vault.init_empty()

    data.setdefault("google", {}).setdefault("accounts", {})
    data["google"]["client_secret"] = client_secret_str
    data["google"]["accounts"][account_label] = {
        "label": account_label,
        "email": email,
        "client_id": client_id,
        "refresh_token": creds.refresh_token,
        "access_token": creds.token,
        "access_token_expires_at": expiry,
        "scopes": list(creds.scopes or GOOGLE_SCOPES_ALL),
        "connected_at": datetime.now(timezone.utc).isoformat(),
    }
    vault.save(data)

    logger.info("Saved Google account '%s' to vault (%s)", account_label, email or "no email")
    return {
        "account": account_label,
        "email": email,
        "scopes": list(creds.scopes or GOOGLE_SCOPES_ALL),
        "vault_path": vault_path,
    }


def _fetch_user_email(creds) -> Optional[str]:
    """Return the signed-in user's email, or None if the call fails."""
    try:
        from googleapiclient.discovery import build

        service = build("oauth2", "v2", credentials=creds, cache_discovery=False)
        info = service.userinfo().get().execute()
        return info.get("email")
    except Exception as exc:  # pragma: no cover - best effort only
        logger.warning("Could not fetch user email: %s", exc)
        return None


def _isoformat(dt) -> Optional[str]:
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="ppc-manager Google OAuth runner")
    parser.add_argument(
        "--client-secret",
        required=True,
        help="Absolute path to the Google OAuth client_secret.json (Desktop client).",
    )
    parser.add_argument(
        "--account",
        default="default",
        help="Label for this account in the vault (default: 'default').",
    )
    parser.add_argument(
        "--vault-path",
        default=os.environ.get("PPC_VAULT_PATH"),
        help="Path to the encrypted vault. Defaults to $PPC_VAULT_PATH.",
    )
    parser.add_argument(
        "--vault-passphrase",
        default=os.environ.get("PPC_VAULT_PASSPHRASE"),
        help="Vault passphrase. Defaults to $PPC_VAULT_PASSPHRASE.",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Do not try to open a browser automatically. Print the URL instead.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=0,
        help="Port for the local loopback server (0 = random free port).",
    )
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)
    if not args.vault_path:
        logger.error("Vault path not provided. Pass --vault-path or set PPC_VAULT_PATH.")
        return 2
    if not args.vault_passphrase:
        logger.error("Vault passphrase not provided. Pass --vault-passphrase or set PPC_VAULT_PASSPHRASE.")
        return 2

    result = run(
        client_secret_path=args.client_secret,
        account_label=args.account,
        vault_path=args.vault_path,
        vault_passphrase=args.vault_passphrase,
        no_browser=args.no_browser,
        port=args.port,
    )
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
