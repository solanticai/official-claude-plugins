"""Google Ads ad group CRUD tools."""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

from mcp_servers.common.errors import wrap_http_error
from mcp_servers.common.logger import get_server_logger

logger = get_server_logger("ppc-google-ads.ad_groups")


def register(mcp, get_auth: Callable[[], Any]) -> None:
    @mcp.tool()
    def list_ad_groups(
        customer_id: str,
        campaign_id: Optional[str] = None,
        account_label: str = "default",
    ) -> Dict[str, Any]:
        """List ad groups on a customer account, optionally filtered by campaign."""
        try:
            client = get_auth().get_google_ads_client(account_label)
            service = client.get_service("GoogleAdsService")
            where = f"WHERE campaign.id = {campaign_id}" if campaign_id else ""
            query = f"""
                SELECT
                    ad_group.id, ad_group.name, ad_group.status,
                    ad_group.type, ad_group.cpc_bid_micros,
                    campaign.id, campaign.name
                FROM ad_group
                {where}
                ORDER BY ad_group.name
                LIMIT 1000
            """
            response = service.search(customer_id=customer_id, query=query)
            groups: List[Dict[str, Any]] = []
            for row in response:
                groups.append(
                    {
                        "id": str(row.ad_group.id),
                        "name": row.ad_group.name,
                        "status": str(row.ad_group.status),
                        "type": str(row.ad_group.type),
                        "cpc_bid_micros": row.ad_group.cpc_bid_micros,
                        "campaign_id": str(row.campaign.id),
                        "campaign_name": row.campaign.name,
                    }
                )
            return {
                "customer_id": customer_id,
                "count": len(groups),
                "ad_groups": groups,
            }
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def create_ad_group(
        customer_id: str,
        campaign_id: str,
        name: str,
        cpc_bid_aud: float = 1.00,
        status: str = "ENABLED",
        account_label: str = "default",
    ) -> Dict[str, Any]:
        """Create an ad group inside a campaign.

        Args:
            cpc_bid_aud: Default CPC bid in AUD (converted to micros).
            status: `ENABLED` or `PAUSED`.
        """
        try:
            client = get_auth().get_google_ads_client(account_label)
            service = client.get_service("AdGroupService")
            op = client.get_type("AdGroupOperation")
            ad_group = op.create
            ad_group.name = name
            ad_group.status = client.enums.AdGroupStatusEnum[status]
            ad_group.campaign = client.get_service("CampaignService").campaign_path(
                customer_id, campaign_id
            )
            ad_group.type_ = client.enums.AdGroupTypeEnum.SEARCH_STANDARD
            ad_group.cpc_bid_micros = int(cpc_bid_aud * 1_000_000)
            response = service.mutate_ad_groups(
                customer_id=customer_id, operations=[op]
            )
            logger.info("Created ad group '%s' in campaign %s", name, campaign_id)
            return {"resource_name": response.results[0].resource_name, "name": name}
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def update_ad_group(
        customer_id: str,
        ad_group_id: str,
        name: Optional[str] = None,
        cpc_bid_aud: Optional[float] = None,
        account_label: str = "default",
    ) -> Dict[str, Any]:
        """Update an ad group's name or default CPC bid.

        Args:
            cpc_bid_aud: New default CPC bid in AUD.
        """
        try:
            client = get_auth().get_google_ads_client(account_label)
            service = client.get_service("AdGroupService")
            op = client.get_type("AdGroupOperation")
            op.update.resource_name = service.ad_group_path(customer_id, ad_group_id)
            paths: List[str] = []
            if name is not None:
                op.update.name = name
                paths.append("name")
            if cpc_bid_aud is not None:
                op.update.cpc_bid_micros = int(cpc_bid_aud * 1_000_000)
                paths.append("cpc_bid_micros")
            if not paths:
                return {"error": "No fields to update"}
            client.copy_from(
                op.update_mask,
                client.get_type("FieldMask")(paths=paths),
            )
            response = service.mutate_ad_groups(customer_id=customer_id, operations=[op])
            return {"resource_name": response.results[0].resource_name, "updated_fields": paths}
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def pause_ad_group(
        customer_id: str,
        ad_group_id: str,
        account_label: str = "default",
    ) -> Dict[str, Any]:
        """Pause an ad group by setting status = PAUSED."""
        try:
            client = get_auth().get_google_ads_client(account_label)
            service = client.get_service("AdGroupService")
            op = client.get_type("AdGroupOperation")
            op.update.resource_name = service.ad_group_path(customer_id, ad_group_id)
            op.update.status = client.enums.AdGroupStatusEnum.PAUSED
            client.copy_from(
                op.update_mask,
                client.get_type("FieldMask")(paths=["status"]),
            )
            response = service.mutate_ad_groups(customer_id=customer_id, operations=[op])
            return {"resource_name": response.results[0].resource_name, "status": "PAUSED"}
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def enable_ad_group(
        customer_id: str,
        ad_group_id: str,
        account_label: str = "default",
    ) -> Dict[str, Any]:
        """Enable an ad group by setting status = ENABLED."""
        try:
            client = get_auth().get_google_ads_client(account_label)
            service = client.get_service("AdGroupService")
            op = client.get_type("AdGroupOperation")
            op.update.resource_name = service.ad_group_path(customer_id, ad_group_id)
            op.update.status = client.enums.AdGroupStatusEnum.ENABLED
            client.copy_from(
                op.update_mask,
                client.get_type("FieldMask")(paths=["status"]),
            )
            response = service.mutate_ad_groups(customer_id=customer_id, operations=[op])
            return {"resource_name": response.results[0].resource_name, "status": "ENABLED"}
        except Exception as exc:
            raise wrap_http_error(exc)
