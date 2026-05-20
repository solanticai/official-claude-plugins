"""GA4 Data API reporting tools: run_report, run_realtime_report."""

from __future__ import annotations

from typing import Any, Callable, Dict, List

from mcp_servers.common.errors import wrap_http_error
from mcp_servers.common.logger import get_server_logger

logger = get_server_logger("ppc-ga4.reporting")


def register(mcp, get_auth: Callable[[], Any]) -> None:
    @mcp.tool()
    def run_report(
        property_id: str,
        dimensions: List[str],
        metrics: List[str],
        start_date: str = "30daysAgo",
        end_date: str = "today",
        limit: int = 100,
        dimension_filter: Dict[str, Any] | None = None,
        google_account: str = "default",
    ) -> Dict[str, Any]:
        """Run a GA4 report via the Data API.

        Args:
            property_id: Numeric GA4 property ID (or ``properties/<id>``).
            dimensions: List of GA4 dimension API names (e.g. ``eventName``).
            metrics: List of GA4 metric API names (e.g. ``eventCount``).
            start_date: ``YYYY-MM-DD``, ``NdaysAgo``, or ``today``/``yesterday``.
            end_date: Same format as start_date.
            limit: Max rows to return (default 100, max 250 000).
            dimension_filter: Optional GA4 FilterExpression dict.
        """
        try:
            from google.analytics.data_v1beta import (
                DateRange,
                Dimension,
                Metric,
                RunReportRequest,
            )

            if property_id.startswith("properties/"):
                property_id_only = property_id
            else:
                property_id_only = f"properties/{property_id}"

            client = get_auth().get_ga4_data_client(google_account)
            request = RunReportRequest(
                property=property_id_only,
                dimensions=[Dimension(name=d) for d in dimensions],
                metrics=[Metric(name=m) for m in metrics],
                date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
                limit=limit,
            )
            response = client.run_report(request=request)

            rows: List[Dict[str, Any]] = []
            for row in response.rows:
                entry: Dict[str, Any] = {}
                for i, dim in enumerate(row.dimension_values):
                    entry[dimensions[i]] = dim.value
                for i, met in enumerate(row.metric_values):
                    entry[metrics[i]] = met.value
                rows.append(entry)

            return {
                "property": property_id_only,
                "dimensions": dimensions,
                "metrics": metrics,
                "date_range": {"start": start_date, "end": end_date},
                "row_count": response.row_count,
                "rows": rows,
            }
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def run_realtime_report(
        property_id: str,
        dimensions: List[str],
        metrics: List[str],
        limit: int = 100,
        google_account: str = "default",
    ) -> Dict[str, Any]:
        """Run a GA4 realtime report.

        Realtime reports support a narrower set of dimensions/metrics than
        regular reports. Use for DebugView-like "is tracking firing right now".
        """
        try:
            from google.analytics.data_v1beta import (
                Dimension,
                Metric,
                RunRealtimeReportRequest,
            )

            if property_id.startswith("properties/"):
                property_id_only = property_id
            else:
                property_id_only = f"properties/{property_id}"

            client = get_auth().get_ga4_data_client(google_account)
            request = RunRealtimeReportRequest(
                property=property_id_only,
                dimensions=[Dimension(name=d) for d in dimensions],
                metrics=[Metric(name=m) for m in metrics],
                limit=limit,
            )
            response = client.run_realtime_report(request=request)

            rows: List[Dict[str, Any]] = []
            for row in response.rows:
                entry: Dict[str, Any] = {}
                for i, dim in enumerate(row.dimension_values):
                    entry[dimensions[i]] = dim.value
                for i, met in enumerate(row.metric_values):
                    entry[metrics[i]] = met.value
                rows.append(entry)

            return {
                "property": property_id_only,
                "row_count": response.row_count,
                "rows": rows,
            }
        except Exception as exc:
            raise wrap_http_error(exc)
