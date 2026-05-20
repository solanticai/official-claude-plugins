"""Google Ads budget management tools."""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

from mcp_servers.common.errors import wrap_http_error
from mcp_servers.common.logger import get_server_logger

logger = get_server_logger("ppc-google-ads.budgets")


def register(mcp, get_auth: Callable[[], Any]) -> None:
    @mcp.tool()
    def list_budgets(
        customer_id: str,
        account_label: str = "default",
    ) -> Dict[str, Any]:
        """List all campaign budgets on an account."""
        try:
            client = get_auth().get_google_ads_client(account_label)
            service = client.get_service("GoogleAdsService")
            query = """
                SELECT
                    campaign_budget.id,
                    campaign_budget.name,
                    campaign_budget.amount_micros,
                    campaign_budget.delivery_method,
                    campaign_budget.explicitly_shared,
                    campaign_budget.status,
                    campaign_budget.total_amount_micros,
                    campaign_budget.resource_name
                FROM campaign_budget
                ORDER BY campaign_budget.name
                LIMIT 500
            """
            response = service.search(customer_id=customer_id, query=query)
            budgets: List[Dict[str, Any]] = []
            for row in response:
                b = row.campaign_budget
                budgets.append(
                    {
                        "id": str(b.id),
                        "name": b.name,
                        "amount_micros": b.amount_micros,
                        "amount_aud": b.amount_micros / 1_000_000
                        if b.amount_micros
                        else None,
                        "delivery_method": str(b.delivery_method),
                        "explicitly_shared": b.explicitly_shared,
                        "status": str(b.status),
                        "total_amount_micros": b.total_amount_micros
                        if b.total_amount_micros
                        else None,
                        "resource_name": b.resource_name,
                    }
                )
            return {"count": len(budgets), "budgets": budgets}
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def update_budget(
        customer_id: str,
        budget_id: str,
        amount_aud: Optional[float] = None,
        delivery_method: Optional[str] = None,
        account_label: str = "default",
    ) -> Dict[str, Any]:
        """Update a campaign budget.

        Args:
            amount_aud: New daily budget amount in AUD.
            delivery_method: ``STANDARD`` or ``ACCELERATED``.
        """
        try:
            client = get_auth().get_google_ads_client(account_label)
            service = client.get_service("CampaignBudgetService")
            op = client.get_type("CampaignBudgetOperation")
            op.update.resource_name = service.campaign_budget_path(
                customer_id, budget_id
            )
            paths = []
            if amount_aud is not None:
                op.update.amount_micros = int(amount_aud * 1_000_000)
                paths.append("amount_micros")
            if delivery_method:
                op.update.delivery_method = client.enums.BudgetDeliveryMethodEnum[
                    delivery_method.upper()
                ]
                paths.append("delivery_method")
            if not paths:
                return {"error": "No fields to update — provide amount_aud or delivery_method"}

            client.copy_from(
                op.update_mask,
                client.get_type("FieldMask")(paths=paths),
            )
            response = service.mutate_campaign_budgets(
                customer_id=customer_id, operations=[op]
            )
            logger.info("Updated budget %s", budget_id)
            return {"resource_name": response.results[0].resource_name}
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def create_shared_budget(
        customer_id: str,
        name: str,
        amount_aud: float,
        account_label: str = "default",
    ) -> Dict[str, Any]:
        """Create a shared budget that can be used across multiple campaigns.

        Args:
            amount_aud: Daily budget amount in AUD.
        """
        try:
            client = get_auth().get_google_ads_client(account_label)
            service = client.get_service("CampaignBudgetService")
            op = client.get_type("CampaignBudgetOperation")
            budget = op.create
            budget.name = name
            budget.amount_micros = int(amount_aud * 1_000_000)
            budget.delivery_method = client.enums.BudgetDeliveryMethodEnum.STANDARD
            budget.explicitly_shared = True

            response = service.mutate_campaign_budgets(
                customer_id=customer_id, operations=[op]
            )
            logger.info("Created shared budget '%s'", name)
            return {"resource_name": response.results[0].resource_name}
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def assign_shared_budget(
        customer_id: str,
        campaign_id: str,
        budget_resource_name: str,
        account_label: str = "default",
    ) -> Dict[str, Any]:
        """Assign a shared budget to a campaign.

        Args:
            budget_resource_name: Full resource name of the shared budget
                (e.g. ``customers/123/campaignBudgets/456``).
        """
        try:
            client = get_auth().get_google_ads_client(account_label)
            service = client.get_service("CampaignService")
            op = client.get_type("CampaignOperation")
            op.update.resource_name = service.campaign_path(
                customer_id, campaign_id
            )
            op.update.campaign_budget = budget_resource_name
            client.copy_from(
                op.update_mask,
                client.get_type("FieldMask")(paths=["campaign_budget"]),
            )
            response = service.mutate_campaigns(
                customer_id=customer_id, operations=[op]
            )
            return {"resource_name": response.results[0].resource_name}
        except Exception as exc:
            raise wrap_http_error(exc)
