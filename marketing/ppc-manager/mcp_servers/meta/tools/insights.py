"""Meta insights (reporting) tools."""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

from mcp_servers.common.errors import wrap_http_error
from mcp_servers.common.logger import get_server_logger

logger = get_server_logger("ppc-meta.insights")


def register(mcp, get_auth: Callable[[], Any]) -> None:
    @mcp.tool()
    def get_ad_account_insights(
        ad_account_id: str,
        fields: Optional[List[str]] = None,
        time_range: Optional[Dict[str, str]] = None,
        level: str = "campaign",
        limit: int = 100,
        account_label: str = "default",
    ) -> Dict[str, Any]:
        """Query Meta insights at account / campaign / ad_set / ad level.

        Args:
            fields: List of insight field names. Defaults to a sensible set.
            time_range: ``{"since": "YYYY-MM-DD", "until": "YYYY-MM-DD"}``;
                defaults to last 30 days.
            level: ``account``, ``campaign``, ``adset``, ``ad``.
        """
        try:
            from datetime import date, timedelta

            from facebook_business.adobjects.adaccount import AdAccount

            get_auth().get_meta_api_init(account_label)
            if not ad_account_id.startswith("act_"):
                ad_account_id = f"act_{ad_account_id}"
            account = AdAccount(ad_account_id)

            if fields is None:
                fields = [
                    "campaign_name",
                    "adset_name",
                    "ad_name",
                    "impressions",
                    "clicks",
                    "ctr",
                    "cpc",
                    "spend",
                    "reach",
                    "frequency",
                    "actions",
                    "action_values",
                    "cost_per_action_type",
                ]
            if time_range is None:
                today = date.today()
                thirty = today - timedelta(days=30)
                time_range = {"since": thirty.isoformat(), "until": today.isoformat()}

            params: Dict[str, Any] = {
                "level": level,
                "time_range": time_range,
                "limit": limit,
            }
            insights = account.get_insights(fields=fields, params=params)
            return {
                "count": len(insights),
                "level": level,
                "time_range": time_range,
                "rows": [dict(i) for i in insights],
            }
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def get_campaign_insights(
        campaign_id: str,
        fields: Optional[List[str]] = None,
        breakdowns: Optional[List[str]] = None,
        time_range: Optional[Dict[str, str]] = None,
        time_increment: Optional[str] = None,
        limit: int = 100,
        account_label: str = "default",
    ) -> Dict[str, Any]:
        """Get performance insights for a specific campaign.

        Args:
            breakdowns: Optional list — ``age``, ``gender``, ``country``,
                ``publisher_platform``, ``platform_position``,
                ``impression_device``, ``device_platform``, ``dma``,
                ``region``.
            time_increment: ``1`` (daily), ``7`` (weekly), ``monthly``,
                ``all_days``.
        """
        try:
            from datetime import date, timedelta

            from facebook_business.adobjects.campaign import Campaign

            get_auth().get_meta_api_init(account_label)
            campaign = Campaign(campaign_id)

            if fields is None:
                fields = [
                    "campaign_name",
                    "impressions",
                    "clicks",
                    "ctr",
                    "cpc",
                    "spend",
                    "reach",
                    "frequency",
                    "actions",
                    "action_values",
                    "cost_per_action_type",
                ]
            if time_range is None:
                today = date.today()
                thirty = today - timedelta(days=30)
                time_range = {"since": thirty.isoformat(), "until": today.isoformat()}

            params: Dict[str, Any] = {
                "time_range": time_range,
                "limit": limit,
            }
            if breakdowns:
                params["breakdowns"] = breakdowns
            if time_increment:
                params["time_increment"] = time_increment

            insights = campaign.get_insights(fields=fields, params=params)
            return {
                "campaign_id": campaign_id,
                "count": len(insights),
                "time_range": time_range,
                "breakdowns": breakdowns,
                "rows": [dict(i) for i in insights],
            }
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def get_ad_set_insights(
        ad_set_id: str,
        fields: Optional[List[str]] = None,
        breakdowns: Optional[List[str]] = None,
        time_range: Optional[Dict[str, str]] = None,
        time_increment: Optional[str] = None,
        limit: int = 100,
        account_label: str = "default",
    ) -> Dict[str, Any]:
        """Get performance insights for a specific ad set.

        Args:
            breakdowns: Optional list — ``age``, ``gender``, ``country``,
                ``publisher_platform``, ``platform_position``,
                ``impression_device``, ``device_platform``.
            time_increment: ``1`` (daily), ``7`` (weekly), ``monthly``,
                ``all_days``.
        """
        try:
            from datetime import date, timedelta

            from facebook_business.adobjects.adset import AdSet

            get_auth().get_meta_api_init(account_label)
            ad_set = AdSet(ad_set_id)

            if fields is None:
                fields = [
                    "adset_name",
                    "impressions",
                    "clicks",
                    "ctr",
                    "cpc",
                    "spend",
                    "reach",
                    "frequency",
                    "actions",
                    "action_values",
                    "cost_per_action_type",
                ]
            if time_range is None:
                today = date.today()
                thirty = today - timedelta(days=30)
                time_range = {"since": thirty.isoformat(), "until": today.isoformat()}

            params: Dict[str, Any] = {
                "time_range": time_range,
                "limit": limit,
            }
            if breakdowns:
                params["breakdowns"] = breakdowns
            if time_increment:
                params["time_increment"] = time_increment

            insights = ad_set.get_insights(fields=fields, params=params)
            return {
                "ad_set_id": ad_set_id,
                "count": len(insights),
                "time_range": time_range,
                "breakdowns": breakdowns,
                "rows": [dict(i) for i in insights],
            }
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def get_ad_insights(
        ad_id: str,
        fields: Optional[List[str]] = None,
        breakdowns: Optional[List[str]] = None,
        time_range: Optional[Dict[str, str]] = None,
        time_increment: Optional[str] = None,
        limit: int = 100,
        account_label: str = "default",
    ) -> Dict[str, Any]:
        """Get performance insights for a specific ad.

        Args:
            breakdowns: Optional list — ``age``, ``gender``, ``country``,
                ``publisher_platform``, ``platform_position``,
                ``impression_device``, ``device_platform``.
            time_increment: ``1`` (daily), ``7`` (weekly), ``monthly``,
                ``all_days``.
        """
        try:
            from datetime import date, timedelta

            from facebook_business.adobjects.ad import Ad

            get_auth().get_meta_api_init(account_label)
            ad = Ad(ad_id)

            if fields is None:
                fields = [
                    "ad_name",
                    "impressions",
                    "clicks",
                    "ctr",
                    "cpc",
                    "spend",
                    "reach",
                    "frequency",
                    "actions",
                    "action_values",
                    "cost_per_action_type",
                ]
            if time_range is None:
                today = date.today()
                thirty = today - timedelta(days=30)
                time_range = {"since": thirty.isoformat(), "until": today.isoformat()}

            params: Dict[str, Any] = {
                "time_range": time_range,
                "limit": limit,
            }
            if breakdowns:
                params["breakdowns"] = breakdowns
            if time_increment:
                params["time_increment"] = time_increment

            insights = ad.get_insights(fields=fields, params=params)
            return {
                "ad_id": ad_id,
                "count": len(insights),
                "time_range": time_range,
                "breakdowns": breakdowns,
                "rows": [dict(i) for i in insights],
            }
        except Exception as exc:
            raise wrap_http_error(exc)
