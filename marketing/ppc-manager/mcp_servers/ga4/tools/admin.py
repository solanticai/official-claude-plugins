"""GA4 Admin API tools: accounts, properties, data streams, linked Google Ads."""

from __future__ import annotations

from typing import Any, Callable, Dict, List

from mcp_servers.common.errors import wrap_http_error
from mcp_servers.common.logger import get_server_logger

logger = get_server_logger("ppc-ga4.admin")


def register(mcp, get_auth: Callable[[], Any]) -> None:
    @mcp.tool()
    def get_account_summaries(google_account: str = "default") -> Dict[str, Any]:
        """List every GA4 account and property accessible to the authenticated user.

        Returns a compact summary. Use ``get_property_details`` to drill into
        a single property.
        """
        try:
            from google.analytics.admin_v1beta import ListAccountSummariesRequest

            client = get_auth().get_ga4_admin_client(google_account)
            request = ListAccountSummariesRequest()
            response = client.list_account_summaries(request=request)

            accounts: List[Dict[str, Any]] = []
            for summary in response:
                accounts.append(
                    {
                        "account": summary.account,
                        "display_name": summary.display_name,
                        "property_summaries": [
                            {
                                "property": p.property,
                                "display_name": p.display_name,
                                "property_type": p.property_type.name if p.property_type else None,
                                "parent": p.parent,
                            }
                            for p in summary.property_summaries
                        ],
                    }
                )
            return {"count": len(accounts), "accounts": accounts}
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def get_property_details(
        property_id: str, google_account: str = "default"
    ) -> Dict[str, Any]:
        """Get full details for one GA4 property.

        Args:
            property_id: Either the numeric ID or the full resource name
                ``properties/123456``.
        """
        try:
            from google.analytics.admin_v1beta import GetPropertyRequest

            if not property_id.startswith("properties/"):
                property_id = f"properties/{property_id}"

            client = get_auth().get_ga4_admin_client(google_account)
            response = client.get_property(request=GetPropertyRequest(name=property_id))
            return {
                "name": response.name,
                "display_name": response.display_name,
                "property_type": response.property_type.name if response.property_type else None,
                "currency_code": response.currency_code,
                "time_zone": response.time_zone,
                "industry_category": response.industry_category.name if response.industry_category else None,
                "create_time": response.create_time.isoformat() if response.create_time else None,
                "update_time": response.update_time.isoformat() if response.update_time else None,
                "parent": response.parent,
            }
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def list_data_streams(
        property_id: str, google_account: str = "default"
    ) -> Dict[str, Any]:
        """List all data streams on a GA4 property (Web, iOS, Android).

        The Web stream's ``measurement_id`` (format ``G-XXXXXXXXXX``) is what
        you paste into the GTM GA4 Config tag.
        """
        try:
            from google.analytics.admin_v1beta import ListDataStreamsRequest

            if not property_id.startswith("properties/"):
                property_id = f"properties/{property_id}"

            client = get_auth().get_ga4_admin_client(google_account)
            response = client.list_data_streams(
                request=ListDataStreamsRequest(parent=property_id)
            )
            streams: List[Dict[str, Any]] = []
            for ds in response:
                entry: Dict[str, Any] = {
                    "name": ds.name,
                    "display_name": ds.display_name,
                    "type": ds.type_.name if ds.type_ else None,
                    "create_time": ds.create_time.isoformat() if ds.create_time else None,
                }
                if ds.web_stream_data:
                    entry["measurement_id"] = ds.web_stream_data.measurement_id
                    entry["default_uri"] = ds.web_stream_data.default_uri
                if ds.android_app_stream_data:
                    entry["package_name"] = ds.android_app_stream_data.package_name
                if ds.ios_app_stream_data:
                    entry["bundle_id"] = ds.ios_app_stream_data.bundle_id
                streams.append(entry)
            return {"count": len(streams), "streams": streams}
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def list_google_ads_links(
        property_id: str, google_account: str = "default"
    ) -> Dict[str, Any]:
        """List Google Ads accounts linked to a GA4 property."""
        try:
            from google.analytics.admin_v1beta import ListGoogleAdsLinksRequest

            if not property_id.startswith("properties/"):
                property_id = f"properties/{property_id}"

            client = get_auth().get_ga4_admin_client(google_account)
            response = client.list_google_ads_links(
                request=ListGoogleAdsLinksRequest(parent=property_id)
            )
            links: List[Dict[str, Any]] = []
            for link in response:
                links.append(
                    {
                        "name": link.name,
                        "customer_id": link.customer_id,
                        "can_manage_clients": link.can_manage_clients,
                        "ads_personalization_enabled": (
                            link.ads_personalization_enabled.value
                            if link.ads_personalization_enabled
                            else None
                        ),
                    }
                )
            return {"count": len(links), "links": links}
        except Exception as exc:
            raise wrap_http_error(exc)
