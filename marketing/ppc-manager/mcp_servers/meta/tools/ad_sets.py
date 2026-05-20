"""Meta ad set (audience + placement + bidding) tools."""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

from mcp_servers.common.errors import wrap_http_error
from mcp_servers.common.logger import get_server_logger

logger = get_server_logger("ppc-meta.ad_sets")


def register(mcp, get_auth: Callable[[], Any]) -> None:
    @mcp.tool()
    def list_ad_sets(
        campaign_id: str, account_label: str = "default"
    ) -> Dict[str, Any]:
        """List ad sets in a Meta campaign."""
        try:
            from facebook_business.adobjects.campaign import Campaign

            get_auth().get_meta_api_init(account_label)
            campaign = Campaign(campaign_id)
            ad_sets = campaign.get_ad_sets(
                fields=[
                    "id",
                    "name",
                    "status",
                    "daily_budget",
                    "lifetime_budget",
                    "optimization_goal",
                    "billing_event",
                    "bid_strategy",
                    "targeting",
                    "start_time",
                    "end_time",
                ],
                params={"limit": 200},
            )
            return {"count": len(ad_sets), "ad_sets": [dict(a) for a in ad_sets]}
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def create_ad_set(
        ad_account_id: str,
        campaign_id: str,
        name: str,
        daily_budget_aud: float,
        optimization_goal: str,
        billing_event: str = "IMPRESSIONS",
        targeting: Optional[Dict[str, Any]] = None,
        status: str = "PAUSED",
        account_label: str = "default",
    ) -> Dict[str, Any]:
        """Create a Meta ad set inside a campaign.

        Args:
            optimization_goal: OFFSITE_CONVERSIONS, LINK_CLICKS, REACH,
                THRUPLAY, LANDING_PAGE_VIEWS, VALUE, etc.
            billing_event: IMPRESSIONS (default for most objectives) or LINK_CLICKS.
            targeting: Meta targeting dict. See reference.md for shape.
        """
        try:
            from facebook_business.adobjects.adaccount import AdAccount
            from facebook_business.adobjects.adset import AdSet

            get_auth().get_meta_api_init(account_label)
            if not ad_account_id.startswith("act_"):
                ad_account_id = f"act_{ad_account_id}"
            account = AdAccount(ad_account_id)
            params: Dict[str, Any] = {
                AdSet.Field.name: name,
                AdSet.Field.campaign_id: campaign_id,
                AdSet.Field.daily_budget: int(daily_budget_aud * 100),
                AdSet.Field.billing_event: billing_event,
                AdSet.Field.optimization_goal: optimization_goal,
                AdSet.Field.status: status,
                AdSet.Field.targeting: targeting or {"geo_locations": {"countries": ["AU"]}},
            }
            ad_set = account.create_ad_set(params=params)
            logger.info("Created Meta ad set '%s' in campaign %s", name, campaign_id)
            return {"id": ad_set.get("id"), "name": name, "status": status}
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def get_ad_set(
        ad_set_id: str, account_label: str = "default"
    ) -> Dict[str, Any]:
        """Get full details for a Meta ad set."""
        try:
            from facebook_business.adobjects.adset import AdSet

            get_auth().get_meta_api_init(account_label)
            ad_set = AdSet(ad_set_id)
            data = ad_set.api_get(
                fields=[
                    "id",
                    "name",
                    "status",
                    "configured_status",
                    "effective_status",
                    "campaign_id",
                    "daily_budget",
                    "lifetime_budget",
                    "budget_remaining",
                    "optimization_goal",
                    "billing_event",
                    "bid_strategy",
                    "bid_amount",
                    "targeting",
                    "start_time",
                    "end_time",
                    "created_time",
                    "updated_time",
                    "attribution_spec",
                    "learning_stage_info",
                    "issues_info",
                ]
            )
            return dict(data)
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def update_ad_set(
        ad_set_id: str,
        name: Optional[str] = None,
        daily_budget_aud: Optional[float] = None,
        lifetime_budget_aud: Optional[float] = None,
        bid_amount_aud: Optional[float] = None,
        optimization_goal: Optional[str] = None,
        targeting: Optional[Dict[str, Any]] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        account_label: str = "default",
    ) -> Dict[str, Any]:
        """Update a Meta ad set.

        Args:
            daily_budget_aud: New daily budget in AUD.
            lifetime_budget_aud: New lifetime budget in AUD.
            bid_amount_aud: New bid amount in AUD.
            targeting: New targeting dict (replaces the entire targeting spec).
            start_time: ISO-8601 timestamp.
            end_time: ISO-8601 timestamp.
        """
        try:
            from facebook_business.adobjects.adset import AdSet

            get_auth().get_meta_api_init(account_label)
            ad_set = AdSet(ad_set_id)
            params: Dict[str, Any] = {}
            if name is not None:
                params[AdSet.Field.name] = name
            if daily_budget_aud is not None:
                params[AdSet.Field.daily_budget] = int(daily_budget_aud * 100)
            if lifetime_budget_aud is not None:
                params[AdSet.Field.lifetime_budget] = int(lifetime_budget_aud * 100)
            if bid_amount_aud is not None:
                params[AdSet.Field.bid_amount] = int(bid_amount_aud * 100)
            if optimization_goal is not None:
                params[AdSet.Field.optimization_goal] = optimization_goal
            if targeting is not None:
                params[AdSet.Field.targeting] = targeting
            if start_time is not None:
                params[AdSet.Field.start_time] = start_time
            if end_time is not None:
                params[AdSet.Field.end_time] = end_time
            if not params:
                return {"error": "No fields to update"}
            ad_set.api_update(params=params)
            logger.info("Updated Meta ad set %s", ad_set_id)
            return {"id": ad_set_id, "updated_fields": list(params.keys())}
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def pause_ad_set(
        ad_set_id: str, account_label: str = "default"
    ) -> Dict[str, Any]:
        """Pause a Meta ad set."""
        try:
            from facebook_business.adobjects.adset import AdSet

            get_auth().get_meta_api_init(account_label)
            ad_set = AdSet(ad_set_id)
            ad_set.api_update(params={AdSet.Field.status: "PAUSED"})
            return {"id": ad_set_id, "status": "PAUSED"}
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def enable_ad_set(
        ad_set_id: str, account_label: str = "default"
    ) -> Dict[str, Any]:
        """Resume/enable a Meta ad set."""
        try:
            from facebook_business.adobjects.adset import AdSet

            get_auth().get_meta_api_init(account_label)
            ad_set = AdSet(ad_set_id)
            ad_set.api_update(params={AdSet.Field.status: "ACTIVE"})
            return {"id": ad_set_id, "status": "ACTIVE"}
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def archive_ad_set(
        ad_set_id: str, account_label: str = "default"
    ) -> Dict[str, Any]:
        """Archive a Meta ad set."""
        try:
            from facebook_business.adobjects.adset import AdSet

            get_auth().get_meta_api_init(account_label)
            ad_set = AdSet(ad_set_id)
            ad_set.api_update(params={AdSet.Field.status: "ARCHIVED"})
            return {"id": ad_set_id, "status": "ARCHIVED"}
        except Exception as exc:
            raise wrap_http_error(exc)
