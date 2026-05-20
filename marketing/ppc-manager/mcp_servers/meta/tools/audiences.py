"""Meta audience tools: custom audience, lookalike, list."""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

from mcp_servers.common.errors import wrap_http_error
from mcp_servers.common.logger import get_server_logger

logger = get_server_logger("ppc-meta.audiences")


def register(mcp, get_auth: Callable[[], Any]) -> None:
    @mcp.tool()
    def list_custom_audiences(
        ad_account_id: str, account_label: str = "default"
    ) -> Dict[str, Any]:
        """List custom audiences in a Meta ad account."""
        try:
            from facebook_business.adobjects.adaccount import AdAccount

            get_auth().get_meta_api_init(account_label)
            if not ad_account_id.startswith("act_"):
                ad_account_id = f"act_{ad_account_id}"
            account = AdAccount(ad_account_id)
            audiences = account.get_custom_audiences(
                fields=[
                    "id",
                    "name",
                    "approximate_count_lower_bound",
                    "approximate_count_upper_bound",
                    "subtype",
                    "rule",
                ],
                params={"limit": 200},
            )
            return {"count": len(audiences), "audiences": [dict(a) for a in audiences]}
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def create_custom_audience_from_pixel(
        ad_account_id: str,
        pixel_id: str,
        name: str,
        event: str = "Purchase",
        retention_days: int = 180,
        account_label: str = "default",
    ) -> Dict[str, Any]:
        """Create a custom audience based on a pixel event.

        Args:
            event: Pixel event name (e.g. Purchase, AddToCart, ViewContent).
            retention_days: 1-365.
        """
        try:
            from facebook_business.adobjects.adaccount import AdAccount
            from facebook_business.adobjects.customaudience import CustomAudience

            get_auth().get_meta_api_init(account_label)
            if not ad_account_id.startswith("act_"):
                ad_account_id = f"act_{ad_account_id}"
            account = AdAccount(ad_account_id)
            rule = {
                "inclusions": {
                    "operator": "or",
                    "rules": [
                        {
                            "event_sources": [{"id": pixel_id, "type": "pixel"}],
                            "retention_seconds": retention_days * 86400,
                            "filter": {
                                "operator": "and",
                                "filters": [
                                    {
                                        "field": "event",
                                        "operator": "eq",
                                        "value": event,
                                    }
                                ],
                            },
                        }
                    ],
                }
            }
            params = {
                CustomAudience.Field.name: name,
                CustomAudience.Field.subtype: "WEBSITE",
                CustomAudience.Field.retention_days: retention_days,
                CustomAudience.Field.rule: rule,
                CustomAudience.Field.prefill: True,
            }
            audience = account.create_custom_audience(params=params)
            logger.info("Created Meta pixel audience '%s' event=%s", name, event)
            return {"id": audience.get("id"), "name": name}
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def create_lookalike_audience(
        ad_account_id: str,
        source_audience_id: str,
        name: str,
        country: str = "AU",
        ratio: float = 0.01,
        account_label: str = "default",
    ) -> Dict[str, Any]:
        """Create a lookalike audience from a source audience.

        Args:
            ratio: 0.01-0.20 (1%-20% of country population).
        """
        try:
            from facebook_business.adobjects.adaccount import AdAccount
            from facebook_business.adobjects.customaudience import CustomAudience

            get_auth().get_meta_api_init(account_label)
            if not ad_account_id.startswith("act_"):
                ad_account_id = f"act_{ad_account_id}"
            account = AdAccount(ad_account_id)
            params = {
                CustomAudience.Field.name: name,
                CustomAudience.Field.subtype: "LOOKALIKE",
                CustomAudience.Field.origin_audience_id: source_audience_id,
                CustomAudience.Field.lookalike_spec: {
                    "country": country,
                    "ratio": ratio,
                    "type": "similarity",
                },
            }
            audience = account.create_custom_audience(params=params)
            logger.info(
                "Created Meta lookalike '%s' from source=%s country=%s ratio=%.2f",
                name,
                source_audience_id,
                country,
                ratio,
            )
            return {"id": audience.get("id"), "name": name}
        except Exception as exc:
            raise wrap_http_error(exc)
