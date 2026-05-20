"""GTM trigger tools: list, create, delete."""

from __future__ import annotations

from typing import Any, Callable, Dict, List

from mcp_servers.common.errors import wrap_http_error


def register(mcp, get_auth: Callable[[], Any]) -> None:
    @mcp.tool()
    def list_triggers(
        account_id: str,
        container_id: str,
        workspace_id: str,
        google_account: str = "default",
    ) -> Dict[str, Any]:
        """List every trigger in a workspace."""
        try:
            service = get_auth().get_gtm_service(google_account)
            parent = (
                f"accounts/{account_id}/containers/{container_id}/workspaces/{workspace_id}"
            )
            result = (
                service.accounts()
                .containers()
                .workspaces()
                .triggers()
                .list(parent=parent)
                .execute()
            )
            triggers: List[Dict[str, Any]] = result.get("trigger", [])
            return {
                "count": len(triggers),
                "triggers": [
                    {
                        "triggerId": t.get("triggerId"),
                        "name": t.get("name"),
                        "type": t.get("type"),
                    }
                    for t in triggers
                ],
            }
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def create_trigger(
        account_id: str,
        container_id: str,
        workspace_id: str,
        name: str,
        trigger_type: str,
        filters: List[Dict[str, Any]] | None = None,
        custom_event_filter: List[Dict[str, Any]] | None = None,
        google_account: str = "default",
    ) -> Dict[str, Any]:
        """Create a trigger.

        Args:
            trigger_type: 'pageview', 'click', 'customEvent', 'formSubmission',
                'timer', 'historyChange', etc.
            filters: Optional list of filter dicts per the GTM API filter shape.
            custom_event_filter: Required for ``trigger_type='customEvent'``.
        """
        try:
            service = get_auth().get_gtm_service(google_account)
            parent = (
                f"accounts/{account_id}/containers/{container_id}/workspaces/{workspace_id}"
            )
            body: Dict[str, Any] = {"name": name, "type": trigger_type}
            if filters:
                body["filter"] = filters
            if custom_event_filter:
                body["customEventFilter"] = custom_event_filter
            return (
                service.accounts()
                .containers()
                .workspaces()
                .triggers()
                .create(parent=parent, body=body)
                .execute()
            )
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def delete_trigger(
        account_id: str,
        container_id: str,
        workspace_id: str,
        trigger_id: str,
        google_account: str = "default",
    ) -> Dict[str, Any]:
        try:
            service = get_auth().get_gtm_service(google_account)
            path = (
                f"accounts/{account_id}/containers/{container_id}"
                f"/workspaces/{workspace_id}/triggers/{trigger_id}"
            )
            service.accounts().containers().workspaces().triggers().delete(
                path=path
            ).execute()
            return {"deleted": True, "path": path}
        except Exception as exc:
            raise wrap_http_error(exc)
