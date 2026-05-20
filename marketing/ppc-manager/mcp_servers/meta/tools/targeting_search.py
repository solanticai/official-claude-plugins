"""Meta targeting search/browse tools for audience discovery."""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

from mcp_servers.common.errors import wrap_http_error
from mcp_servers.common.logger import get_server_logger

logger = get_server_logger("ppc-meta.targeting_search")


def register(mcp, get_auth: Callable[[], Any]) -> None:
    @mcp.tool()
    def search_interests(
        ad_account_id: str,
        query: str,
        limit: int = 25,
        account_label: str = "default",
    ) -> Dict[str, Any]:
        """Search for targetable interests by keyword.

        Returns interest IDs and names that can be used in ad set targeting
        under ``targeting.interests``.

        Args:
            query: Search term (e.g. "software", "technology").
        """
        try:
            from facebook_business.adobjects.targetingsearch import TargetingSearch

            get_auth().get_meta_api_init(account_label)
            results = TargetingSearch.search(params={
                "q": query,
                "type": "adinterest",
                "limit": limit,
            })
            interests = []
            for r in results:
                d = dict(r)
                interests.append({
                    "id": d.get("id"),
                    "name": d.get("name"),
                    "audience_size_lower_bound": d.get("audience_size_lower_bound"),
                    "audience_size_upper_bound": d.get("audience_size_upper_bound"),
                    "path": d.get("path"),
                    "description": d.get("description"),
                    "topic": d.get("topic"),
                })
            return {"query": query, "count": len(interests), "interests": interests}
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def search_behaviors(
        ad_account_id: str,
        query: str,
        limit: int = 25,
        account_label: str = "default",
    ) -> Dict[str, Any]:
        """Search for targetable behaviors by keyword.

        Returns behavior IDs for use in ``targeting.behaviors``.
        """
        try:
            from facebook_business.adobjects.targetingsearch import TargetingSearch

            get_auth().get_meta_api_init(account_label)
            results = TargetingSearch.search(params={
                "q": query,
                "type": "adTargetingCategory",
                "class": "behaviors",
                "limit": limit,
            })
            behaviors = []
            for r in results:
                d = dict(r)
                behaviors.append({
                    "id": d.get("id"),
                    "name": d.get("name"),
                    "audience_size_lower_bound": d.get("audience_size_lower_bound"),
                    "audience_size_upper_bound": d.get("audience_size_upper_bound"),
                    "path": d.get("path"),
                    "description": d.get("description"),
                })
            return {"query": query, "count": len(behaviors), "behaviors": behaviors}
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def search_demographics(
        ad_account_id: str,
        query: str,
        limit: int = 25,
        account_label: str = "default",
    ) -> Dict[str, Any]:
        """Search for targetable demographics by keyword.

        Returns demographic targeting IDs for use in ad set targeting.
        """
        try:
            from facebook_business.adobjects.targetingsearch import TargetingSearch

            get_auth().get_meta_api_init(account_label)
            results = TargetingSearch.search(params={
                "q": query,
                "type": "adTargetingCategory",
                "class": "demographics",
                "limit": limit,
            })
            demographics = []
            for r in results:
                d = dict(r)
                demographics.append({
                    "id": d.get("id"),
                    "name": d.get("name"),
                    "audience_size_lower_bound": d.get("audience_size_lower_bound"),
                    "audience_size_upper_bound": d.get("audience_size_upper_bound"),
                    "path": d.get("path"),
                })
            return {"query": query, "count": len(demographics), "demographics": demographics}
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def search_locations(
        query: str,
        location_type: str = "adgeolocation",
        limit: int = 25,
        account_label: str = "default",
    ) -> Dict[str, Any]:
        """Search for targetable locations by name.

        Returns location keys for use in ``targeting.geo_locations``.

        Args:
            query: Location name (e.g. "Sydney", "California").
            location_type: ``adgeolocation`` (default), ``adgeolocationmeta``,
                ``adradiussuggestion``.
        """
        try:
            from facebook_business.adobjects.targetingsearch import TargetingSearch

            get_auth().get_meta_api_init(account_label)
            results = TargetingSearch.search(params={
                "q": query,
                "type": location_type,
                "limit": limit,
            })
            locations = []
            for r in results:
                d = dict(r)
                locations.append({
                    "key": d.get("key"),
                    "name": d.get("name"),
                    "type": d.get("type"),
                    "country_code": d.get("country_code"),
                    "country_name": d.get("country_name"),
                    "region": d.get("region"),
                    "supports_region": d.get("supports_region"),
                    "supports_city": d.get("supports_city"),
                })
            return {"query": query, "count": len(locations), "locations": locations}
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def browse_targeting(
        ad_account_id: str,
        account_label: str = "default",
    ) -> Dict[str, Any]:
        """Browse all available targeting categories for an ad account.

        Returns the full targeting taxonomy (interests, behaviours,
        demographics, life events, etc.) organised by category.
        """
        try:
            from facebook_business.adobjects.adaccount import AdAccount

            get_auth().get_meta_api_init(account_label)
            if not ad_account_id.startswith("act_"):
                ad_account_id = f"act_{ad_account_id}"
            account = AdAccount(ad_account_id)
            browse = account.get_targeting_browse(
                params={"limit": 500}
            )
            categories = [dict(b) for b in browse]
            return {"count": len(categories), "categories": categories}
        except Exception as exc:
            raise wrap_http_error(exc)
