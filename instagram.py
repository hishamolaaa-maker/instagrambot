import httpx
import asyncio
import logging
import os
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

GRAPH_API_BASE = "https://graph.facebook.com/v19.0"

def get_access_token(db=None):
    """Get access token from DB config or env fallback."""
    if db:
        from models import Config
        config = db.query(Config).first()
        if config and config.access_token:
            return config.access_token
    return os.getenv("INSTAGRAM_ACCESS_TOKEN", "")

async def _api_call(method: str, url: str, retries=3, **kwargs):
    """Make an API call with retry/backoff on rate limits."""
    async with httpx.AsyncClient(timeout=30) as client:
        for attempt in range(retries):
            try:
                if method == "GET":
                    response = await client.get(url, **kwargs)
                else:
                    response = await client.post(url, **kwargs)

                logger.info(f"[Instagram API] {method} {url} → {response.status_code}")

                if response.status_code == 429:
                    wait = 2 ** attempt * 5
                    logger.warning(f"Rate limited. Waiting {wait}s before retry...")
                    await asyncio.sleep(wait)
                    continue

                response.raise_for_status()
                return response.json()

            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
                if attempt == retries - 1:
                    raise
            except Exception as e:
                logger.error(f"Request error: {e}")
                if attempt == retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)

async def reply_to_comment(comment_id: str, message: str, access_token: str) -> dict:
    """Post a public reply to an Instagram comment."""
    url = f"{GRAPH_API_BASE}/{comment_id}/replies"
    data = await _api_call("POST", url, params={
        "message": message,
        "access_token": access_token
    })
    logger.info(f"Replied to comment {comment_id}: {data}")
    return data

async def send_dm(instagram_user_id: str, message: str, page_id: str, access_token: str) -> dict:
    """Send a private DM to an Instagram user via the Messaging API."""
    url = f"{GRAPH_API_BASE}/{page_id}/messages"
    payload = {
        "recipient": {"id": instagram_user_id},
        "message": {"text": message},
        "messaging_type": "RESPONSE",
        "access_token": access_token
    }
    data = await _api_call("POST", url, json=payload)
    logger.info(f"DM sent to user {instagram_user_id}: {data}")
    return data

async def get_post_details(post_id: str, access_token: str) -> dict:
    """Fetch post thumbnail URL and caption from Instagram Graph API."""
    url = f"{GRAPH_API_BASE}/{post_id}"
    data = await _api_call("GET", url, params={
        "fields": "id,caption,thumbnail_url,media_url,media_type,timestamp",
        "access_token": access_token
    })
    return {
        "id": data.get("id"),
        "caption": data.get("caption", ""),
        "thumbnail": data.get("thumbnail_url") or data.get("media_url", ""),
        "media_type": data.get("media_type", ""),
        "timestamp": data.get("timestamp", "")
    }

async def verify_token_valid(access_token: str) -> bool:
    """Check if the access token is valid."""
    try:
        url = f"{GRAPH_API_BASE}/me"
        data = await _api_call("GET", url, params={"access_token": access_token})
        return "id" in data
    except Exception:
        return False
