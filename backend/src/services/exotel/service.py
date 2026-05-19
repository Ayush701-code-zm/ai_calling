import httpx
import logging
from src.config.settings import settings

logger = logging.getLogger(__name__)

class ExotelService:
    def __init__(self):
        self.api_key = settings.EXOTEL_API_KEY
        self.api_token = settings.EXOTEL_API_TOKEN
        self.sid = settings.EXOTEL_SID
        self.subdomain = settings.EXOTEL_SUBDOMAIN
        self.caller_id = settings.EXOTEL_CALLER_ID
        self.app_id = settings.EXOTEL_APP_ID
        
        self.base_url = f"https://{self.api_key}:{self.api_token}@{self.subdomain}/v1/Accounts/{self.sid}/Calls/connect.json"

    async def trigger_outbound_call(self, phone_number: str, customer_name: str):
        async with httpx.AsyncClient() as client:
            payload = {
                "From": phone_number,
                "CallerId": self.caller_id,
                "Url": f"http://my.exotel.com/{self.sid}/exoml/start_voice/{self.app_id}",
                "CustomField": customer_name,
                "StatusCallback": f"{settings.BASE_URL}/api/v1/webhooks/exotel"
            }
            
            try:
                logger.info(f"Triggering Exotel call to {phone_number}")
                response = await client.post(self.base_url, data=payload)
                response.raise_for_status()
                data = response.json()
                logger.info(f"Exotel call triggered successfully: {data.get('Call', {}).get('Sid')}")
                return data
            except httpx.HTTPStatusError as e:
                logger.error(f"Exotel API error: {e.response.text}")
                raise Exception(f"Failed to trigger Exotel call: {e.response.text}")
            except Exception as e:
                logger.error(f"Unexpected error triggering Exotel call: {e}")
                raise

exotel_service = ExotelService()
