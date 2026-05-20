"""GTM tag tools: list, create, update, delete."""

from __future__ import annotations

from typing import Any, Callable, Dict, List

from mcp_servers.common.errors import wrap_http_error
from mcp_servers.common.logger import get_server_logger

logger = get_server_logger("ppc-gtm.tags")


def _parameters_to_api(parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Convert a flat {key: value} dict into the API's parameter list shape."""
    out: List[Dict[str, Any]] = []
    for key, value in parameters.items():
        if isinstance(value, bool):
            out.append({"key": key, "type": "boolean", "value": str(value).lower()})
        elif isinstance(value, (int, float)):
            out.append({"key": key, "type": "template", "value": str(value)})
        elif isinstance(value, list):
            out.append({"key": key, "type": "list", "list": [
                {"type": "template", "value": str(v)} for v in value
            ]})
        else:
            out.append({"key": key, "type": "template", "value": str(value)})
    return out


def register(mcp, get_auth: Callable[[], Any]) -> None:
    @mcp.tool()
    def list_tags(
        account_id: str,
        container_id: str,
        workspace_id: str,
        google_account: str = "default",
    ) -> Dict[str, Any]:
        """List every tag in a workspace."""
        try:
            service = get_auth().get_gtm_service(google_account)
            parent = (
                f"accounts/{account_id}/containers/{container_id}/workspaces/{workspace_id}"
            )
            result = (
                service.accounts()
                .containers()
                .workspaces()
                .tags()
                .list(parent=parent)
                .execute()
            )
            tags: List[Dict[str, Any]] = result.get("tag", [])
            return {
                "count": len(tags),
                "tags": [
                    {
                        "tagId": t.get("tagId"),
                        "name": t.get("name"),
                        "type": t.get("type"),
                        "firingTriggerId": t.get("firingTriggerId"),
                        "paused": t.get("paused"),
                    }
                    for t in tags
                ],
            }
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def get_tag(
        account_id: str,
        container_id: str,
        workspace_id: str,
        tag_id: str,
        google_account: str = "default",
    ) -> Dict[str, Any]:
        """Get a single tag with its full config."""
        try:
            service = get_auth().get_gtm_service(google_account)
            path = (
                f"accounts/{account_id}/containers/{container_id}"
                f"/workspaces/{workspace_id}/tags/{tag_id}"
            )
            return service.accounts().containers().workspaces().tags().get(path=path).execute()
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def create_tag(
        account_id: str,
        container_id: str,
        workspace_id: str,
        name: str,
        tag_type: str,
        parameters: Dict[str, Any],
        firing_trigger_ids: List[str] | None = None,
        google_account: str = "default",
    ) -> Dict[str, Any]:
        """Create a tag inside a workspace.

        Args:
            tag_type: Google Tag Manager tag type id (e.g. 'ua' for Universal
                Analytics, 'html' for Custom HTML, 'gaawe' for GA4 Event,
                'gaawc' for GA4 Config).
            parameters: Flat dict of tag parameters. See ``reference.md`` in
                ``gtm-tags`` skill for the tag-type cheat sheet.
            firing_trigger_ids: Optional list of trigger IDs to attach.
        """
        try:
            service = get_auth().get_gtm_service(google_account)
            parent = (
                f"accounts/{account_id}/containers/{container_id}/workspaces/{workspace_id}"
            )
            body: Dict[str, Any] = {
                "name": name,
                "type": tag_type,
                "parameter": _parameters_to_api(parameters),
            }
            if firing_trigger_ids:
                body["firingTriggerId"] = firing_trigger_ids
            result = (
                service.accounts()
                .containers()
                .workspaces()
                .tags()
                .create(parent=parent, body=body)
                .execute()
            )
            logger.info("Created tag '%s' id=%s", name, result.get("tagId"))
            return result
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def update_tag(
        account_id: str,
        container_id: str,
        workspace_id: str,
        tag_id: str,
        name: str | None = None,
        parameters: Dict[str, Any] | None = None,
        firing_trigger_ids: List[str] | None = None,
        paused: bool | None = None,
        google_account: str = "default",
    ) -> Dict[str, Any]:
        """Update an existing tag. Only provided fields are changed."""
        try:
            service = get_auth().get_gtm_service(google_account)
            path = (
                f"accounts/{account_id}/containers/{container_id}"
                f"/workspaces/{workspace_id}/tags/{tag_id}"
            )
            existing = (
                service.accounts()
                .containers()
                .workspaces()
                .tags()
                .get(path=path)
                .execute()
            )
            if name is not None:
                existing["name"] = name
            if parameters is not None:
                existing["parameter"] = _parameters_to_api(parameters)
            if firing_trigger_ids is not None:
                existing["firingTriggerId"] = firing_trigger_ids
            if paused is not None:
                existing["paused"] = paused
            result = (
                service.accounts()
                .containers()
                .workspaces()
                .tags()
                .update(path=path, body=existing)
                .execute()
            )
            return result
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def delete_tag(
        account_id: str,
        container_id: str,
        workspace_id: str,
        tag_id: str,
        google_account: str = "default",
    ) -> Dict[str, Any]:
        """Delete a tag from a workspace."""
        try:
            service = get_auth().get_gtm_service(google_account)
            path = (
                f"accounts/{account_id}/containers/{container_id}"
                f"/workspaces/{workspace_id}/tags/{tag_id}"
            )
            service.accounts().containers().workspaces().tags().delete(path=path).execute()
            return {"deleted": True, "path": path}
        except Exception as exc:
            raise wrap_http_error(exc)
