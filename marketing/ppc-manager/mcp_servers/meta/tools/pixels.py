"""Meta pixel discovery tools."""

from __future__ import annotations

from typing import Any, Callable, Dict, List

from mcp_servers.common.errors import wrap_http_error
from mcp_servers.common.logger import get_server_logger

logger = get_server_logger("ppc-meta.pixels")


def register(mcp, get_auth: Callable[[], Any]) -> None:
    @mcp.tool()
    def list_pixels(
        ad_account_id: str, account_label: str = "default"
    ) -> Dict[str, Any]:
        """List Meta pixels accessible from an ad account."""
        try:
            from facebook_business.adobjects.adaccount import AdAccount

            get_auth().get_meta_api_init(account_label)
            if not ad_account_id.startswith("act_"):
                ad_account_id = f"act_{ad_account_id}"
            account = AdAccount(ad_account_id)
            pixels = account.get_ads_pixels(fields=["id", "name", "creation_time", "last_fired_time"])
            return {"count": len(pixels), "pixels": [dict(p) for p in pixels]}
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def get_pixel_events(
        pixel_id: str,
        account_label: str = "default",
    ) -> Dict[str, Any]:
        """Get the event names fired on a Meta pixel over the last 7 days."""
        try:
            from facebook_business.adobjects.adspixel import AdsPixel

            get_auth().get_meta_api_init(account_label)
            pixel = AdsPixel(pixel_id)
            stats = pixel.get_stats(
                fields=["data"],
                params={"aggregation": "event", "start_time": 0, "end_time": 0},
            )
            return {"pixel_id": pixel_id, "stats": [dict(s) for s in stats]}
        except Exception as exc:
            raise wrap_http_error(exc)
