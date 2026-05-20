"""SEO Toolkit credential validator.

Reads the encrypted vault and checks that every configured provider's
credentials are present and (for OAuth providers) refreshable.

Exit codes:
    0 — all configured providers are healthy
    1 — one or more providers are missing, stale, or invalid

Usage::

    python token_validator.py --json
    python token_validator.py --json --quiet
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Add scripts/ to path so lib imports work when called directly
sys.path.insert(0, str(Path(__file__).parent))

from lib.seo_vault import get_secret, read_vault


_PROVIDERS = ["serpapi", "dataforseo", "ahrefs", "moz", "psi", "gsc", "ga4"]
_OAUTH_PROVIDERS = {"gsc", "ga4"}
_WARN_DAYS = 7  # warn when OAuth token expires within this many days


def _check_api_key_provider(provider: str, passphrase: str, vault_path: Path | None) -> dict:
    """Validate a simple API-key provider."""
    key_names = {
        "serpapi": ["api_key"],
        "dataforseo": ["login", "password"],
        "ahrefs": ["api_key"],
        "moz": ["access_id", "secret"],
        "psi": ["api_key"],
    }
    required_keys = key_names.get(provider, ["api_key"])

    missing = []
    for k in required_keys:
        val = get_secret(provider, k, passphrase, vault_path=vault_path)
        if not val:
            missing.append(k)

    if missing:
        return {
            "status": "missing",
            "message": f"Missing fields: {', '.join(missing)}",
        }
    return {
        "status": "ok",
        "message": "API key present",
        "last_validated": datetime.now(timezone.utc).isoformat(),
    }


def _check_oauth_provider(provider: str, passphrase: str, vault_path: Path | None) -> dict:
    """Validate an OAuth provider by checking token presence and expiry."""
    refresh_token = get_secret(provider, "refresh_token", passphrase, vault_path=vault_path)
    if not refresh_token:
        return {
            "status": "missing",
            "message": "No refresh token — run /seo-toolkit:seo-connect to authenticate.",
        }

    expires_at_str = get_secret(
        provider, "access_token_expires_at", passphrase, vault_path=vault_path
    )
    now = datetime.now(timezone.utc)
    result: dict = {
        "status": "ok",
        "last_validated": now.isoformat(),
    }

    if expires_at_str:
        try:
            if expires_at_str.endswith("Z"):
                expires_at_str = expires_at_str[:-1] + "+00:00"
            expires_at = datetime.fromisoformat(expires_at_str)
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)

            days_left = (expires_at - now).days
            result["expires_at"] = expires_at.isoformat()
            result["expires_in_days"] = days_left

            if days_left < 0:
                result["status"] = "expired"
                result["message"] = f"Access token expired on {expires_at.date()}"
            elif days_left <= _WARN_DAYS:
                result["status"] = "expiring_soon"
                result["message"] = f"Access token expires in {days_left} days"
        except ValueError:
            pass  # Unparseable expiry — treat as ok, will refresh on use

    return result


def validate_all(passphrase: str, vault_path: Path | None = None) -> dict:
    """Run validation across all known providers.

    Args:
        passphrase: Vault passphrase.
        vault_path: Override vault path (for testing).

    Returns:
        Dict with ``status`` (``"ok"`` | ``"missing"`` | ``"stale"``) and
        ``providers`` mapping each provider name to its individual status dict.
    """
    # Check vault exists at all
    try:
        read_vault(passphrase, vault_path=vault_path)
    except FileNotFoundError:
        return {"status": "missing", "providers": {}}

    provider_statuses: dict = {}
    any_configured = False
    any_bad = False

    for provider in _PROVIDERS:
        if provider in _OAUTH_PROVIDERS:
            result = _check_oauth_provider(provider, passphrase, vault_path)
        else:
            result = _check_api_key_provider(provider, passphrase, vault_path)

        provider_statuses[provider] = result

        if result["status"] != "missing":
            any_configured = True
        if result["status"] in ("expired", "stale"):
            any_bad = True

    if not any_configured:
        overall = "missing"
    elif any_bad:
        overall = "stale"
    else:
        overall = "ok"

    return {"status": overall, "providers": provider_statuses}


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Validate seo-toolkit credentials")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--quiet", action="store_true", help="Suppress non-JSON output")
    args = parser.parse_args()

    passphrase = os.environ.get("SEO_VAULT_PASSPHRASE", "")
    vault_path_env = os.environ.get("SEO_VAULT_PATH")
    vault_path = Path(vault_path_env) if vault_path_env else None

    if not passphrase:
        if args.json:
            print(json.dumps({"status": "missing", "error": "SEO_VAULT_PASSPHRASE not set"}))
        elif not args.quiet:
            print("SEO_VAULT_PASSPHRASE not set", file=sys.stderr)
        sys.exit(1)

    results = validate_all(passphrase, vault_path=vault_path)

    if args.json:
        print(json.dumps(results, indent=2))
    elif not args.quiet:
        for provider, info in results["providers"].items():
            status = info.get("status", "unknown")
            print(f"{provider}: {status}")

    overall = results.get("status", "missing")
    if overall == "ok":
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
