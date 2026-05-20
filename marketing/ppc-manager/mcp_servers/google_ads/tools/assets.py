"""Google Ads asset/extension management tools."""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

from mcp_servers.common.errors import wrap_http_error
from mcp_servers.common.logger import get_server_logger

logger = get_server_logger("ppc-google-ads.assets")


def register(mcp, get_auth: Callable[[], Any]) -> None:
    @mcp.tool()
    def list_assets(
        customer_id: str,
        asset_type: Optional[str] = None,
        account_label: str = "default",
    ) -> Dict[str, Any]:
        """List assets on the account, optionally filtered by type.

        Args:
            asset_type: Optional filter — ``SITELINK``, ``CALLOUT``,
                ``STRUCTURED_SNIPPET``, ``CALL``, ``IMAGE``, ``LEAD_FORM``,
                ``PROMOTION``, ``PRICE``, etc.
        """
        try:
            client = get_auth().get_google_ads_client(account_label)
            service = client.get_service("GoogleAdsService")
            where = (
                f"WHERE asset.type = '{asset_type}'" if asset_type else ""
            )
            query = f"""
                SELECT
                    asset.id,
                    asset.name,
                    asset.type,
                    asset.resource_name,
                    asset.final_urls
                FROM asset
                {where}
                LIMIT 500
            """
            response = service.search(customer_id=customer_id, query=query)
            assets: List[Dict[str, Any]] = []
            for row in response:
                a = row.asset
                assets.append(
                    {
                        "id": str(a.id),
                        "name": a.name,
                        "type": str(a.type_),
                        "resource_name": a.resource_name,
                        "final_urls": list(a.final_urls) if a.final_urls else [],
                    }
                )
            return {"count": len(assets), "assets": assets}
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def create_sitelink_asset(
        customer_id: str,
        link_text: str,
        final_url: str,
        description1: str = "",
        description2: str = "",
        account_label: str = "default",
    ) -> Dict[str, Any]:
        """Create a sitelink asset (extension).

        Args:
            link_text: Anchor text for the sitelink (max 25 chars).
            final_url: Landing page URL.
            description1: Optional first description line (max 35 chars).
            description2: Optional second description line (max 35 chars).
        """
        try:
            client = get_auth().get_google_ads_client(account_label)
            service = client.get_service("AssetService")
            op = client.get_type("AssetOperation")
            asset = op.create
            asset.sitelink_asset.link_text = link_text
            asset.sitelink_asset.description1 = description1
            asset.sitelink_asset.description2 = description2
            asset.final_urls.append(final_url)

            response = service.mutate_assets(
                customer_id=customer_id, operations=[op]
            )
            logger.info("Created sitelink asset '%s'", link_text)
            return {"resource_name": response.results[0].resource_name}
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def create_callout_asset(
        customer_id: str,
        callout_text: str,
        account_label: str = "default",
    ) -> Dict[str, Any]:
        """Create a callout asset (extension).

        Args:
            callout_text: Callout text (max 25 chars).
        """
        try:
            client = get_auth().get_google_ads_client(account_label)
            service = client.get_service("AssetService")
            op = client.get_type("AssetOperation")
            asset = op.create
            asset.callout_asset.callout_text = callout_text

            response = service.mutate_assets(
                customer_id=customer_id, operations=[op]
            )
            logger.info("Created callout asset '%s'", callout_text)
            return {"resource_name": response.results[0].resource_name}
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def create_structured_snippet_asset(
        customer_id: str,
        header: str,
        values: List[str],
        account_label: str = "default",
    ) -> Dict[str, Any]:
        """Create a structured snippet asset (extension).

        Args:
            header: Snippet header — must be a predefined header like
                ``Amenities``, ``Brands``, ``Courses``, ``Degree programs``,
                ``Destinations``, ``Featured hotels``, ``Insurance coverage``,
                ``Models``, ``Neighbourhoods``, ``Service catalogue``,
                ``Shows``, ``Styles``, ``Types``.
            values: List of snippet values (3-10 items, max 25 chars each).
        """
        try:
            client = get_auth().get_google_ads_client(account_label)
            service = client.get_service("AssetService")
            op = client.get_type("AssetOperation")
            asset = op.create
            asset.structured_snippet_asset.header = header
            for v in values:
                asset.structured_snippet_asset.values.append(v)

            response = service.mutate_assets(
                customer_id=customer_id, operations=[op]
            )
            logger.info("Created structured snippet asset header='%s'", header)
            return {"resource_name": response.results[0].resource_name}
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def create_call_asset(
        customer_id: str,
        phone_number: str,
        country_code: str = "AU",
        account_label: str = "default",
    ) -> Dict[str, Any]:
        """Create a call asset (phone extension).

        Args:
            phone_number: Phone number string (e.g. ``+61 2 1234 5678``).
            country_code: Two-letter country code (default ``AU``).
        """
        try:
            client = get_auth().get_google_ads_client(account_label)
            service = client.get_service("AssetService")
            op = client.get_type("AssetOperation")
            asset = op.create
            asset.call_asset.phone_number = phone_number
            asset.call_asset.country_code = country_code

            response = service.mutate_assets(
                customer_id=customer_id, operations=[op]
            )
            logger.info("Created call asset '%s'", phone_number)
            return {"resource_name": response.results[0].resource_name}
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def create_image_asset(
        customer_id: str,
        image_url: str,
        name: str,
        account_label: str = "default",
    ) -> Dict[str, Any]:
        """Create an image asset by downloading from a URL.

        Args:
            image_url: Public URL of the image to download.
            name: A descriptive name for the image asset.
        """
        try:
            import httpx

            client = get_auth().get_google_ads_client(account_label)
            service = client.get_service("AssetService")

            img_response = httpx.get(image_url, follow_redirects=True, timeout=30)
            img_response.raise_for_status()
            image_bytes = img_response.content

            op = client.get_type("AssetOperation")
            asset = op.create
            asset.name = name
            asset.type_ = client.enums.AssetTypeEnum.IMAGE
            asset.image_asset.data = image_bytes
            asset.image_asset.file_size = len(image_bytes)
            asset.image_asset.mime_type = client.enums.MimeTypeEnum.IMAGE_JPEG

            response = service.mutate_assets(
                customer_id=customer_id, operations=[op]
            )
            logger.info("Created image asset '%s' from %s", name, image_url)
            return {"resource_name": response.results[0].resource_name}
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def link_asset_to_campaign(
        customer_id: str,
        campaign_id: str,
        asset_resource_name: str,
        field_type: str,
        account_label: str = "default",
    ) -> Dict[str, Any]:
        """Link an asset to a campaign.

        Args:
            asset_resource_name: Full resource name of the asset
                (e.g. ``customers/123/assets/456``).
            field_type: Asset field type — ``SITELINK``, ``CALLOUT``,
                ``STRUCTURED_SNIPPET``, ``CALL``, ``MOBILE_APP``,
                ``HOTEL_CALLOUT``, ``PROMOTION``, ``PRICE``, ``IMAGE``, etc.
        """
        try:
            client = get_auth().get_google_ads_client(account_label)
            service = client.get_service("CampaignAssetService")
            campaign_service = client.get_service("CampaignService")
            op = client.get_type("CampaignAssetOperation")
            ca = op.create
            ca.campaign = campaign_service.campaign_path(customer_id, campaign_id)
            ca.asset = asset_resource_name
            ca.field_type = client.enums.AssetFieldTypeEnum[field_type.upper()]

            response = service.mutate_campaign_assets(
                customer_id=customer_id, operations=[op]
            )
            logger.info(
                "Linked asset %s to campaign %s as %s",
                asset_resource_name,
                campaign_id,
                field_type,
            )
            return {"resource_name": response.results[0].resource_name}
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def link_asset_to_ad_group(
        customer_id: str,
        ad_group_id: str,
        asset_resource_name: str,
        field_type: str,
        account_label: str = "default",
    ) -> Dict[str, Any]:
        """Link an asset to an ad group.

        Args:
            asset_resource_name: Full resource name of the asset.
            field_type: Asset field type — ``SITELINK``, ``CALLOUT``,
                ``STRUCTURED_SNIPPET``, ``CALL``, etc.
        """
        try:
            client = get_auth().get_google_ads_client(account_label)
            service = client.get_service("AdGroupAssetService")
            ad_group_service = client.get_service("AdGroupService")
            op = client.get_type("AdGroupAssetOperation")
            aga = op.create
            aga.ad_group = ad_group_service.ad_group_path(
                customer_id, ad_group_id
            )
            aga.asset = asset_resource_name
            aga.field_type = client.enums.AssetFieldTypeEnum[field_type.upper()]

            response = service.mutate_ad_group_assets(
                customer_id=customer_id, operations=[op]
            )
            return {"resource_name": response.results[0].resource_name}
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def remove_asset_link(
        customer_id: str,
        asset_link_resource_name: str,
        level: str = "campaign",
        account_label: str = "default",
    ) -> Dict[str, Any]:
        """Remove an asset link from a campaign or ad group.

        Args:
            asset_link_resource_name: Full resource name of the campaign-asset
                or ad-group-asset link to remove.
            level: ``campaign`` or ``ad_group``.
        """
        try:
            client = get_auth().get_google_ads_client(account_label)
            if level == "campaign":
                service = client.get_service("CampaignAssetService")
                op = client.get_type("CampaignAssetOperation")
                op.remove = asset_link_resource_name
                response = service.mutate_campaign_assets(
                    customer_id=customer_id, operations=[op]
                )
            else:
                service = client.get_service("AdGroupAssetService")
                op = client.get_type("AdGroupAssetOperation")
                op.remove = asset_link_resource_name
                response = service.mutate_ad_group_assets(
                    customer_id=customer_id, operations=[op]
                )
            return {"removed": response.results[0].resource_name}
        except Exception as exc:
            raise wrap_http_error(exc)
