import re
import httpx
import logging

from src.config.settings import settings

logger = logging.getLogger(__name__)

EXOTEL_PLACEHOLDERS = {
    "your_api_key",
    "your_api_token",
    "your_sid",
    "your_exophone",
    "your_app_id",
}


def normalize_phone_number(phone_number: str) -> str:
    """Strip spaces/dashes; prefer E.164 for India (+91...)."""
    cleaned = re.sub(r"[^\d+]", "", phone_number.strip())
    if cleaned.startswith("+"):
        return cleaned
    if cleaned.startswith("00"):
        return "+" + cleaned[2:]
    if cleaned.startswith("91") and len(cleaned) == 12:
        return f"+{cleaned}"
    if len(cleaned) == 10:
        return f"+91{cleaned}"
    return cleaned


class ExotelService:
    def __init__(self):
        self.api_key = settings.EXOTEL_API_KEY
        self.api_token = settings.EXOTEL_API_TOKEN
        self.sid = settings.EXOTEL_SID
        self.subdomain = settings.EXOTEL_SUBDOMAIN
        self.caller_id = settings.EXOTEL_CALLER_ID
        self.app_id = settings.EXOTEL_APP_ID

        self.base_url = (
            f"https://{self.subdomain}/v1/Accounts/{self.sid}/Calls/connect.json"
        )

    def _ensure_configured(self):
        values = [
            self.api_key,
            self.api_token,
            self.sid,
            self.caller_id,
            self.app_id,
        ]
        if any(not v or v in EXOTEL_PLACEHOLDERS for v in values):
            raise Exception(
                "Exotel is not configured. Add real EXOTEL_API_KEY, EXOTEL_API_TOKEN, "
                "EXOTEL_SID, EXOTEL_CALLER_ID, and EXOTEL_APP_ID in backend/.env"
            )

    async def trigger_outbound_call(self, phone_number: str, customer_name: str):
        self._ensure_configured()
        to_number = normalize_phone_number(phone_number)

        if len(to_number) < 10:
            raise Exception("Invalid phone number. Use format +919876543210")

        payload = {
            "From": to_number,
            "CallerId": self.caller_id,
            "Url": f"http://my.exotel.com/{self.sid}/exoml/start_voice/{self.app_id}",
            "CustomField": customer_name,
            "StatusCallback": f"{settings.BASE_URL}/api/v1/calls/webhooks/exotel",
        }

        async with httpx.AsyncClient() as client:
            try:
                logger.info("Triggering Exotel call to %s", to_number)
                response = await client.post(
                    self.base_url,
                    data=payload,
                    auth=(self.api_key, self.api_token),
                )
                response.raise_for_status()
                data = response.json()
                logger.info(
                    "Exotel call triggered successfully: %s",
                    data.get("Call", {}).get("Sid"),
                )
                return data
            except httpx.HTTPStatusError as e:
                logger.error("Exotel API error: %s", e.response.text)
                raise Exception(f"Exotel rejected the call: {e.response.text}")
            except Exception as e:
                logger.error("Unexpected error triggering Exotel call: %s", e)
                raise

exotel_service = ExotelService()
