"""Meta Conversions API (CAPI) server-side event upload tool."""

from __future__ import annotations

import hashlib
import time
from typing import Any, Callable, Dict, List, Optional

from mcp_servers.common.errors import wrap_http_error
from mcp_servers.common.logger import get_server_logger

logger = get_server_logger("ppc-meta.capi")


def _sha256(value: str) -> str:
    return hashlib.sha256(value.strip().lower().encode("utf-8")).hexdigest()


def register(mcp, get_auth: Callable[[], Any]) -> None:
    @mcp.tool()
    def upload_capi_event(
        pixel_id: str,
        event_name: str,
        event_time: Optional[int] = None,
        event_id: Optional[str] = None,
        event_source_url: Optional[str] = None,
        action_source: str = "website",
        user_data: Optional[Dict[str, str]] = None,
        custom_data: Optional[Dict[str, Any]] = None,
        test_event_code: Optional[str] = None,
        account_label: str = "default",
    ) -> Dict[str, Any]:
        """Upload a single Meta CAPI event to a pixel.

        Args:
            pixel_id: Meta pixel ID.
            event_name: Purchase, AddToCart, Lead, etc.
            event_time: Unix seconds; defaults to now.
            event_id: Unique dedup ID that matches the browser pixel event.
            event_source_url: URL of the page where the event happened.
            action_source: website / app / email / phone_call / chat / physical_store / system_generated / other.
            user_data: Raw user identifiers. This tool hashes email/phone/name
                before sending — never send already-hashed values here.
            custom_data: Event-specific data (currency, value, content_ids, ...).
            test_event_code: Meta Events Manager Test Events code (starts with
                ``TEST``). Required for DebugView.
        """
        try:
            from facebook_business.adobjects.serverside.event import Event
            from facebook_business.adobjects.serverside.event_request import EventRequest
            from facebook_business.adobjects.serverside.user_data import UserData
            from facebook_business.adobjects.serverside.custom_data import CustomData

            get_auth().get_meta_api_init(account_label)

            hashed_user_data = UserData()
            if user_data:
                if user_data.get("email"):
                    hashed_user_data.email = _sha256(user_data["email"])
                if user_data.get("phone"):
                    hashed_user_data.phone = _sha256(
                        user_data["phone"].replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
                    )
                if user_data.get("first_name"):
                    hashed_user_data.first_name = _sha256(user_data["first_name"])
                if user_data.get("last_name"):
                    hashed_user_data.last_name = _sha256(user_data["last_name"])
                if user_data.get("city"):
                    hashed_user_data.city = _sha256(user_data["city"])
                if user_data.get("country"):
                    hashed_user_data.country = _sha256(user_data["country"])
                if user_data.get("zip"):
                    hashed_user_data.zip = _sha256(user_data["zip"])
                if user_data.get("client_ip_address"):
                    hashed_user_data.client_ip_address = user_data["client_ip_address"]
                if user_data.get("client_user_agent"):
                    hashed_user_data.client_user_agent = user_data["client_user_agent"]
                if user_data.get("fbc"):
                    hashed_user_data.fbc = user_data["fbc"]
                if user_data.get("fbp"):
                    hashed_user_data.fbp = user_data["fbp"]

            cd = CustomData()
            if custom_data:
                if "currency" in custom_data:
                    cd.currency = custom_data["currency"]
                if "value" in custom_data:
                    cd.value = float(custom_data["value"])
                if "content_ids" in custom_data:
                    cd.content_ids = custom_data["content_ids"]
                if "content_type" in custom_data:
                    cd.content_type = custom_data["content_type"]
                if "num_items" in custom_data:
                    cd.num_items = int(custom_data["num_items"])

            event = Event()
            event.event_name = event_name
            event.event_time = event_time or int(time.time())
            event.event_id = event_id
            event.event_source_url = event_source_url
            event.action_source = action_source
            event.user_data = hashed_user_data
            event.custom_data = cd

            request = EventRequest(
                events=[event],
                pixel_id=pixel_id,
                test_event_code=test_event_code,
            )
            response = request.execute()
            logger.info("Uploaded Meta CAPI event=%s event_id=%s", event_name, event_id)
            return {
                "events_received": response.events_received if hasattr(response, "events_received") else None,
                "messages": list(response.messages) if hasattr(response, "messages") and response.messages else [],
                "fbtrace_id": response.fbtrace_id if hasattr(response, "fbtrace_id") else None,
            }
        except Exception as exc:
            raise wrap_http_error(exc)
