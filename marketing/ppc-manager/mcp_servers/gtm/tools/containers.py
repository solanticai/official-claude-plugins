"""GTM container / workspace / account listing tools."""

from __future__ import annotations

from typing import Any, Callable, Dict, List

from mcp_servers.common.errors import NotFoundError, wrap_http_error
from mcp_servers.common.logger import get_server_logger

logger = get_server_logger("ppc-gtm.containers")


def register(mcp, get_auth: Callable[[], Any]) -> None:
    """Register container / workspace / account tools on the given FastMCP instance."""

    @mcp.tool()
    def list_accounts(google_account: str = "default") -> Dict[str, Any]:
        """List every Google Tag Manager account accessible to the authenticated user.

        Args:
            google_account: Vault account label (default: 'default').

        Returns:
            {"accounts": [{"accountId", "name", "path", "fingerprint"}]}
        """
        try:
            service = get_auth().get_gtm_service(google_account)
            result = service.accounts().list().execute()
            accounts: List[Dict[str, Any]] = result.get("account", [])
            return {
                "count": len(accounts),
                "accounts": [
                    {
                        "accountId": a.get("accountId"),
                        "name": a.get("name"),
                        "path": a.get("path"),
                        "fingerprint": a.get("fingerprint"),
                    }
                    for a in accounts
                ],
            }
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def list_containers(account_id: str, google_account: str = "default") -> Dict[str, Any]:
        """List every container inside a GTM account.

        Args:
            account_id: GTM account ID (not the path).
            google_account: Vault account label.
        """
        try:
            service = get_auth().get_gtm_service(google_account)
            parent = f"accounts/{account_id}"
            result = service.accounts().containers().list(parent=parent).execute()
            containers: List[Dict[str, Any]] = result.get("container", [])
            return {
                "account_id": account_id,
                "count": len(containers),
                "containers": [
                    {
                        "containerId": c.get("containerId"),
                        "name": c.get("name"),
                        "publicId": c.get("publicId"),
                        "usageContext": c.get("usageContext"),
                        "path": c.get("path"),
                        "tagIds": c.get("tagIds"),
                    }
                    for c in containers
                ],
            }
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def get_container(
        account_id: str, container_id: str, google_account: str = "default"
    ) -> Dict[str, Any]:
        """Get metadata for a single GTM container."""
        try:
            service = get_auth().get_gtm_service(google_account)
            path = f"accounts/{account_id}/containers/{container_id}"
            result = service.accounts().containers().get(path=path).execute()
            return result
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def list_workspaces(
        account_id: str, container_id: str, google_account: str = "default"
    ) -> Dict[str, Any]:
        """List every workspace in a container.

        Workspace 'default' is the only one 99 % of users need.
        """
        try:
            service = get_auth().get_gtm_service(google_account)
            parent = f"accounts/{account_id}/containers/{container_id}"
            result = (
                service.accounts()
                .containers()
                .workspaces()
                .list(parent=parent)
                .execute()
            )
            workspaces: List[Dict[str, Any]] = result.get("workspace", [])
            return {
                "account_id": account_id,
                "container_id": container_id,
                "count": len(workspaces),
                "workspaces": [
                    {
                        "workspaceId": w.get("workspaceId"),
                        "name": w.get("name"),
                        "description": w.get("description"),
                        "path": w.get("path"),
                    }
                    for w in workspaces
                ],
            }
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def get_default_workspace_id(
        account_id: str, container_id: str, google_account: str = "default"
    ) -> Dict[str, Any]:
        """Return the workspaceId of the 'Default Workspace' for a container.

        Most write operations go against the default workspace.
        """
        try:
            service = get_auth().get_gtm_service(google_account)
            parent = f"accounts/{account_id}/containers/{container_id}"
            result = (
                service.accounts()
                .containers()
                .workspaces()
                .list(parent=parent)
                .execute()
            )
            for w in result.get("workspace", []):
                if w.get("name", "").lower().startswith("default"):
                    return {
                        "workspaceId": w.get("workspaceId"),
                        "name": w.get("name"),
                        "path": w.get("path"),
                    }
            raise NotFoundError(
                f"No default workspace in {account_id}/{container_id}"
            )
        except NotFoundError:
            raise
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def create_workspace(
        account_id: str,
        container_id: str,
        name: str,
        description: str = "",
        google_account: str = "default",
    ) -> Dict[str, Any]:
        """Create a new workspace inside a container.

        Use this to isolate a set of pending changes from the default workspace.
        """
        try:
            service = get_auth().get_gtm_service(google_account)
            parent = f"accounts/{account_id}/containers/{container_id}"
            body = {"name": name, "description": description}
            result = (
                service.accounts()
                .containers()
                .workspaces()
                .create(parent=parent, body=body)
                .execute()
            )
            return result
        except Exception as exc:
            raise wrap_http_error(exc)
