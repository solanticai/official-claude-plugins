"""Meta Facebook Pages tools — required for creative creation."""

from __future__ import annotations

from typing import Any, Callable, Dict, List

from mcp_servers.common.errors import wrap_http_error
from mcp_servers.common.logger import get_server_logger

logger = get_server_logger("ppc-meta.pages")


def register(mcp, get_auth: Callable[[], Any]) -> None:
    @mcp.tool()
    def list_pages(
        account_label: str = "default",
    ) -> Dict[str, Any]:
        """List Facebook Pages accessible by the authenticated user.

        Returns page IDs that are required when creating ad creatives
        (the ``page_id`` parameter in ``create_creative``).
        """
        try:
            from facebook_business.adobjects.user import User

            get_auth().get_meta_api_init(account_label)
            me = User(fbid="me")
            pages = me.get_accounts(
                fields=[
                    "id",
                    "name",
                    "category",
                    "access_token",
                    "fan_count",
                    "link",
                    "picture",
                ],
                params={"limit": 100},
            )
            results: List[Dict[str, Any]] = []
            for p in pages:
                d = dict(p)
                results.append({
                    "id": d.get("id"),
                    "name": d.get("name"),
                    "category": d.get("category"),
                    "fan_count": d.get("fan_count"),
                    "link": d.get("link"),
                })
            return {"count": len(results), "pages": results}
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def get_page(
        page_id: str,
        account_label: str = "default",
    ) -> Dict[str, Any]:
        """Get details for a Facebook Page.

        Args:
            page_id: The Facebook Page ID.
        """
        try:
            from facebook_business.adobjects.page import Page

            get_auth().get_meta_api_init(account_label)
            page = Page(page_id)
            data = page.api_get(
                fields=[
                    "id",
                    "name",
                    "category",
                    "fan_count",
                    "link",
                    "about",
                    "website",
                    "picture",
                    "connected_instagram_account",
                ]
            )
            return dict(data)
        except Exception as exc:
            raise wrap_http_error(exc)
