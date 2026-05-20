"""Meta ad image management tools."""

from __future__ import annotations

from typing import Any, Callable, Dict, List

from mcp_servers.common.errors import wrap_http_error
from mcp_servers.common.logger import get_server_logger

logger = get_server_logger("ppc-meta.images")


def register(mcp, get_auth: Callable[[], Any]) -> None:
    @mcp.tool()
    def upload_image(
        ad_account_id: str,
        image_url: str,
        name: str = "",
        account_label: str = "default",
    ) -> Dict[str, Any]:
        """Upload an ad image to the Meta ad account image library.

        Args:
            image_url: Public URL of the image. Meta will fetch and store it.
            name: Optional descriptive name for the image.

        Returns the image hash that can be used with ``create_creative``.
        """
        try:
            from facebook_business.adobjects.adaccount import AdAccount
            from facebook_business.adobjects.adimage import AdImage

            get_auth().get_meta_api_init(account_label)
            if not ad_account_id.startswith("act_"):
                ad_account_id = f"act_{ad_account_id}"

            # Download image and upload as bytes
            import httpx
            import base64
            import tempfile
            import os

            resp = httpx.get(image_url, follow_redirects=True, timeout=30)
            resp.raise_for_status()

            # Write to temp file for SDK upload
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                tmp.write(resp.content)
                tmp_path = tmp.name

            try:
                account = AdAccount(ad_account_id)
                image = AdImage(parent_id=ad_account_id)
                image[AdImage.Field.filename] = tmp_path
                if name:
                    image[AdImage.Field.name] = name
                image.remote_create()
                result = {
                    "hash": image.get("hash"),
                    "url": image.get("url"),
                    "name": name or image.get("name"),
                }
            finally:
                os.unlink(tmp_path)

            logger.info("Uploaded image '%s' hash=%s", name, result.get("hash"))
            return result
        except Exception as exc:
            raise wrap_http_error(exc)

    @mcp.tool()
    def list_images(
        ad_account_id: str,
        limit: int = 100,
        account_label: str = "default",
    ) -> Dict[str, Any]:
        """List all images in a Meta ad account's image library."""
        try:
            from facebook_business.adobjects.adaccount import AdAccount

            get_auth().get_meta_api_init(account_label)
            if not ad_account_id.startswith("act_"):
                ad_account_id = f"act_{ad_account_id}"
            account = AdAccount(ad_account_id)
            images = account.get_ad_images(
                fields=[
                    "id",
                    "account_id",
                    "hash",
                    "name",
                    "url",
                    "url_128",
                    "permalink_url",
                    "height",
                    "width",
                    "status",
                    "created_time",
                ],
                params={"limit": limit},
            )
            return {
                "count": len(images),
                "images": [dict(img) for img in images],
            }
        except Exception as exc:
            raise wrap_http_error(exc)
