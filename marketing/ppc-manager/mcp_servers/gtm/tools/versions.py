"""GTM version tools: create a version from the workspace and publish it."""

from __future__ import annotations

from typing import Any, Callable, Dict

from mcp_servers.common.errors import wrap_http_error
from mcp_servers.common.logger import get_server_logger

logger = get_server_logger("ppc-gtm.versions")


def register(mcp, get_auth: Callable[[], Any]) -> None:
    @mcp.tool()
    def create_version(
        account_id: str,
        container_id: str,
        workspace_id: str,
        name: str,
        notes: str = "",
        google_account: str = "default",
    ) -> Dict[str, Any]:
        """Create a version from the current state of a workspace.

        Returns the new version's path. Call ``publish_version`` to promote it
        to live.
        """
        try:
            service = get_auth().get_gtm_service(google_account)
            parent = (
                f"accounts/{account_id}/containers/{container_id}/workspaces/{workspace_id}"
            )
            result = (
                service.accounts()
                .containers()
                .workspaces()
                .create_version(parent=parent, body={"name": name, "notes": notes})
                .execute()
            )
            logger.info("Created version '%s'", name)
            return result
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def publish_version(
        account_id: str,
        container_id: str,
        version_id: str,
        google_account: str = "default",
    ) -> Dict[str, Any]:
        """Publish a GTM version, making it live for end users."""
        try:
            service = get_auth().get_gtm_service(google_account)
            path = (
                f"accounts/{account_id}/containers/{container_id}/versions/{version_id}"
            )
            result = (
                service.accounts()
                .containers()
                .versions()
                .publish(path=path)
                .execute()
            )
            logger.info("Published version id=%s", version_id)
            return result
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def get_container_preview_url(
        account_id: str,
        container_id: str,
        version_id: str,
        google_account: str = "default",
    ) -> Dict[str, Any]:
        """Return the GTM preview-mode URL for a version.

        Used by the gtm-setup/gtm-tags skills to let users click-test changes
        before publishing.
        """
        path = (
            f"accounts/{account_id}/containers/{container_id}/versions/{version_id}"
        )
        preview = (
            f"https://tagassistant.google.com/"
            f"?container_id=GTM-{container_id}&version_id={version_id}"
        )
        return {"path": path, "preview_url": preview}
