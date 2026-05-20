"""GTM variable tools: list, create, delete (user-defined and data-layer variables)."""

from __future__ import annotations

from typing import Any, Callable, Dict, List

from mcp_servers.common.errors import wrap_http_error
from mcp_servers.gtm.tools.tags import _parameters_to_api


def register(mcp, get_auth: Callable[[], Any]) -> None:
    @mcp.tool()
    def list_variables(
        account_id: str,
        container_id: str,
        workspace_id: str,
        google_account: str = "default",
    ) -> Dict[str, Any]:
        """List every user-defined variable in a workspace."""
        try:
            service = get_auth().get_gtm_service(google_account)
            parent = (
                f"accounts/{account_id}/containers/{container_id}/workspaces/{workspace_id}"
            )
            result = (
                service.accounts()
                .containers()
                .workspaces()
                .variables()
                .list(parent=parent)
                .execute()
            )
            variables: List[Dict[str, Any]] = result.get("variable", [])
            return {
                "count": len(variables),
                "variables": [
                    {
                        "variableId": v.get("variableId"),
                        "name": v.get("name"),
                        "type": v.get("type"),
                    }
                    for v in variables
                ],
            }
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def create_variable(
        account_id: str,
        container_id: str,
        workspace_id: str,
        name: str,
        variable_type: str,
        parameters: Dict[str, Any],
        google_account: str = "default",
    ) -> Dict[str, Any]:
        """Create a user-defined variable.

        Args:
            variable_type: 'v' for Data Layer Variable, 'c' for Constant,
                'smm' for Lookup Table, 'u' for URL, etc. See
                ``reference.md`` in the gtm-datalayer skill for the cheat sheet.
            parameters: Flat dict of variable parameters. For a Data Layer
                Variable, the only required key is ``name`` (the dataLayer key).
        """
        try:
            service = get_auth().get_gtm_service(google_account)
            parent = (
                f"accounts/{account_id}/containers/{container_id}/workspaces/{workspace_id}"
            )
            body = {
                "name": name,
                "type": variable_type,
                "parameter": _parameters_to_api(parameters),
            }
            return (
                service.accounts()
                .containers()
                .workspaces()
                .variables()
                .create(parent=parent, body=body)
                .execute()
            )
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def delete_variable(
        account_id: str,
        container_id: str,
        workspace_id: str,
        variable_id: str,
        google_account: str = "default",
    ) -> Dict[str, Any]:
        try:
            service = get_auth().get_gtm_service(google_account)
            path = (
                f"accounts/{account_id}/containers/{container_id}"
                f"/workspaces/{workspace_id}/variables/{variable_id}"
            )
            service.accounts().containers().workspaces().variables().delete(
                path=path
            ).execute()
            return {"deleted": True, "path": path}
        except Exception as exc:
            raise wrap_http_error(exc)
