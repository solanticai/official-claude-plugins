#!/usr/bin/env python3
"""Validate every credential in the ppc-manager vault with a read-only ping.

Usage:
    python token_validator.py
    python token_validator.py --quiet           # exit code only, no stdout on success
    python token_validator.py --json            # machine-readable output

Used by the SessionStart hook (`check-credentials.sh`) and by `oauth-setup` at
the end of its flow.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from lib.masking_logger import get_logger  # noqa: E402
from lib.ppc_auth import AuthError, PPCAuth  # noqa: E402
from lib.vault import VaultError, VaultFileNotFoundError  # noqa: E402

logger = get_logger("token_validator")

WARN_DAYS_BEFORE_EXPIRY = 7


def _parse_iso(value: str | None):
    if not value:
        return None
    try:
        if value.endswith("Z"):
            value = value[:-1] + "+00:00"
        dt = datetime.fromisoformat(value)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def validate(auth: PPCAuth) -> List[Dict[str, Any]]:
    """Validate every credential in the vault and return a list of status records."""
    results: List[Dict[str, Any]] = []
    try:
        data = auth.vault.load()
    except VaultFileNotFoundError:
        return [
            {
                "platform": "vault",
                "status": "missing",
                "detail": "Vault file not found. Run /ppc-manager:oauth-setup.",
            }
        ]

    # Google accounts (GTM + GA4 share the same refresh token)
    for label, account in (data.get("google", {}).get("accounts") or {}).items():
        record: Dict[str, Any] = {
            "platform": "google",
            "account": label,
            "email": account.get("email"),
        }
        try:
            auth.get_google_credentials(label)
            record["status"] = "ok"
        except AuthError as exc:
            record["status"] = "failed"
            record["detail"] = str(exc)
        except Exception as exc:
            record["status"] = "failed"
            record["detail"] = f"{type(exc).__name__}: {exc}"
        results.append(record)

    # Google Ads accounts (depend on a linked Google account)
    for label, ads_account in (data.get("google_ads", {}).get("accounts") or {}).items():
        record = {
            "platform": "google_ads",
            "account": label,
            "customer_id": ads_account.get("customer_id"),
        }
        try:
            # We don't actually call the API here to avoid eating quota — a
            # successful google_credentials refresh on the linked account plus
            # a present developer_token is enough for a session-start check.
            auth.get_google_credentials(ads_account.get("linked_google_account", "default"))
            developer_token = os.environ.get(
                "GOOGLE_ADS_DEVELOPER_TOKEN"
            ) or os.environ.get("CLAUDE_PLUGIN_OPTION_GOOGLE_ADS_DEVELOPER_TOKEN")
            if not developer_token:
                raise AuthError("Google Ads developer token not configured")
            record["status"] = "ok"
        except AuthError as exc:
            record["status"] = "failed"
            record["detail"] = str(exc)
        results.append(record)

    # Meta accounts
    for label, account in (data.get("meta", {}).get("accounts") or {}).items():
        record = {
            "platform": "meta",
            "account": label,
            "user_name": account.get("user_name"),
        }
        expires_at = _parse_iso(account.get("long_lived_user_token_expires_at"))
        now = datetime.now(timezone.utc)
        if expires_at is None:
            record["status"] = "unknown_expiry"
        elif expires_at <= now:
            record["status"] = "expired"
            record["detail"] = f"Meta token expired on {expires_at.isoformat()}"
        else:
            days_left = (expires_at - now).days
            if days_left <= WARN_DAYS_BEFORE_EXPIRY:
                record["status"] = "expiring_soon"
                record["days_left"] = days_left
            else:
                record["status"] = "ok"
                record["days_left"] = days_left
        results.append(record)

    if not results:
        results.append(
            {
                "platform": "vault",
                "status": "empty",
                "detail": "Vault exists but has no accounts. Run /ppc-manager:oauth-setup.",
            }
        )
    return results


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="ppc-manager token validator")
    parser.add_argument("--quiet", action="store_true", help="Only print on failure")
    parser.add_argument("--json", action="store_true", help="Machine-readable JSON output")
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
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    if not args.vault_path or not args.vault_passphrase:
        if args.quiet:
            return 1
        print(
            json.dumps(
                {
                    "status": "error",
                    "detail": "Vault path or passphrase not set",
                }
            )
        )
        return 2

    from lib.vault import PPCVault

    try:
        auth = PPCAuth(PPCVault(args.vault_path, args.vault_passphrase))
        results = validate(auth)
    except VaultError as exc:
        results = [{"platform": "vault", "status": "failed", "detail": str(exc)}]

    has_failure = any(r.get("status") not in {"ok", "expiring_soon"} for r in results)
    has_warning = any(r.get("status") == "expiring_soon" for r in results)

    if args.quiet and not has_failure and not has_warning:
        return 0

    if args.json:
        print(json.dumps({"results": results}, indent=2))
    else:
        for r in results:
            status = r.get("status", "unknown")
            platform = r.get("platform", "?")
            account = r.get("account", "")
            detail = r.get("detail", "")
            extra = f" ({detail})" if detail else ""
            line = f"[{status.upper()}] {platform}:{account}{extra}"
            print(line)

    return 1 if has_failure else 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
