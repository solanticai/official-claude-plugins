"""Meta ad account discovery tools."""

from __future__ import annotations

from typing import Any, Callable, Dict, List

from mcp_servers.common.errors import wrap_http_error
from mcp_servers.common.logger import get_server_logger

logger = get_server_logger("ppc-meta.accounts")


def register(mcp, get_auth: Callable[[], Any]) -> None:
    @mcp.tool()
    def list_ad_accounts(account_label: str = "default") -> Dict[str, Any]:
        """List every Meta ad account the stored long-lived token can access."""
        try:
            from facebook_business.adobjects.user import User

            get_auth().get_meta_api_init(account_label)
            me = User(fbid="me")
            accounts = me.get_ad_accounts(
                fields=[
                    "id",
                    "account_id",
                    "name",
                    "currency",
                    "timezone_name",
                    "account_status",
                    "spend_cap",
                    "business",
                ],
                params={"limit": 100},
            )
            result = [
                {
                    "id": a.get("id"),
                    "account_id": a.get("account_id"),
                    "name": a.get("name"),
                    "currency": a.get("currency"),
                    "timezone": a.get("timezone_name"),
                    "status": a.get("account_status"),
                    "spend_cap": a.get("spend_cap"),
                    "business_id": (a.get("business") or {}).get("id"),
                }
                for a in accounts
            ]
            return {"count": len(result), "accounts": result}
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def list_businesses(account_label: str = "default") -> Dict[str, Any]:
        """List Meta Business Manager accounts the user can access."""
        try:
            from facebook_business.adobjects.user import User

            get_auth().get_meta_api_init(account_label)
            me = User(fbid="me")
            businesses = me.get_businesses(fields=["id", "name", "verification_status"])
            return {
                "count": len(businesses),
                "businesses": [
                    {
                        "id": b.get("id"),
                        "name": b.get("name"),
                        "verification_status": b.get("verification_status"),
                    }
                    for b in businesses
                ],
            }
        except Exception as exc:
            raise wrap_http_error(exc)
