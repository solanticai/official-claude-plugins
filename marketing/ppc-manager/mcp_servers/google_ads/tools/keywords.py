"""Google Ads keyword tools: list, add, generate ideas, add negatives."""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

from mcp_servers.common.errors import wrap_http_error
from mcp_servers.common.logger import get_server_logger

logger = get_server_logger("ppc-google-ads.keywords")


def register(mcp, get_auth: Callable[[], Any]) -> None:
    @mcp.tool()
    def list_keywords(
        customer_id: str,
        ad_group_id: Optional[str] = None,
        account_label: str = "default",
    ) -> Dict[str, Any]:
        """List keywords on a customer, optionally filtered by ad group."""
        try:
            client = get_auth().get_google_ads_client(account_label)
            service = client.get_service("GoogleAdsService")
            where = f"WHERE ad_group.id = {ad_group_id}" if ad_group_id else ""
            query = f"""
                SELECT
                    ad_group_criterion.criterion_id,
                    ad_group_criterion.keyword.text,
                    ad_group_criterion.keyword.match_type,
                    ad_group_criterion.status,
                    ad_group_criterion.cpc_bid_micros,
                    ad_group_criterion.negative,
                    ad_group.id,
                    ad_group.name
                FROM ad_group_criterion
                {where}
                WHERE ad_group_criterion.type = KEYWORD
                LIMIT 5000
            """ if ad_group_id else """
                SELECT
                    ad_group_criterion.criterion_id,
                    ad_group_criterion.keyword.text,
                    ad_group_criterion.keyword.match_type,
                    ad_group_criterion.status,
                    ad_group_criterion.cpc_bid_micros,
                    ad_group_criterion.negative,
                    ad_group.id,
                    ad_group.name
                FROM ad_group_criterion
                WHERE ad_group_criterion.type = KEYWORD
                LIMIT 5000
            """
            # Fix: if ad_group_id given, combine filter
            if ad_group_id:
                query = f"""
                    SELECT
                        ad_group_criterion.criterion_id,
                        ad_group_criterion.keyword.text,
                        ad_group_criterion.keyword.match_type,
                        ad_group_criterion.status,
                        ad_group_criterion.cpc_bid_micros,
                        ad_group_criterion.negative,
                        ad_group.id,
                        ad_group.name
                    FROM ad_group_criterion
                    WHERE ad_group_criterion.type = KEYWORD
                      AND ad_group.id = {ad_group_id}
                    LIMIT 5000
                """
            response = service.search(customer_id=customer_id, query=query)
            keywords: List[Dict[str, Any]] = []
            for row in response:
                kw = row.ad_group_criterion
                keywords.append(
                    {
                        "criterion_id": str(kw.criterion_id),
                        "text": kw.keyword.text,
                        "match_type": str(kw.keyword.match_type),
                        "status": str(kw.status),
                        "cpc_bid_micros": kw.cpc_bid_micros,
                        "negative": kw.negative,
                        "ad_group_id": str(row.ad_group.id),
                        "ad_group_name": row.ad_group.name,
                    }
                )
            return {"count": len(keywords), "keywords": keywords}
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def add_keywords(
        customer_id: str,
        ad_group_id: str,
        keywords: List[Dict[str, Any]],
        account_label: str = "default",
    ) -> Dict[str, Any]:
        """Add a batch of keywords to an ad group.

        Args:
            keywords: List of ``{"text": "...", "match_type": "EXACT|PHRASE|BROAD",
                "cpc_bid_aud": 1.00}``.
        """
        try:
            client = get_auth().get_google_ads_client(account_label)
            service = client.get_service("AdGroupCriterionService")
            operations = []
            for kw in keywords:
                op = client.get_type("AdGroupCriterionOperation")
                criterion = op.create
                criterion.ad_group = client.get_service("AdGroupService").ad_group_path(
                    customer_id, ad_group_id
                )
                criterion.status = client.enums.AdGroupCriterionStatusEnum.ENABLED
                criterion.keyword.text = kw["text"]
                criterion.keyword.match_type = client.enums.KeywordMatchTypeEnum[
                    kw.get("match_type", "PHRASE").upper()
                ]
                if "cpc_bid_aud" in kw:
                    criterion.cpc_bid_micros = int(kw["cpc_bid_aud"] * 1_000_000)
                operations.append(op)

            response = service.mutate_ad_group_criteria(
                customer_id=customer_id, operations=operations
            )
            logger.info("Added %d keywords to ad_group %s", len(keywords), ad_group_id)
            return {
                "count": len(response.results),
                "resource_names": [r.resource_name for r in response.results],
            }
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def add_negative_keywords(
        customer_id: str,
        ad_group_id: str,
        keywords: List[Dict[str, Any]],
        account_label: str = "default",
    ) -> Dict[str, Any]:
        """Add negative keywords to an ad group.

        Args:
            keywords: List of ``{"text": "...", "match_type": "EXACT|PHRASE|BROAD"}``.
        """
        try:
            client = get_auth().get_google_ads_client(account_label)
            service = client.get_service("AdGroupCriterionService")
            operations = []
            for kw in keywords:
                op = client.get_type("AdGroupCriterionOperation")
                criterion = op.create
                criterion.ad_group = client.get_service("AdGroupService").ad_group_path(
                    customer_id, ad_group_id
                )
                criterion.negative = True
                criterion.keyword.text = kw["text"]
                criterion.keyword.match_type = client.enums.KeywordMatchTypeEnum[
                    kw.get("match_type", "PHRASE").upper()
                ]
                operations.append(op)

            response = service.mutate_ad_group_criteria(
                customer_id=customer_id, operations=operations
            )
            return {
                "count": len(response.results),
                "resource_names": [r.resource_name for r in response.results],
            }
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def generate_keyword_ideas(
        customer_id: str,
        seeds: List[str],
        language_id: str = "1000",
        geo_target_id: str = "2036",
        account_label: str = "default",
    ) -> Dict[str, Any]:
        """Generate keyword ideas from seed keywords.

        Args:
            seeds: List of seed keyword strings.
            language_id: Google Ads language criterion ID (1000 = English).
            geo_target_id: Google Ads geo criterion ID (2036 = Australia).
        """
        try:
            client = get_auth().get_google_ads_client(account_label)
            service = client.get_service("KeywordPlanIdeaService")
            request = client.get_type("GenerateKeywordIdeasRequest")
            request.customer_id = customer_id
            request.language = client.get_service("LanguageConstantService").language_constant_path(language_id)
            request.geo_target_constants.append(
                client.get_service("GeoTargetConstantService").geo_target_constant_path(geo_target_id)
            )
            request.keyword_plan_network = client.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH
            request.keyword_seed.keywords.extend(seeds)

            response = service.generate_keyword_ideas(request=request)
            ideas: List[Dict[str, Any]] = []
            for idea in response:
                metrics = idea.keyword_idea_metrics
                ideas.append(
                    {
                        "text": idea.text,
                        "avg_monthly_searches": metrics.avg_monthly_searches,
                        "competition": str(metrics.competition),
                        "low_top_of_page_bid_micros": metrics.low_top_of_page_bid_micros,
                        "high_top_of_page_bid_micros": metrics.high_top_of_page_bid_micros,
                    }
                )
            ideas.sort(key=lambda x: x.get("avg_monthly_searches") or 0, reverse=True)
            return {"seeds": seeds, "count": len(ideas), "ideas": ideas[:200]}
        except Exception as exc:
            raise wrap_http_error(exc)
