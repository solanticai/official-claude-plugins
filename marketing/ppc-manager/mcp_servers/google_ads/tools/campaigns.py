"""Google Ads campaign CRUD tools."""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

from mcp_servers.common.errors import wrap_http_error
from mcp_servers.common.logger import get_server_logger

logger = get_server_logger("ppc-google-ads.campaigns")


def register(mcp, get_auth: Callable[[], Any]) -> None:
    @mcp.tool()
    def list_campaigns(
        customer_id: str,
        status: Optional[str] = None,
        account_label: str = "default",
    ) -> Dict[str, Any]:
        """List campaigns on a customer account.

        Args:
            status: Optional filter — `ENABLED`, `PAUSED`, or `REMOVED`.
        """
        try:
            client = get_auth().get_google_ads_client(account_label)
            service = client.get_service("GoogleAdsService")
            where = f"WHERE campaign.status = '{status}'" if status else ""
            query = f"""
                SELECT
                    campaign.id,
                    campaign.name,
                    campaign.status,
                    campaign.advertising_channel_type,
                    campaign.advertising_channel_sub_type,
                    campaign.bidding_strategy_type,
                    campaign_budget.amount_micros,
                    campaign.start_date,
                    campaign.end_date
                FROM campaign
                {where}
                ORDER BY campaign.name
                LIMIT 1000
            """
            response = service.search(customer_id=customer_id, query=query)
            campaigns: List[Dict[str, Any]] = []
            for row in response:
                c = row.campaign
                campaigns.append(
                    {
                        "id": str(c.id),
                        "name": c.name,
                        "status": c.status.name if hasattr(c.status, "name") else str(c.status),
                        "channel_type": c.advertising_channel_type.name
                        if hasattr(c.advertising_channel_type, "name")
                        else str(c.advertising_channel_type),
                        "channel_sub_type": c.advertising_channel_sub_type.name
                        if hasattr(c.advertising_channel_sub_type, "name")
                        else str(c.advertising_channel_sub_type),
                        "bidding_strategy_type": c.bidding_strategy_type.name
                        if hasattr(c.bidding_strategy_type, "name")
                        else str(c.bidding_strategy_type),
                        "budget_amount_micros": row.campaign_budget.amount_micros
                        if row.campaign_budget
                        else None,
                        "start_date": c.start_date,
                        "end_date": c.end_date,
                    }
                )
            return {
                "customer_id": customer_id,
                "count": len(campaigns),
                "campaigns": campaigns,
            }
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def get_campaign(
        customer_id: str,
        campaign_id: str,
        account_label: str = "default",
    ) -> Dict[str, Any]:
        """Get full details for a single campaign."""
        try:
            client = get_auth().get_google_ads_client(account_label)
            service = client.get_service("GoogleAdsService")
            query = f"""
                SELECT
                    campaign.id, campaign.name, campaign.status,
                    campaign.advertising_channel_type,
                    campaign.advertising_channel_sub_type,
                    campaign.bidding_strategy_type,
                    campaign_budget.amount_micros,
                    campaign_budget.delivery_method,
                    campaign.start_date, campaign.end_date,
                    campaign.network_settings.target_google_search,
                    campaign.network_settings.target_search_network,
                    campaign.network_settings.target_content_network,
                    campaign.network_settings.target_partner_search_network,
                    campaign.geo_target_type_setting.positive_geo_target_type,
                    campaign.geo_target_type_setting.negative_geo_target_type
                FROM campaign
                WHERE campaign.id = {campaign_id}
            """
            response = service.search(customer_id=customer_id, query=query)
            for row in response:
                c = row.campaign
                return {
                    "id": str(c.id),
                    "name": c.name,
                    "status": c.status.name if hasattr(c.status, "name") else str(c.status),
                    "channel_type": str(c.advertising_channel_type),
                    "bidding_strategy_type": str(c.bidding_strategy_type),
                    "budget_amount_micros": row.campaign_budget.amount_micros if row.campaign_budget else None,
                    "start_date": c.start_date,
                    "end_date": c.end_date,
                    "network_settings": {
                        "target_google_search": c.network_settings.target_google_search,
                        "target_search_network": c.network_settings.target_search_network,
                        "target_content_network": c.network_settings.target_content_network,
                        "target_partner_search_network": c.network_settings.target_partner_search_network,
                    },
                }
            return {"error": f"Campaign {campaign_id} not found"}
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def create_search_campaign(
        customer_id: str,
        name: str,
        budget_amount_aud: float,
        account_label: str = "default",
        status: str = "PAUSED",
        target_locations: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Create a Google Ads Search campaign with a daily budget.

        Creates the campaign in PAUSED state by default — you must explicitly
        set status='ENABLED' to activate it.

        Args:
            budget_amount_aud: Daily budget in AUD (or the account's currency
                — will be converted to micros).
            target_locations: Optional list of location criterion IDs. If None,
                uses the account default (no geo targeting).
        """
        try:
            client = get_auth().get_google_ads_client(account_label)

            # 1. Create shared budget
            budget_service = client.get_service("CampaignBudgetService")
            budget_op = client.get_type("CampaignBudgetOperation")
            budget = budget_op.create
            budget.name = f"{name} Budget"
            budget.delivery_method = client.enums.BudgetDeliveryMethodEnum.STANDARD
            budget.amount_micros = int(budget_amount_aud * 1_000_000)
            budget.explicitly_shared = False
            budget_response = budget_service.mutate_campaign_budgets(
                customer_id=customer_id, operations=[budget_op]
            )
            budget_resource_name = budget_response.results[0].resource_name

            # 2. Create campaign
            campaign_service = client.get_service("CampaignService")
            campaign_op = client.get_type("CampaignOperation")
            campaign = campaign_op.create
            campaign.name = name
            campaign.advertising_channel_type = client.enums.AdvertisingChannelTypeEnum.SEARCH
            campaign.status = client.enums.CampaignStatusEnum[status]
            campaign.campaign_budget = budget_resource_name
            campaign.manual_cpc.enhanced_cpc_enabled = True
            campaign.network_settings.target_google_search = True
            campaign.network_settings.target_search_network = True
            campaign.network_settings.target_content_network = False
            campaign.network_settings.target_partner_search_network = False
            campaign_response = campaign_service.mutate_campaigns(
                customer_id=customer_id, operations=[campaign_op]
            )
            campaign_resource_name = campaign_response.results[0].resource_name
            logger.info("Created Search campaign '%s' status=%s", name, status)
            return {
                "campaign_resource_name": campaign_resource_name,
                "budget_resource_name": budget_resource_name,
                "status": status,
            }
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def pause_campaign(
        customer_id: str,
        campaign_id: str,
        account_label: str = "default",
    ) -> Dict[str, Any]:
        """Pause a campaign by setting status = PAUSED."""
        try:
            client = get_auth().get_google_ads_client(account_label)
            service = client.get_service("CampaignService")
            op = client.get_type("CampaignOperation")
            op.update.resource_name = service.campaign_path(customer_id, campaign_id)
            op.update.status = client.enums.CampaignStatusEnum.PAUSED
            client.copy_from(
                op.update_mask,
                client.get_type("FieldMask")(paths=["status"]),
            )
            response = service.mutate_campaigns(customer_id=customer_id, operations=[op])
            return {"resource_name": response.results[0].resource_name, "status": "PAUSED"}
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def enable_campaign(
        customer_id: str,
        campaign_id: str,
        account_label: str = "default",
    ) -> Dict[str, Any]:
        """Enable a campaign by setting status = ENABLED."""
        try:
            client = get_auth().get_google_ads_client(account_label)
            service = client.get_service("CampaignService")
            op = client.get_type("CampaignOperation")
            op.update.resource_name = service.campaign_path(customer_id, campaign_id)
            op.update.status = client.enums.CampaignStatusEnum.ENABLED
            client.copy_from(
                op.update_mask,
                client.get_type("FieldMask")(paths=["status"]),
            )
            response = service.mutate_campaigns(customer_id=customer_id, operations=[op])
            return {"resource_name": response.results[0].resource_name, "status": "ENABLED"}
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def update_campaign(
        customer_id: str,
        campaign_id: str,
        name: Optional[str] = None,
        end_date: Optional[str] = None,
        target_google_search: Optional[bool] = None,
        target_search_network: Optional[bool] = None,
        target_content_network: Optional[bool] = None,
        account_label: str = "default",
    ) -> Dict[str, Any]:
        """Update campaign settings.

        Args:
            name: New campaign name.
            end_date: End date in ``YYYY-MM-DD`` format (or empty string to
                clear).
            target_google_search: Show ads on Google Search.
            target_search_network: Show ads on search partner sites.
            target_content_network: Show ads on the Display Network.
        """
        try:
            client = get_auth().get_google_ads_client(account_label)
            service = client.get_service("CampaignService")
            op = client.get_type("CampaignOperation")
            op.update.resource_name = service.campaign_path(customer_id, campaign_id)
            paths: List[str] = []

            if name is not None:
                op.update.name = name
                paths.append("name")
            if end_date is not None:
                op.update.end_date = end_date
                paths.append("end_date")
            if target_google_search is not None:
                op.update.network_settings.target_google_search = target_google_search
                paths.append("network_settings.target_google_search")
            if target_search_network is not None:
                op.update.network_settings.target_search_network = target_search_network
                paths.append("network_settings.target_search_network")
            if target_content_network is not None:
                op.update.network_settings.target_content_network = target_content_network
                paths.append("network_settings.target_content_network")

            if not paths:
                return {"error": "No fields to update"}

            client.copy_from(
                op.update_mask,
                client.get_type("FieldMask")(paths=paths),
            )
            response = service.mutate_campaigns(customer_id=customer_id, operations=[op])
            logger.info("Updated campaign %s fields=%s", campaign_id, paths)
            return {"resource_name": response.results[0].resource_name, "updated_fields": paths}
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def remove_campaign(
        customer_id: str,
        campaign_id: str,
        account_label: str = "default",
    ) -> Dict[str, Any]:
        """Remove (delete) a campaign. Sets status to REMOVED."""
        try:
            client = get_auth().get_google_ads_client(account_label)
            service = client.get_service("CampaignService")
            op = client.get_type("CampaignOperation")
            op.remove = service.campaign_path(customer_id, campaign_id)
            response = service.mutate_campaigns(customer_id=customer_id, operations=[op])
            logger.info("Removed campaign %s", campaign_id)
            return {"removed": response.results[0].resource_name}
        except Exception as exc:
            raise wrap_http_error(exc)
