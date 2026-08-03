import logging
from typing import Optional, Dict, Any
import httpx
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from app.core.config import settings

logger = logging.getLogger(__name__)


def verify_google_id_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify Google OAuth ID Token string directly using google-auth library.
    Returns user payload dictionary (email, sub, name, picture) if valid, or None.
    """
    try:
        request = google_requests.Request()
        client_id = settings.GOOGLE_CLIENT_ID if settings.GOOGLE_CLIENT_ID else None
        
        # Verify token
        id_info = id_token.verify_oauth2_token(token, request, audience=client_id)
        
        return {
            "google_id": id_info.get("sub"),
            "email": id_info.get("email"),
            "full_name": id_info.get("name"),
            "avatar_url": id_info.get("picture"),
            "email_verified": id_info.get("email_verified", True)
        }
    except Exception as e:
        logger.warning(f"Google ID Token verification failed: {e}")
        return None


async def verify_google_user_from_token_or_auth_code(token_or_code: str) -> Optional[Dict[str, Any]]:
    """
    Attempts to verify as a Google ID token first. If it fails, checks if it's an access token
    or authorization code to exchange/verify against Google API.
    """
    # 1. Try ID Token verification first
    result = verify_google_id_token(token_or_code)
    if result:
        return result

    # 2. Try fetching Google UserInfo with access token via httpx
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://www.googleapis.com/oauth2/v3/userinfo",
                headers={"Authorization": f"Bearer {token_or_code}"},
                timeout=10.0
            )
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "google_id": data.get("sub"),
                    "email": data.get("email"),
                    "full_name": data.get("name"),
                    "avatar_url": data.get("picture"),
                    "email_verified": data.get("email_verified", True)
                }
    except Exception as e:
        logger.warning(f"Failed to fetch Google userinfo with access token: {e}")

    return None
