"""OAuth 2.0 loopback flow for Google Analytics 4.

Opens the user's browser for Google consent, catches the loopback redirect,
exchanges the authorisation code for access + refresh tokens, and writes them
to the seo-toolkit encrypted vault under provider ``ga4``.

Required scope: https://www.googleapis.com/auth/analytics.readonly

Usage::

    python oauth_ga4.py --passphrase VAULT_PASSPHRASE
    python oauth_ga4.py --passphrase VAULT_PASSPHRASE --client-id CLIENT_ID --client-secret CLIENT_SECRET
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

_GA4_SCOPE = "https://www.googleapis.com/auth/analytics.readonly"
_TOKEN_URI = "https://oauth2.googleapis.com/token"


def _load_client_secrets(client_secrets_path: str | None) -> tuple[str, str]:
    """Read client_id and client_secret from a GCP client_secret.json file."""
    if not client_secrets_path:
        raise ValueError(
            "No client secrets path provided. Pass --client-secrets-file or "
            "set GOOGLE_CLIENT_SECRETS_FILE."
        )
    path = Path(client_secrets_path)
    if not path.exists():
        raise FileNotFoundError(f"Client secrets file not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    app = data.get("installed") or data.get("web") or {}
    client_id = app.get("client_id", "")
    client_secret = app.get("client_secret", "")
    if not client_id or not client_secret:
        raise ValueError(f"Could not read client_id/client_secret from {path}")
    return client_id, client_secret


def run_oauth_flow(
    client_id: str,
    client_secret: str,
    passphrase: str,
) -> None:
    """Run the loopback OAuth flow and save tokens to the vault.

    Args:
        client_id:     Google OAuth client ID.
        client_secret: Google OAuth client secret.
        passphrase:    Vault passphrase for credential storage.
    """
    from google_auth_oauthlib.flow import InstalledAppFlow
    from datetime import timezone

    client_config = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": _TOKEN_URI,
            "redirect_uris": ["http://localhost"],
        }
    }

    flow = InstalledAppFlow.from_client_config(client_config, scopes=[_GA4_SCOPE])

    print("Opening browser for Google Analytics 4 authorisation...")
    print("If the browser does not open, visit the URL printed above manually.")

    creds = flow.run_local_server(
        port=0,
        prompt="consent",
        access_type="offline",
    )

    sys.path.insert(0, str(Path(__file__).parent))
    from lib.seo_vault import set_secret

    set_secret("ga4", "client_id", client_id, passphrase)
    set_secret("ga4", "client_secret", client_secret, passphrase)
    set_secret("ga4", "refresh_token", creds.refresh_token, passphrase)
    set_secret("ga4", "access_token", creds.token, passphrase)

    if creds.expiry:
        expiry = creds.expiry
        if expiry.tzinfo is None:
            expiry = expiry.replace(tzinfo=timezone.utc)
        set_secret("ga4", "access_token_expires_at", expiry.isoformat(), passphrase)

    print("GA4 credentials saved to vault successfully.")


def main() -> None:
    """Parse CLI arguments and run the GA4 OAuth flow."""
    parser = argparse.ArgumentParser(
        description="Authenticate Google Analytics 4 via OAuth 2.0"
    )
    parser.add_argument("--passphrase", required=True, help="Vault passphrase")
    parser.add_argument("--client-id", help="Google OAuth client ID")
    parser.add_argument("--client-secret", help="Google OAuth client secret")
    parser.add_argument(
        "--client-secrets-file",
        default=os.environ.get("GOOGLE_CLIENT_SECRETS_FILE"),
        help="Path to GCP client_secret.json (alternative to --client-id/--client-secret)",
    )
    args = parser.parse_args()

    client_id = args.client_id
    client_secret = args.client_secret

    if not client_id or not client_secret:
        if args.client_secrets_file:
            client_id, client_secret = _load_client_secrets(args.client_secrets_file)
        else:
            print(
                "Error: provide --client-id and --client-secret, "
                "or --client-secrets-file pointing to a GCP client_secret.json.",
                file=sys.stderr,
            )
            sys.exit(1)

    try:
        run_oauth_flow(client_id, client_secret, args.passphrase)
    except Exception as exc:  # noqa: BLE001
        print(f"OAuth flow failed: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
