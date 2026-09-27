import httpx
import logging
from app.config import settings

logger = logging.getLogger(__name__)

async def notify_new_content(
    creator_name:str,
    content_title:str,
    subscribers:list
):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.NOTIFICATION_SERVICE_URL}/notify/new-content",
                json={
                    "creator_name":creator_name,
                    "creator_title":content_title,
                    "subscribers":subscribers
                },
                timeout=5.0
            )
            return response.json()
    except Exception as e:
        logger.error(f"Notification service error: {e}")
        return None
    
async def notify_new_follower(follower_name:str,creator_email:str):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.NOTIFICATION_SERVICE_URL}/notify/new-follower",
                json={
                    "follower_name":follower_name,
                    "creator_email":creator_email
                },
                timeout=5.0
            )
            return response.json()
    except Exception as e:
        logger.error(f"Notification service error: {e}")
        return None