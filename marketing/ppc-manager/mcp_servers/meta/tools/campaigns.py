"""Meta campaign CRUD tools."""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

from mcp_servers.common.errors import wrap_http_error
from mcp_servers.common.logger import get_server_logger

logger = get_server_logger("ppc-meta.campaigns")


def register(mcp, get_auth: Callable[[], Any]) -> None:
    @mcp.tool()
    def list_campaigns(
        ad_account_id: str,
        limit: int = 100,
        account_label: str = "default",
    ) -> Dict[str, Any]:
        """List campaigns in a Meta ad account.

        Args:
            ad_account_id: Full ad account id including the ``act_`` prefix.
        """
        try:
            from facebook_business.adobjects.adaccount import AdAccount

            get_auth().get_meta_api_init(account_label)
            if not ad_account_id.startswith("act_"):
                ad_account_id = f"act_{ad_account_id}"
            account = AdAccount(ad_account_id)
            campaigns = account.get_campaigns(
                fields=[
                    "id",
                    "name",
                    "status",
                    "objective",
                    "buying_type",
                    "daily_budget",
                    "lifetime_budget",
                    "start_time",
                    "stop_time",
                ],
                params={"limit": limit},
            )
            return {
                "count": len(campaigns),
                "campaigns": [dict(c) for c in campaigns],
            }
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def create_campaign(
        ad_account_id: str,
        name: str,
        objective: str,
        daily_budget_aud: float,
        status: str = "PAUSED",
        special_ad_categories: Optional[List[str]] = None,
        account_label: str = "default",
    ) -> Dict[str, Any]:
        """Create a Meta campaign.

        Args:
            objective: One of OUTCOME_SALES, OUTCOME_LEADS, OUTCOME_TRAFFIC,
                OUTCOME_AWARENESS, OUTCOME_ENGAGEMENT, OUTCOME_APP_PROMOTION.
            daily_budget_aud: Daily budget in AUD (converted to cents).
            status: PAUSED or ACTIVE.
            special_ad_categories: Required for HOUSING, EMPLOYMENT, CREDIT,
                ISSUES_ELECTIONS_POLITICS, otherwise pass an empty list.
        """
        try:
            from facebook_business.adobjects.adaccount import AdAccount
            from facebook_business.adobjects.campaign import Campaign

            get_auth().get_meta_api_init(account_label)
            if not ad_account_id.startswith("act_"):
                ad_account_id = f"act_{ad_account_id}"
            account = AdAccount(ad_account_id)
            params = {
                Campaign.Field.name: name,
                Campaign.Field.objective: objective,
                Campaign.Field.status: status,
                Campaign.Field.daily_budget: int(daily_budget_aud * 100),
                Campaign.Field.special_ad_categories: special_ad_categories or [],
            }
            campaign = account.create_campaign(params=params)
            logger.info("Created Meta campaign '%s' objective=%s status=%s", name, objective, status)
            return {"id": campaign.get("id"), "name": name, "status": status}
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def pause_campaign(
        campaign_id: str, account_label: str = "default"
    ) -> Dict[str, Any]:
        """Pause a Meta campaign."""
        try:
            from facebook_business.adobjects.campaign import Campaign

            get_auth().get_meta_api_init(account_label)
            campaign = Campaign(campaign_id)
            campaign.api_update(params={Campaign.Field.status: "PAUSED"})
            return {"id": campaign_id, "status": "PAUSED"}
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def get_campaign(
        campaign_id: str, account_label: str = "default"
    ) -> Dict[str, Any]:
        """Get full details for a Meta campaign."""
        try:
            from facebook_business.adobjects.campaign import Campaign

            get_auth().get_meta_api_init(account_label)
            campaign = Campaign(campaign_id)
            data = campaign.api_get(
                fields=[
                    "id",
                    "name",
                    "status",
                    "configured_status",
                    "effective_status",
                    "objective",
                    "buying_type",
                    "daily_budget",
                    "lifetime_budget",
                    "budget_remaining",
                    "spend_cap",
                    "bid_strategy",
                    "start_time",
                    "stop_time",
                    "created_time",
                    "updated_time",
                    "special_ad_categories",
                    "issues_info",
                ]
            )
            return dict(data)
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def update_campaign(
        campaign_id: str,
        name: Optional[str] = None,
        daily_budget_aud: Optional[float] = None,
        lifetime_budget_aud: Optional[float] = None,
        bid_strategy: Optional[str] = None,
        end_time: Optional[str] = None,
        account_label: str = "default",
    ) -> Dict[str, Any]:
        """Update a Meta campaign.

        Args:
            daily_budget_aud: New daily budget in AUD.
            lifetime_budget_aud: New lifetime budget in AUD.
            bid_strategy: ``LOWEST_COST_WITHOUT_CAP``,
                ``LOWEST_COST_WITH_BID_CAP``, ``COST_CAP``,
                ``LOWEST_COST_WITH_MIN_ROAS``.
            end_time: ISO-8601 timestamp for campaign end.
        """
        try:
            from facebook_business.adobjects.campaign import Campaign

            get_auth().get_meta_api_init(account_label)
            campaign = Campaign(campaign_id)
            params: Dict[str, Any] = {}
            if name is not None:
                params[Campaign.Field.name] = name
            if daily_budget_aud is not None:
                params[Campaign.Field.daily_budget] = int(daily_budget_aud * 100)
            if lifetime_budget_aud is not None:
                params[Campaign.Field.lifetime_budget] = int(lifetime_budget_aud * 100)
            if bid_strategy is not None:
                params[Campaign.Field.bid_strategy] = bid_strategy
            if end_time is not None:
                params[Campaign.Field.stop_time] = end_time
            if not params:
                return {"error": "No fields to update"}
            campaign.api_update(params=params)
            logger.info("Updated Meta campaign %s fields=%s", campaign_id, list(params.keys()))
            return {"id": campaign_id, "updated_fields": list(params.keys())}
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def enable_campaign(
        campaign_id: str, account_label: str = "default"
    ) -> Dict[str, Any]:
        """Resume/enable a Meta campaign by setting status = ACTIVE."""
        try:
            from facebook_business.adobjects.campaign import Campaign

            get_auth().get_meta_api_init(account_label)
            campaign = Campaign(campaign_id)
            campaign.api_update(params={Campaign.Field.status: "ACTIVE"})
            return {"id": campaign_id, "status": "ACTIVE"}
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def archive_campaign(
        campaign_id: str, account_label: str = "default"
    ) -> Dict[str, Any]:
        """Archive a Meta campaign. Archived campaigns cannot be reactivated."""
        try:
            from facebook_business.adobjects.campaign import Campaign

            get_auth().get_meta_api_init(account_label)
            campaign = Campaign(campaign_id)
            campaign.api_update(params={Campaign.Field.status: "ARCHIVED"})
            return {"id": campaign_id, "status": "ARCHIVED"}
        except Exception as exc:
            raise wrap_http_error(exc)
