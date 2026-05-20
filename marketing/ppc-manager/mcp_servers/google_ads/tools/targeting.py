"""Google Ads campaign targeting tools: geo, language, schedule, device."""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

from mcp_servers.common.errors import wrap_http_error
from mcp_servers.common.logger import get_server_logger

logger = get_server_logger("ppc-google-ads.targeting")


def register(mcp, get_auth: Callable[[], Any]) -> None:
    @mcp.tool()
    def search_geo_targets(
        customer_id: str,
        query: str,
        country_code: Optional[str] = None,
        account_label: str = "default",
    ) -> Dict[str, Any]:
        """Search for geo-targeting location IDs by name.

        Returns location criterion IDs that can be used with
        ``set_campaign_geo_targets``.

        Args:
            query: Location name to search (e.g. "Sydney", "Australia").
            country_code: Optional two-letter country code to filter results
                (e.g. "AU", "US").
        """
        try:
            client = get_auth().get_google_ads_client(account_label)
            service = client.get_service("GeoTargetConstantService")
            request = client.get_type("SuggestGeoTargetConstantsRequest")
            request.locale = "en"
            request.location_names.names.append(query)
            if country_code:
                request.location_names.locale = country_code

            response = service.suggest_geo_target_constants(request=request)
            results: List[Dict[str, Any]] = []
            for suggestion in response.geo_target_constant_suggestions:
                geo = suggestion.geo_target_constant
                results.append(
                    {
                        "criterion_id": str(geo.id),
                        "name": geo.name,
                        "canonical_name": geo.canonical_name,
                        "target_type": geo.target_type,
                        "country_code": geo.country_code,
                        "resource_name": geo.resource_name,
                        "reach": suggestion.reach
                        if hasattr(suggestion, "reach")
                        else None,
                        "search_term": suggestion.search_term
                        if hasattr(suggestion, "search_term")
                        else None,
                    }
                )
            return {"query": query, "count": len(results), "locations": results}
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def set_campaign_geo_targets(
        customer_id: str,
        campaign_id: str,
        location_ids: List[str],
        negative_location_ids: Optional[List[str]] = None,
        account_label: str = "default",
    ) -> Dict[str, Any]:
        """Set geo-targeting locations on a campaign.

        Args:
            location_ids: List of location criterion IDs to target
                (e.g. ``["2036"]`` for Australia).
            negative_location_ids: Optional list of location criterion IDs to
                exclude.
        """
        try:
            client = get_auth().get_google_ads_client(account_label)
            service = client.get_service("CampaignCriterionService")
            geo_service = client.get_service("GeoTargetConstantService")
            campaign_service = client.get_service("CampaignService")
            operations = []

            for loc_id in location_ids:
                op = client.get_type("CampaignCriterionOperation")
                criterion = op.create
                criterion.campaign = campaign_service.campaign_path(
                    customer_id, campaign_id
                )
                criterion.location.geo_target_constant = (
                    geo_service.geo_target_constant_path(loc_id)
                )
                criterion.negative = False
                operations.append(op)

            for loc_id in negative_location_ids or []:
                op = client.get_type("CampaignCriterionOperation")
                criterion = op.create
                criterion.campaign = campaign_service.campaign_path(
                    customer_id, campaign_id
                )
                criterion.location.geo_target_constant = (
                    geo_service.geo_target_constant_path(loc_id)
                )
                criterion.negative = True
                operations.append(op)

            response = service.mutate_campaign_criteria(
                customer_id=customer_id, operations=operations
            )
            logger.info(
                "Set %d geo targets on campaign %s", len(operations), campaign_id
            )
            return {
                "count": len(response.results),
                "resource_names": [r.resource_name for r in response.results],
            }
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def get_campaign_geo_targets(
        customer_id: str,
        campaign_id: str,
        account_label: str = "default",
    ) -> Dict[str, Any]:
        """Get current geo-targeting locations for a campaign."""
        try:
            client = get_auth().get_google_ads_client(account_label)
            service = client.get_service("GoogleAdsService")
            query = f"""
                SELECT
                    campaign_criterion.criterion_id,
                    campaign_criterion.location.geo_target_constant,
                    campaign_criterion.negative,
                    campaign_criterion.status
                FROM campaign_criterion
                WHERE campaign.id = {campaign_id}
                  AND campaign_criterion.type = 'LOCATION'
                LIMIT 500
            """
            response = service.search(customer_id=customer_id, query=query)
            targets: List[Dict[str, Any]] = []
            for row in response:
                cc = row.campaign_criterion
                targets.append(
                    {
                        "criterion_id": str(cc.criterion_id),
                        "geo_target_constant": cc.location.geo_target_constant,
                        "negative": cc.negative,
                        "status": str(cc.status),
                    }
                )
            return {"campaign_id": campaign_id, "count": len(targets), "targets": targets}
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def set_campaign_language_targets(
        customer_id: str,
        campaign_id: str,
        language_ids: List[str],
        account_label: str = "default",
    ) -> Dict[str, Any]:
        """Set language targeting on a campaign.

        Args:
            language_ids: List of language criterion IDs
                (e.g. ``["1000"]`` for English).
        """
        try:
            client = get_auth().get_google_ads_client(account_label)
            service = client.get_service("CampaignCriterionService")
            campaign_service = client.get_service("CampaignService")
            lang_service = client.get_service("LanguageConstantService")
            operations = []

            for lang_id in language_ids:
                op = client.get_type("CampaignCriterionOperation")
                criterion = op.create
                criterion.campaign = campaign_service.campaign_path(
                    customer_id, campaign_id
                )
                criterion.language.language_constant = (
                    lang_service.language_constant_path(lang_id)
                )
                operations.append(op)

            response = service.mutate_campaign_criteria(
                customer_id=customer_id, operations=operations
            )
            return {
                "count": len(response.results),
                "resource_names": [r.resource_name for r in response.results],
            }
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def set_campaign_ad_schedule(
        customer_id: str,
        campaign_id: str,
        schedules: List[Dict[str, Any]],
        account_label: str = "default",
    ) -> Dict[str, Any]:
        """Set ad scheduling (day-parting) on a campaign.

        Args:
            schedules: List of schedule dicts, each with:
                ``day_of_week`` (``MONDAY``..``SUNDAY``),
                ``start_hour`` (0-23), ``start_minute`` (``ZERO``/``FIFTEEN``/
                ``THIRTY``/``FORTY_FIVE``),
                ``end_hour`` (0-24), ``end_minute`` (same options).
        """
        try:
            client = get_auth().get_google_ads_client(account_label)
            service = client.get_service("CampaignCriterionService")
            campaign_service = client.get_service("CampaignService")
            operations = []

            for sched in schedules:
                op = client.get_type("CampaignCriterionOperation")
                criterion = op.create
                criterion.campaign = campaign_service.campaign_path(
                    customer_id, campaign_id
                )
                ad_sched = criterion.ad_schedule
                ad_sched.day_of_week = client.enums.DayOfWeekEnum[
                    sched["day_of_week"].upper()
                ]
                ad_sched.start_hour = sched["start_hour"]
                ad_sched.start_minute = client.enums.MinuteOfHourEnum[
                    sched.get("start_minute", "ZERO").upper()
                ]
                ad_sched.end_hour = sched["end_hour"]
                ad_sched.end_minute = client.enums.MinuteOfHourEnum[
                    sched.get("end_minute", "ZERO").upper()
                ]
                operations.append(op)

            response = service.mutate_campaign_criteria(
                customer_id=customer_id, operations=operations
            )
            return {
                "count": len(response.results),
                "resource_names": [r.resource_name for r in response.results],
            }
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def set_device_bid_modifier(
        customer_id: str,
        campaign_id: str,
        device_type: str,
        bid_modifier: float,
        account_label: str = "default",
    ) -> Dict[str, Any]:
        """Set a bid modifier for a device type on a campaign.

        Args:
            device_type: ``MOBILE``, ``TABLET``, or ``DESKTOP``.
            bid_modifier: Multiplier — 1.0 = no change, 1.2 = +20%,
                0.8 = -20%, -1.0 = opt out (mobile only).
        """
        try:
            client = get_auth().get_google_ads_client(account_label)
            service = client.get_service("CampaignCriterionService")
            campaign_service = client.get_service("CampaignService")

            op = client.get_type("CampaignCriterionOperation")
            criterion = op.create
            criterion.campaign = campaign_service.campaign_path(
                customer_id, campaign_id
            )
            criterion.device.type_ = client.enums.DeviceEnum[device_type.upper()]
            criterion.bid_modifier = bid_modifier

            response = service.mutate_campaign_criteria(
                customer_id=customer_id, operations=[op]
            )
            return {
                "resource_name": response.results[0].resource_name,
                "device_type": device_type,
                "bid_modifier": bid_modifier,
            }
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def list_campaign_criteria(
        customer_id: str,
        campaign_id: str,
        criterion_type: Optional[str] = None,
        account_label: str = "default",
    ) -> Dict[str, Any]:
        """List all targeting criteria on a campaign.

        Args:
            criterion_type: Optional filter — ``LOCATION``, ``LANGUAGE``,
                ``AD_SCHEDULE``, ``DEVICE``, ``USER_LIST``, etc.
        """
        try:
            client = get_auth().get_google_ads_client(account_label)
            service = client.get_service("GoogleAdsService")
            where_type = (
                f"AND campaign_criterion.type = '{criterion_type}'"
                if criterion_type
                else ""
            )
            query = f"""
                SELECT
                    campaign_criterion.criterion_id,
                    campaign_criterion.type,
                    campaign_criterion.status,
                    campaign_criterion.negative,
                    campaign_criterion.bid_modifier,
                    campaign_criterion.location.geo_target_constant,
                    campaign_criterion.language.language_constant,
                    campaign_criterion.ad_schedule.day_of_week,
                    campaign_criterion.ad_schedule.start_hour,
                    campaign_criterion.ad_schedule.end_hour,
                    campaign_criterion.device.type
                FROM campaign_criterion
                WHERE campaign.id = {campaign_id}
                  {where_type}
                LIMIT 1000
            """
            response = service.search(customer_id=customer_id, query=query)
            criteria: List[Dict[str, Any]] = []
            for row in response:
                cc = row.campaign_criterion
                entry: Dict[str, Any] = {
                    "criterion_id": str(cc.criterion_id),
                    "type": str(cc.type_),
                    "status": str(cc.status),
                    "negative": cc.negative,
                    "bid_modifier": cc.bid_modifier if cc.bid_modifier else None,
                }
                if cc.location and cc.location.geo_target_constant:
                    entry["geo_target_constant"] = cc.location.geo_target_constant
                if cc.language and cc.language.language_constant:
                    entry["language_constant"] = cc.language.language_constant
                if cc.ad_schedule and cc.ad_schedule.day_of_week:
                    entry["ad_schedule"] = {
                        "day_of_week": str(cc.ad_schedule.day_of_week),
                        "start_hour": cc.ad_schedule.start_hour,
                        "end_hour": cc.ad_schedule.end_hour,
                    }
                if cc.device and cc.device.type_:
                    entry["device_type"] = str(cc.device.type_)
                criteria.append(entry)
            return {
                "campaign_id": campaign_id,
                "count": len(criteria),
                "criteria": criteria,
            }
        except Exception as exc:
            raise wrap_http_error(exc)
