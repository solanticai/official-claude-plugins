"""Google Ads reporting tools: GAQL query runner and common preset reports."""

from __future__ import annotations

from typing import Any, Callable, Dict, List

from mcp_servers.common.errors import wrap_http_error
from mcp_servers.common.logger import get_server_logger

logger = get_server_logger("ppc-google-ads.reporting")


def register(mcp, get_auth: Callable[[], Any]) -> None:
    @mcp.tool()
    def run_gaql(
        customer_id: str,
        query: str,
        account_label: str = "default",
        limit: int = 1000,
    ) -> Dict[str, Any]:
        """Run a raw GAQL query and return the rows.

        Args:
            query: A full GAQL query string. Automatically applies ``LIMIT``
                if not present.
        """
        try:
            client = get_auth().get_google_ads_client(account_label)
            service = client.get_service("GoogleAdsService")
            if "LIMIT" not in query.upper():
                query = f"{query.rstrip()} LIMIT {limit}"
            response = service.search(customer_id=customer_id, query=query)
            rows: List[Dict[str, Any]] = []
            for row in response:
                # Flatten the proto-plus object to a plain dict.
                rows.append(_row_to_dict(row))
            return {"customer_id": customer_id, "count": len(rows), "rows": rows}
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def campaign_performance_last_30_days(
        customer_id: str,
        account_label: str = "default",
    ) -> Dict[str, Any]:
        """Preset: campaign-level performance for the last 30 days."""
        query = """
            SELECT
                campaign.id,
                campaign.name,
                campaign.status,
                metrics.impressions,
                metrics.clicks,
                metrics.ctr,
                metrics.average_cpc,
                metrics.cost_micros,
                metrics.conversions,
                metrics.conversions_value,
                metrics.cost_per_conversion
            FROM campaign
            WHERE segments.date DURING LAST_30_DAYS
              AND campaign.status != 'REMOVED'
            ORDER BY metrics.cost_micros DESC
            LIMIT 500
        """
        try:
            client = get_auth().get_google_ads_client(account_label)
            service = client.get_service("GoogleAdsService")
            response = service.search(customer_id=customer_id, query=query)
            rows: List[Dict[str, Any]] = []
            for row in response:
                rows.append(
                    {
                        "campaign_id": str(row.campaign.id),
                        "campaign_name": row.campaign.name,
                        "status": str(row.campaign.status),
                        "impressions": row.metrics.impressions,
                        "clicks": row.metrics.clicks,
                        "ctr": row.metrics.ctr,
                        "avg_cpc_aud": row.metrics.average_cpc / 1_000_000,
                        "cost_aud": row.metrics.cost_micros / 1_000_000,
                        "conversions": row.metrics.conversions,
                        "conversions_value": row.metrics.conversions_value,
                        "cost_per_conversion_aud": (
                            row.metrics.cost_per_conversion / 1_000_000
                            if row.metrics.cost_per_conversion
                            else None
                        ),
                    }
                )
            return {"customer_id": customer_id, "count": len(rows), "rows": rows}
        except Exception as exc:
            raise wrap_http_error(exc)


def _row_to_dict(row) -> Dict[str, Any]:
    """Best-effort proto-plus → dict conversion for GAQL query rows."""
    try:
        # proto-plus exposes _pb.DESCRIPTOR; iterate top-level fields.
        fields = row._pb.DESCRIPTOR.fields
        out: Dict[str, Any] = {}
        for f in fields:
            value = getattr(row, f.name, None)
            if value is None:
                continue
            if hasattr(value, "_pb"):
                out[f.name] = _nested_to_dict(value)
            else:
                out[f.name] = value
        return out
    except Exception:
        return {"raw": str(row)}


def _nested_to_dict(proto_msg) -> Dict[str, Any]:
    """Recursively convert a proto message to a dict, flattening singular fields."""
    try:
        out: Dict[str, Any] = {}
        for f in proto_msg._pb.DESCRIPTOR.fields:
            v = getattr(proto_msg, f.name, None)
            if v is None:
                continue
            if hasattr(v, "_pb"):
                out[f.name] = _nested_to_dict(v)
            else:
                out[f.name] = v
        return out
    except Exception:
        return {"raw": str(proto_msg)}
