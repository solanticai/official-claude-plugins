"""Google Ads ad creation tools (Responsive Search Ads focus)."""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

from mcp_servers.common.errors import wrap_http_error
from mcp_servers.common.logger import get_server_logger

logger = get_server_logger("ppc-google-ads.ads")


def register(mcp, get_auth: Callable[[], Any]) -> None:
    @mcp.tool()
    def list_ads(
        customer_id: str,
        ad_group_id: Optional[str] = None,
        account_label: str = "default",
    ) -> Dict[str, Any]:
        """List ads on a customer, optionally filtered by ad group."""
        try:
            client = get_auth().get_google_ads_client(account_label)
            service = client.get_service("GoogleAdsService")
            where = f"WHERE ad_group.id = {ad_group_id}" if ad_group_id else ""
            query = f"""
                SELECT
                    ad_group_ad.ad.id,
                    ad_group_ad.ad.type,
                    ad_group_ad.ad.final_urls,
                    ad_group_ad.status,
                    ad_group.id,
                    ad_group.name,
                    campaign.id,
                    campaign.name
                FROM ad_group_ad
                {where}
                LIMIT 1000
            """
            response = service.search(customer_id=customer_id, query=query)
            ads: List[Dict[str, Any]] = []
            for row in response:
                ads.append(
                    {
                        "ad_id": str(row.ad_group_ad.ad.id),
                        "type": str(row.ad_group_ad.ad.type_),
                        "final_urls": list(row.ad_group_ad.ad.final_urls),
                        "status": str(row.ad_group_ad.status),
                        "ad_group_id": str(row.ad_group.id),
                        "ad_group_name": row.ad_group.name,
                        "campaign_id": str(row.campaign.id),
                        "campaign_name": row.campaign.name,
                    }
                )
            return {"count": len(ads), "ads": ads}
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def create_responsive_search_ad(
        customer_id: str,
        ad_group_id: str,
        final_url: str,
        headlines: List[str],
        descriptions: List[str],
        path1: str = "",
        path2: str = "",
        pinned_headlines: Optional[Dict[int, int]] = None,
        account_label: str = "default",
    ) -> Dict[str, Any]:
        """Create a Responsive Search Ad.

        Args:
            headlines: 3-15 headlines, each ≤30 chars.
            descriptions: 2-4 descriptions, each ≤90 chars.
            pinned_headlines: Optional dict mapping headline index (0-based)
                to pin position (1, 2, or 3).
        """
        try:
            if len(headlines) < 3:
                return {"error": "Responsive Search Ads need at least 3 headlines"}
            if len(descriptions) < 2:
                return {"error": "Responsive Search Ads need at least 2 descriptions"}

            client = get_auth().get_google_ads_client(account_label)
            service = client.get_service("AdGroupAdService")
            op = client.get_type("AdGroupAdOperation")
            ad_group_ad = op.create
            ad_group_ad.ad_group = client.get_service("AdGroupService").ad_group_path(
                customer_id, ad_group_id
            )
            ad_group_ad.status = client.enums.AdGroupAdStatusEnum.PAUSED

            rsa = ad_group_ad.ad.responsive_search_ad
            ad_group_ad.ad.final_urls.append(final_url)
            if path1:
                rsa.path1 = path1[:15]
            if path2:
                rsa.path2 = path2[:15]

            for i, text in enumerate(headlines[:15]):
                asset = client.get_type("AdTextAsset")
                asset.text = text[:30]
                if pinned_headlines and i in pinned_headlines:
                    asset.pinned_field = client.enums.ServedAssetFieldTypeEnum[
                        f"HEADLINE_{pinned_headlines[i]}"
                    ]
                rsa.headlines.append(asset)

            for text in descriptions[:4]:
                asset = client.get_type("AdTextAsset")
                asset.text = text[:90]
                rsa.descriptions.append(asset)

            response = service.mutate_ad_group_ads(
                customer_id=customer_id, operations=[op]
            )
            logger.info("Created RSA with %d headlines, %d descriptions", len(headlines), len(descriptions))
            return {
                "resource_name": response.results[0].resource_name,
                "headlines_count": len(headlines),
                "descriptions_count": len(descriptions),
                "status": "PAUSED",
            }
        except Exception as exc:
            raise wrap_http_error(exc)
