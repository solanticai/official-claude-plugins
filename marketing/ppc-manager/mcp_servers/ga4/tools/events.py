"""GA4 Admin API event + custom dimension/metric tools."""

from __future__ import annotations

from typing import Any, Callable, Dict, List

from mcp_servers.common.errors import wrap_http_error
from mcp_servers.common.logger import get_server_logger

logger = get_server_logger("ppc-ga4.events")


def _normalize_property(property_id: str) -> str:
    if property_id.startswith("properties/"):
        return property_id
    return f"properties/{property_id}"


def register(mcp, get_auth: Callable[[], Any]) -> None:
    @mcp.tool()
    def list_conversion_events(
        property_id: str, google_account: str = "default"
    ) -> Dict[str, Any]:
        """List all conversion events configured on a GA4 property."""
        try:
            from google.analytics.admin_v1beta import ListConversionEventsRequest

            client = get_auth().get_ga4_admin_client(google_account)
            response = client.list_conversion_events(
                request=ListConversionEventsRequest(parent=_normalize_property(property_id))
            )
            events: List[Dict[str, Any]] = []
            for event in response:
                events.append(
                    {
                        "name": event.name,
                        "event_name": event.event_name,
                        "deletable": event.deletable,
                        "custom": event.custom,
                        "create_time": event.create_time.isoformat() if event.create_time else None,
                    }
                )
            return {"count": len(events), "events": events}
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def create_conversion_event(
        property_id: str,
        event_name: str,
        google_account: str = "default",
    ) -> Dict[str, Any]:
        """Mark an event as a conversion on a GA4 property.

        The event must already be arriving (i.e. GTM has pushed it at least once)
        for this to work. If you call this before the event has fired, GA4
        returns ``INVALID_ARGUMENT``.
        """
        try:
            from google.analytics.admin_v1beta import (
                ConversionEvent,
                CreateConversionEventRequest,
            )

            client = get_auth().get_ga4_admin_client(google_account)
            request = CreateConversionEventRequest(
                parent=_normalize_property(property_id),
                conversion_event=ConversionEvent(event_name=event_name),
            )
            response = client.create_conversion_event(request=request)
            return {
                "name": response.name,
                "event_name": response.event_name,
                "deletable": response.deletable,
                "custom": response.custom,
            }
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def list_custom_dimensions(
        property_id: str, google_account: str = "default"
    ) -> Dict[str, Any]:
        """List custom dimensions on a GA4 property."""
        try:
            from google.analytics.admin_v1beta import ListCustomDimensionsRequest

            client = get_auth().get_ga4_admin_client(google_account)
            response = client.list_custom_dimensions(
                request=ListCustomDimensionsRequest(parent=_normalize_property(property_id))
            )
            dims: List[Dict[str, Any]] = []
            for d in response:
                dims.append(
                    {
                        "name": d.name,
                        "parameter_name": d.parameter_name,
                        "display_name": d.display_name,
                        "description": d.description,
                        "scope": d.scope.name if d.scope else None,
                    }
                )
            return {"count": len(dims), "dimensions": dims}
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def create_custom_dimension(
        property_id: str,
        parameter_name: str,
        display_name: str,
        description: str = "",
        scope: str = "EVENT",
        google_account: str = "default",
    ) -> Dict[str, Any]:
        """Create a custom dimension on a GA4 property.

        Args:
            parameter_name: The dataLayer/event parameter name (e.g. ``item_brand``).
            display_name: Human-readable label in GA4 reports.
            scope: ``EVENT`` (default, per-event) or ``USER`` (persisted).
        """
        try:
            from google.analytics.admin_v1beta import (
                CreateCustomDimensionRequest,
                CustomDimension,
            )

            client = get_auth().get_ga4_admin_client(google_account)
            scope_enum = CustomDimension.DimensionScope[scope.upper()]
            request = CreateCustomDimensionRequest(
                parent=_normalize_property(property_id),
                custom_dimension=CustomDimension(
                    parameter_name=parameter_name,
                    display_name=display_name,
                    description=description,
                    scope=scope_enum,
                ),
            )
            response = client.create_custom_dimension(request=request)
            return {
                "name": response.name,
                "parameter_name": response.parameter_name,
                "display_name": response.display_name,
                "scope": response.scope.name if response.scope else None,
            }
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def list_custom_metrics(
        property_id: str, google_account: str = "default"
    ) -> Dict[str, Any]:
        """List custom metrics on a GA4 property."""
        try:
            from google.analytics.admin_v1beta import ListCustomMetricsRequest

            client = get_auth().get_ga4_admin_client(google_account)
            response = client.list_custom_metrics(
                request=ListCustomMetricsRequest(parent=_normalize_property(property_id))
            )
            metrics: List[Dict[str, Any]] = []
            for m in response:
                metrics.append(
                    {
                        "name": m.name,
                        "parameter_name": m.parameter_name,
                        "display_name": m.display_name,
                        "measurement_unit": m.measurement_unit.name if m.measurement_unit else None,
                        "scope": m.scope.name if m.scope else None,
                    }
                )
            return {"count": len(metrics), "metrics": metrics}
        except Exception as exc:
            raise wrap_http_error(exc)
