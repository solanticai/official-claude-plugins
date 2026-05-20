"""Meta ad (creative pairing) tools."""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

from mcp_servers.common.errors import wrap_http_error
from mcp_servers.common.logger import get_server_logger

logger = get_server_logger("ppc-meta.ads")


def register(mcp, get_auth: Callable[[], Any]) -> None:
    @mcp.tool()
    def list_ads(
        ad_set_id: str, account_label: str = "default"
    ) -> Dict[str, Any]:
        """List ads in a Meta ad set."""
        try:
            from facebook_business.adobjects.adset import AdSet

            get_auth().get_meta_api_init(account_label)
            ad_set = AdSet(ad_set_id)
            ads = ad_set.get_ads(
                fields=["id", "name", "status", "creative", "effective_status"],
                params={"limit": 100},
            )
            return {"count": len(ads), "ads": [dict(a) for a in ads]}
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def create_ad(
        ad_account_id: str,
        ad_set_id: str,
        name: str,
        creative_id: str,
        status: str = "PAUSED",
        account_label: str = "default",
    ) -> Dict[str, Any]:
        """Create a Meta ad referencing an existing creative."""
        try:
            from facebook_business.adobjects.adaccount import AdAccount
            from facebook_business.adobjects.ad import Ad

            get_auth().get_meta_api_init(account_label)
            if not ad_account_id.startswith("act_"):
                ad_account_id = f"act_{ad_account_id}"
            account = AdAccount(ad_account_id)
            params = {
                Ad.Field.name: name,
                Ad.Field.adset_id: ad_set_id,
                Ad.Field.creative: {"creative_id": creative_id},
                Ad.Field.status: status,
            }
            ad = account.create_ad(params=params)
            logger.info("Created Meta ad '%s'", name)
            return {"id": ad.get("id"), "name": name, "status": status}
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def create_creative(
        ad_account_id: str,
        name: str,
        page_id: str,
        message: str,
        link_url: str,
        image_hash: Optional[str] = None,
        image_url: Optional[str] = None,
        headline: Optional[str] = None,
        description: Optional[str] = None,
        call_to_action_type: str = "SHOP_NOW",
        account_label: str = "default",
    ) -> Dict[str, Any]:
        """Create a Meta ad creative (single-image link ad).

        Either ``image_hash`` (pre-uploaded) or ``image_url`` (Meta fetches)
        must be provided.
        """
        try:
            from facebook_business.adobjects.adaccount import AdAccount
            from facebook_business.adobjects.adcreative import AdCreative

            get_auth().get_meta_api_init(account_label)
            if not ad_account_id.startswith("act_"):
                ad_account_id = f"act_{ad_account_id}"
            account = AdAccount(ad_account_id)

            link_data: Dict[str, Any] = {
                "link": link_url,
                "message": message,
                "call_to_action": {"type": call_to_action_type, "value": {"link": link_url}},
            }
            if headline:
                link_data["name"] = headline
            if description:
                link_data["description"] = description
            if image_hash:
                link_data["image_hash"] = image_hash
            elif image_url:
                link_data["picture"] = image_url
            else:
                return {"error": "Either image_hash or image_url is required"}

            params = {
                AdCreative.Field.name: name,
                AdCreative.Field.object_story_spec: {
                    "page_id": page_id,
                    "link_data": link_data,
                },
            }
            creative = account.create_ad_creative(params=params)
            logger.info("Created Meta creative '%s'", name)
            return {"id": creative.get("id"), "name": name}
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def get_ad(
        ad_id: str, account_label: str = "default"
    ) -> Dict[str, Any]:
        """Get full details for a Meta ad."""
        try:
            from facebook_business.adobjects.ad import Ad

            get_auth().get_meta_api_init(account_label)
            ad = Ad(ad_id)
            data = ad.api_get(
                fields=[
                    "id",
                    "name",
                    "status",
                    "configured_status",
                    "effective_status",
                    "adset_id",
                    "campaign_id",
                    "creative",
                    "ad_review_feedback",
                    "issues_info",
                    "created_time",
                    "updated_time",
                ]
            )
            return dict(data)
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def update_ad(
        ad_id: str,
        name: Optional[str] = None,
        creative_id: Optional[str] = None,
        account_label: str = "default",
    ) -> Dict[str, Any]:
        """Update a Meta ad.

        Args:
            name: New ad name.
            creative_id: ID of a new creative to use.
        """
        try:
            from facebook_business.adobjects.ad import Ad

            get_auth().get_meta_api_init(account_label)
            ad = Ad(ad_id)
            params: Dict[str, Any] = {}
            if name is not None:
                params[Ad.Field.name] = name
            if creative_id is not None:
                params[Ad.Field.creative] = {"creative_id": creative_id}
            if not params:
                return {"error": "No fields to update"}
            ad.api_update(params=params)
            return {"id": ad_id, "updated_fields": list(params.keys())}
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def pause_ad(
        ad_id: str, account_label: str = "default"
    ) -> Dict[str, Any]:
        """Pause a Meta ad."""
        try:
            from facebook_business.adobjects.ad import Ad

            get_auth().get_meta_api_init(account_label)
            ad = Ad(ad_id)
            ad.api_update(params={Ad.Field.status: "PAUSED"})
            return {"id": ad_id, "status": "PAUSED"}
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def enable_ad(
        ad_id: str, account_label: str = "default"
    ) -> Dict[str, Any]:
        """Resume/enable a Meta ad."""
        try:
            from facebook_business.adobjects.ad import Ad

            get_auth().get_meta_api_init(account_label)
            ad = Ad(ad_id)
            ad.api_update(params={Ad.Field.status: "ACTIVE"})
            return {"id": ad_id, "status": "ACTIVE"}
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def archive_ad(
        ad_id: str, account_label: str = "default"
    ) -> Dict[str, Any]:
        """Archive a Meta ad."""
        try:
            from facebook_business.adobjects.ad import Ad

            get_auth().get_meta_api_init(account_label)
            ad = Ad(ad_id)
            ad.api_update(params={Ad.Field.status: "ARCHIVED"})
            return {"id": ad_id, "status": "ARCHIVED"}
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def get_ad_preview(
        ad_id: str,
        ad_format: str = "DESKTOP_FEED_STANDARD",
        account_label: str = "default",
    ) -> Dict[str, Any]:
        """Generate a preview of a Meta ad.

        Args:
            ad_format: Placement format — ``DESKTOP_FEED_STANDARD``,
                ``MOBILE_FEED_STANDARD``, ``INSTAGRAM_STANDARD``,
                ``INSTAGRAM_STORY``, ``FACEBOOK_STORY_MOBILE``,
                ``RIGHT_COLUMN_STANDARD``, ``MARKETPLACE_MOBILE``, etc.
        """
        try:
            from facebook_business.adobjects.ad import Ad

            get_auth().get_meta_api_init(account_label)
            ad = Ad(ad_id)
            previews = ad.get_previews(params={"ad_format": ad_format})
            results = [dict(p) for p in previews]
            return {"ad_id": ad_id, "ad_format": ad_format, "previews": results}
        except Exception as exc:
            raise wrap_http_error(exc)
