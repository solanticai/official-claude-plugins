#!/usr/bin/env python3
"""Interactive Meta (Facebook) OAuth flow for ppc-manager.

Run this script to connect a Meta account. Spawns a local loopback server,
opens the system browser to the OAuth dialog, exchanges the returned code for
a short-lived token, then re-exchanges for a long-lived (~60-day) token.
Writes the long-lived token and the user's ad accounts to the encrypted vault.

Usage:
    python oauth_meta.py --app-id 1234 --app-secret abc --vault-path ... --vault-passphrase ...
"""

from __future__ import annotations

import argparse
import http.server
import json
import os
import secrets
import socket
import sys
import threading
import urllib.parse
import webbrowser
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Optional

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from lib.masking_logger import get_logger  # noqa: E402
from lib.meta_helpers import (  # noqa: E402
    MetaAPIError,
    exchange_code_for_token,
    exchange_long_lived_token,
    get_user_ad_accounts,
    get_user_info,
)
from lib.ppc_auth import META_SCOPES  # noqa: E402
from lib.vault import PPCVault, VaultFileNotFoundError  # noqa: E402

logger = get_logger("oauth_meta")

_FB_OAUTH_URL = "https://www.facebook.com/v22.0/dialog/oauth"


class _OAuthCallbackHandler(http.server.BaseHTTPRequestHandler):
    """One-shot HTTP handler that captures the ?code= from Meta's redirect."""

    captured_code: Optional[str] = None
    captured_state: Optional[str] = None
    captured_error: Optional[str] = None

    def log_message(self, format, *args):  # silence default stderr spam
        pass

    def do_GET(self):  # noqa: N802
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()

        if "error" in params:
            _OAuthCallbackHandler.captured_error = params["error"][0]
            body = (
                "<h1>ppc-manager: Meta OAuth failed</h1>"
                f"<p>{params.get('error_description', [''])[0]}</p>"
                "<p>You can close this tab.</p>"
            )
        elif "code" in params:
            _OAuthCallbackHandler.captured_code = params["code"][0]
            _OAuthCallbackHandler.captured_state = params.get("state", [""])[0]
            body = (
                "<h1>ppc-manager: Meta OAuth complete</h1>"
                "<p>You can close this tab.</p>"
            )
        else:
            body = "<h1>ppc-manager: waiting for OAuth redirect...</h1>"
        self.wfile.write(body.encode("utf-8"))


def _pick_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _run_loopback_server(port: int) -> http.server.HTTPServer:
    server = http.server.HTTPServer(("127.0.0.1", port), _OAuthCallbackHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def run(
    app_id: str,
    app_secret: str,
    vault_path: str,
    vault_passphrase: str,
    account_label: str = "default",
    no_browser: bool = False,
    port: Optional[int] = None,
    timeout_seconds: int = 300,
) -> Dict[str, Any]:
    port = port or _pick_free_port()
    redirect_uri = f"http://localhost:{port}/"
    state = secrets.token_urlsafe(24)

    auth_url = (
        f"{_FB_OAUTH_URL}"
        f"?client_id={urllib.parse.quote(app_id)}"
        f"&redirect_uri={urllib.parse.quote(redirect_uri)}"
        f"&scope={urllib.parse.quote(','.join(META_SCOPES))}"
        f"&response_type=code"
        f"&state={state}"
    )

    logger.info("Starting Meta loopback server on port %s", port)
    _OAuthCallbackHandler.captured_code = None
    _OAuthCallbackHandler.captured_state = None
    _OAuthCallbackHandler.captured_error = None
    server = _run_loopback_server(port)

    try:
        if no_browser:
            print(f"Open this URL in your browser to authorise ppc-manager:\n  {auth_url}")
        else:
            logger.info("Opening browser for Meta OAuth consent")
            webbrowser.open(auth_url)

        # Wait for the redirect to come back.
        import time as _time

        deadline = _time.monotonic() + timeout_seconds
        while _time.monotonic() < deadline:
            if _OAuthCallbackHandler.captured_code or _OAuthCallbackHandler.captured_error:
                break
            _time.sleep(0.2)
    finally:
        server.shutdown()
        server.server_close()

    if _OAuthCallbackHandler.captured_error:
        raise SystemExit(
            f"Meta OAuth failed: {_OAuthCallbackHandler.captured_error}"
        )
    if not _OAuthCallbackHandler.captured_code:
        raise SystemExit("Meta OAuth timed out waiting for redirect.")
    if _OAuthCallbackHandler.captured_state != state:
        raise SystemExit("Meta OAuth state mismatch — possible CSRF, aborting.")

    code = _OAuthCallbackHandler.captured_code
    logger.info("Got OAuth code; exchanging for short-lived token")
    try:
        short_token_payload = exchange_code_for_token(app_id, app_secret, redirect_uri, code)
    except MetaAPIError as exc:
        raise SystemExit(f"Short-lived token exchange failed: {exc}")

    short_token = short_token_payload.get("access_token")
    if not short_token:
        raise SystemExit(f"No access_token in short-lived exchange: {short_token_payload}")

    logger.info("Re-exchanging for long-lived token (~60 days)")
    try:
        long_payload = exchange_long_lived_token(app_id, app_secret, short_token)
    except MetaAPIError as exc:
        raise SystemExit(f"Long-lived exchange failed: {exc}")

    long_token = long_payload.get("access_token")
    if not long_token:
        raise SystemExit(f"No access_token in long-lived exchange: {long_payload}")
    expires_in = int(long_payload.get("expires_in", 60 * 24 * 3600))
    expires_at = (datetime.now(timezone.utc) + timedelta(seconds=expires_in)).isoformat()

    try:
        user = get_user_info(long_token)
    except MetaAPIError as exc:
        raise SystemExit(f"Could not fetch user info: {exc}")
    try:
        ad_accounts = get_user_ad_accounts(long_token)
    except MetaAPIError as exc:
        logger.warning("Could not fetch ad accounts: %s", exc)
        ad_accounts = []

    vault = PPCVault(vault_path, vault_passphrase)
    try:
        data = vault.load()
    except VaultFileNotFoundError:
        data = vault.init_empty()

    data.setdefault("meta", {}).setdefault("accounts", {})
    data["meta"]["app_secret"] = app_secret
    data["meta"]["accounts"][account_label] = {
        "label": account_label,
        "user_id": user.get("id"),
        "user_name": user.get("name"),
        "long_lived_user_token": long_token,
        "long_lived_user_token_expires_at": expires_at,
        "ad_accounts": [
            {
                "id": acc.get("id"),
                "account_id": acc.get("account_id"),
                "name": acc.get("name"),
                "currency": acc.get("currency"),
                "timezone_name": acc.get("timezone_name"),
                "status": acc.get("account_status"),
            }
            for acc in ad_accounts
        ],
        "connected_at": datetime.now(timezone.utc).isoformat(),
    }
    vault.save(data)

    result = {
        "account": account_label,
        "user": user,
        "ad_accounts_count": len(ad_accounts),
        "expires_at": expires_at,
        "vault_path": vault_path,
    }
    logger.info("Saved Meta account '%s' to vault", account_label)
    return result


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="ppc-manager Meta OAuth runner")
    parser.add_argument("--app-id", required=True, help="Meta app ID")
    parser.add_argument("--app-secret", required=True, help="Meta app secret")
    parser.add_argument("--account", default="default", help="Vault account label")
    parser.add_argument(
        "--vault-path",
        default=os.environ.get("PPC_VAULT_PATH"),
        help="Defaults to $PPC_VAULT_PATH",
    )
    parser.add_argument(
        "--vault-passphrase",
        default=os.environ.get("PPC_VAULT_PASSPHRASE"),
        help="Defaults to $PPC_VAULT_PASSPHRASE",
    )
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument("--port", type=int, default=None)
    parser.add_argument("--timeout", type=int, default=300)
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)
    if not args.vault_path or not args.vault_passphrase:
        logger.error("Vault path and passphrase are required")
        return 2

    result = run(
        app_id=args.app_id,
        app_secret=args.app_secret,
        vault_path=args.vault_path,
        vault_passphrase=args.vault_passphrase,
        account_label=args.account,
        no_browser=args.no_browser,
        port=args.port,
        timeout_seconds=args.timeout,
    )
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
