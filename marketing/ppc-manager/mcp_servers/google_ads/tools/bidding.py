"""Google Ads bidding strategy management tools."""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

from mcp_servers.common.errors import wrap_http_error
from mcp_servers.common.logger import get_server_logger

logger = get_server_logger("ppc-google-ads.bidding")


def register(mcp, get_auth: Callable[[], Any]) -> None:
    @mcp.tool()
    def list_bidding_strategies(
        customer_id: str,
        account_label: str = "default",
    ) -> Dict[str, Any]:
        """List all portfolio bidding strategies on an account."""
        try:
            client = get_auth().get_google_ads_client(account_label)
            service = client.get_service("GoogleAdsService")
            query = """
                SELECT
                    bidding_strategy.id,
                    bidding_strategy.name,
                    bidding_strategy.type,
                    bidding_strategy.status,
                    bidding_strategy.campaign_count,
                    bidding_strategy.resource_name
                FROM bidding_strategy
                ORDER BY bidding_strategy.name
                LIMIT 200
            """
            response = service.search(customer_id=customer_id, query=query)
            strategies: List[Dict[str, Any]] = []
            for row in response:
                bs = row.bidding_strategy
                strategies.append(
                    {
                        "id": str(bs.id),
                        "name": bs.name,
                        "type": str(bs.type_),
                        "status": str(bs.status),
                        "campaign_count": bs.campaign_count,
                        "resource_name": bs.resource_name,
                    }
                )
            return {"count": len(strategies), "strategies": strategies}
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def create_bidding_strategy(
        customer_id: str,
        name: str,
        strategy_type: str,
        target_cpa_aud: Optional[float] = None,
        target_roas: Optional[float] = None,
        account_label: str = "default",
    ) -> Dict[str, Any]:
        """Create a portfolio bidding strategy.

        Args:
            strategy_type: One of ``MAXIMIZE_CONVERSIONS``,
                ``MAXIMIZE_CONVERSION_VALUE``, ``TARGET_CPA``, ``TARGET_ROAS``,
                ``TARGET_SPEND`` (Maximize Clicks),
                ``TARGET_IMPRESSION_SHARE``.
            target_cpa_aud: Target CPA in AUD (required for TARGET_CPA).
            target_roas: Target ROAS as a decimal (e.g. 4.0 = 400% ROAS;
                required for TARGET_ROAS).
        """
        try:
            client = get_auth().get_google_ads_client(account_label)
            service = client.get_service("BiddingStrategyService")
            op = client.get_type("BiddingStrategyOperation")
            strategy = op.create
            strategy.name = name

            stype = strategy_type.upper()
            if stype == "TARGET_CPA":
                strategy.target_cpa.target_cpa_micros = int(
                    (target_cpa_aud or 10.0) * 1_000_000
                )
            elif stype == "TARGET_ROAS":
                strategy.target_roas.target_roas = target_roas or 4.0
            elif stype == "MAXIMIZE_CONVERSIONS":
                strategy.maximize_conversions.target_cpa_micros = (
                    int(target_cpa_aud * 1_000_000) if target_cpa_aud else 0
                )
            elif stype == "MAXIMIZE_CONVERSION_VALUE":
                strategy.maximize_conversion_value.target_roas = (
                    target_roas if target_roas else 0.0
                )
            elif stype == "TARGET_SPEND":
                strategy.target_spend.cpc_bid_ceiling_micros = 0
            elif stype == "TARGET_IMPRESSION_SHARE":
                strategy.target_impression_share.location = (
                    client.enums.TargetImpressionShareLocationEnum.ANYWHERE_ON_PAGE
                )
                strategy.target_impression_share.location_fraction_micros = 500_000
            else:
                return {"error": f"Unknown strategy type: {strategy_type}"}

            response = service.mutate_bidding_strategies(
                customer_id=customer_id, operations=[op]
            )
            logger.info("Created bidding strategy '%s' type=%s", name, stype)
            return {"resource_name": response.results[0].resource_name}
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def set_campaign_bidding_strategy(
        customer_id: str,
        campaign_id: str,
        bidding_strategy_id: Optional[str] = None,
        strategy_type: Optional[str] = None,
        target_cpa_aud: Optional[float] = None,
        target_roas: Optional[float] = None,
        account_label: str = "default",
    ) -> Dict[str, Any]:
        """Set the bidding strategy on a campaign.

        Either provide ``bidding_strategy_id`` to use a portfolio strategy, or
        ``strategy_type`` to set a standard (campaign-level) strategy.

        Args:
            bidding_strategy_id: ID of an existing portfolio bidding strategy.
            strategy_type: Standard strategy — ``MAXIMIZE_CONVERSIONS``,
                ``MAXIMIZE_CONVERSION_VALUE``, ``TARGET_CPA``, ``TARGET_ROAS``,
                ``MAXIMIZE_CLICKS``, ``MANUAL_CPC``.
            target_cpa_aud: Target CPA in AUD (for TARGET_CPA or
                MAXIMIZE_CONVERSIONS with a target).
            target_roas: Target ROAS decimal (for TARGET_ROAS or
                MAXIMIZE_CONVERSION_VALUE with a target).
        """
        try:
            client = get_auth().get_google_ads_client(account_label)
            service = client.get_service("CampaignService")
            op = client.get_type("CampaignOperation")
            op.update.resource_name = service.campaign_path(
                customer_id, campaign_id
            )
            paths = []

            if bidding_strategy_id:
                bs_service = client.get_service("BiddingStrategyService")
                op.update.bidding_strategy = bs_service.bidding_strategy_path(
                    customer_id, bidding_strategy_id
                )
                paths.append("bidding_strategy")
            elif strategy_type:
                stype = strategy_type.upper()
                if stype == "MAXIMIZE_CONVERSIONS":
                    op.update.maximize_conversions.target_cpa_micros = (
                        int(target_cpa_aud * 1_000_000) if target_cpa_aud else 0
                    )
                    paths.append("maximize_conversions")
                elif stype == "MAXIMIZE_CONVERSION_VALUE":
                    op.update.maximize_conversion_value.target_roas = (
                        target_roas if target_roas else 0.0
                    )
                    paths.append("maximize_conversion_value")
                elif stype in ("TARGET_CPA", "TARGET_ROAS"):
                    return {
                        "error": f"{stype} is a portfolio-only strategy. "
                        "Create it with create_bidding_strategy first, "
                        "then pass the bidding_strategy_id here."
                    }
                elif stype == "MAXIMIZE_CLICKS":
                    op.update.target_spend.cpc_bid_ceiling_micros = 0
                    paths.append("target_spend")
                elif stype == "MANUAL_CPC":
                    op.update.manual_cpc.enhanced_cpc_enabled = True
                    paths.append("manual_cpc")
                else:
                    return {"error": f"Unknown strategy_type: {strategy_type}"}
            else:
                return {
                    "error": "Provide either bidding_strategy_id or strategy_type"
                }

            client.copy_from(
                op.update_mask,
                client.get_type("FieldMask")(paths=paths),
            )
            response = service.mutate_campaigns(
                customer_id=customer_id, operations=[op]
            )
            return {"resource_name": response.results[0].resource_name}
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def get_bidding_strategy(
        customer_id: str,
        bidding_strategy_id: str,
        account_label: str = "default",
    ) -> Dict[str, Any]:
        """Get details for a portfolio bidding strategy."""
        try:
            client = get_auth().get_google_ads_client(account_label)
            service = client.get_service("GoogleAdsService")
            query = f"""
                SELECT
                    bidding_strategy.id,
                    bidding_strategy.name,
                    bidding_strategy.type,
                    bidding_strategy.status,
                    bidding_strategy.campaign_count,
                    bidding_strategy.resource_name
                FROM bidding_strategy
                WHERE bidding_strategy.id = {bidding_strategy_id}
            """
            response = service.search(customer_id=customer_id, query=query)
            for row in response:
                bs = row.bidding_strategy
                return {
                    "id": str(bs.id),
                    "name": bs.name,
                    "type": str(bs.type_),
                    "status": str(bs.status),
                    "campaign_count": bs.campaign_count,
                    "resource_name": bs.resource_name,
                }
            return {"error": f"Bidding strategy {bidding_strategy_id} not found"}
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def remove_bidding_strategy(
        customer_id: str,
        bidding_strategy_id: str,
        account_label: str = "default",
    ) -> Dict[str, Any]:
        """Delete a portfolio bidding strategy."""
        try:
            client = get_auth().get_google_ads_client(account_label)
            service = client.get_service("BiddingStrategyService")
            op = client.get_type("BiddingStrategyOperation")
            op.remove = service.bidding_strategy_path(
                customer_id, bidding_strategy_id
            )
            response = service.mutate_bidding_strategies(
                customer_id=customer_id, operations=[op]
            )
            return {"removed": response.results[0].resource_name}
        except Exception as exc:
            raise wrap_http_error(exc)
