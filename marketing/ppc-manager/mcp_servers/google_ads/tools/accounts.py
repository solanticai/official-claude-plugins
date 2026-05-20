"""Google Ads account-level tools: list accessible customers, get customer info."""

from __future__ import annotations

from typing import Any, Callable, Dict, List

from mcp_servers.common.errors import wrap_http_error
from mcp_servers.common.logger import get_server_logger

logger = get_server_logger("ppc-google-ads.accounts")


def register(mcp, get_auth: Callable[[], Any]) -> None:
    @mcp.tool()
    def list_accessible_customers(account_label: str = "default") -> Dict[str, Any]:
        """List every Google Ads customer ID accessible to the authenticated user.

        Returns the customer IDs in the raw format ``customers/1234567890``.
        """
        try:
            client = get_auth().get_google_ads_client(account_label)
            service = client.get_service("CustomerService")
            response = service.list_accessible_customers()
            return {
                "count": len(response.resource_names),
                "customers": list(response.resource_names),
            }
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def get_customer_info(
        customer_id: str, account_label: str = "default"
    ) -> Dict[str, Any]:
        """Get basic info for a Google Ads customer.

        Args:
            customer_id: 10-digit customer ID, no dashes.
        """
        try:
            client = get_auth().get_google_ads_client(account_label)
            ga_service = client.get_service("GoogleAdsService")
            query = """
                SELECT
                    customer.id,
                    customer.descriptive_name,
                    customer.currency_code,
                    customer.time_zone,
                    customer.tracking_url_template,
                    customer.auto_tagging_enabled,
                    customer.test_account,
                    customer.manager
                FROM customer
                LIMIT 1
            """
            response = ga_service.search(customer_id=customer_id, query=query)
            for row in response:
                c = row.customer
                return {
                    "id": str(c.id),
                    "descriptive_name": c.descriptive_name,
                    "currency_code": c.currency_code,
                    "time_zone": c.time_zone,
                    "tracking_url_template": c.tracking_url_template,
                    "auto_tagging_enabled": c.auto_tagging_enabled,
                    "test_account": c.test_account,
                    "manager": c.manager,
                }
            return {"error": "No customer data returned"}
        except Exception as exc:
            raise wrap_http_error(exc)
