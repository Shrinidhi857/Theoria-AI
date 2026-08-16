"""
Shared Gemini cascade client.
Tries each model in GEMINI_MODEL_CASCADE order; first successful call wins.
Supports primary and backup API keys (GEMINI_API_KEY and GEMINI_API_KEY_BACKUP) if quota is exhausted.
"""

import os
import logging
from typing import Optional, List, Any
from dotenv import load_dotenv

load_dotenv()

try:
    from app.core.logging_config import setup_colored_logging
    logger = setup_colored_logging(__name__)
except ImportError:
    logger = logging.getLogger(__name__)


def _mask_key(key: str) -> str:
    if not key:
        return ""
    if len(key) > 10:
        return f"{key[:6]}...{key[-4:]}"
    return "***"


def _classify_error(model: str, e: Exception) -> str:
    """Return a terse, actionable reason for the failure."""
    msg = str(e)
    if "429" in msg or "RESOURCE_EXHAUSTED" in msg:
        return f"quota exceeded on '{model}'"
    if "404" in msg or "NOT_FOUND" in msg:
        return f"model '{model}' not available for this API key"
    if "401" in msg or "403" in msg:
        return f"authentication error on '{model}' — check API key"
    return f"'{model}' failed: {msg[:80]}"


def gemini_generate(prompt: str, models: list, api_key: Optional[str] = None) -> Optional[str]:
    """
    Call Gemini generateContent with cascade fallback across `models` list and candidate API keys.

    Args:
        prompt:   The text prompt to send.
        models:   Ordered list of model IDs to try.
        api_key:  Gemini API key override. Falls back to GEMINI_API_KEY env var.

    Returns:
        Response text on first success, or None if all keys & models fail.
    """
    keys_to_try: List[str] = []
    
    primary = api_key or os.getenv("GEMINI_API_KEY")
    if primary:
        keys_to_try.append(primary)
        
    backup = os.getenv("GEMINI_API_KEY_BACKUP")
    if backup and backup not in keys_to_try:
        keys_to_try.append(backup)

    if not keys_to_try:
        logger.warning("⚠️  No GEMINI_API_KEY or GEMINI_API_KEY_BACKUP set in .env")
        return None

    try:
        from google import genai
    except ImportError:
        logger.warning("⚠️  google-genai package missing. Run: pip install google-genai")
        return None

    for k_idx, key in enumerate(keys_to_try):
        is_backup = (k_idx > 0)
        key_label = f"Backup key ({_mask_key(key)})" if is_backup else f"Primary key ({_mask_key(key)})"
        
        try:
            client = genai.Client(api_key=key)
        except Exception as e:
            logger.warning(f"⚠️  Failed to initialize Gemini client with {key_label}: {e}")
            continue

        for model in models:
            try:
                logger.info(f"Calling Gemini model '{model}' using {key_label}...")
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                )
                text = response.text.strip()
                logger.info(f"Model '{model}' responded successfully via {key_label}.")
                return text
            except Exception as e:
                reason = _classify_error(model, e)
                logger.warning(f"⚠️  [{key_label}] {reason}")

        if k_idx < len(keys_to_try) - 1:
            logger.warning(f"⚠️  All models failed for {key_label}. Switching to backup API key...")

    logger.warning("⚠️  All Gemini models and API keys in cascade failed. Using structured fallback.")
    return None


def gemini_generate_vision(
    prompt: str,
    images: List[Any],
    models: list,
    api_key: Optional[str] = None
) -> Optional[str]:
    """
    Call Gemini generateContent with vision capability (text + images) across cascade.

    Args:
        prompt:  Text prompt describing visual check.
        images:  List of PIL Image objects or image bytes.
        models:  Ordered list of model IDs to try.
        api_key: Gemini API key override.

    Returns:
        Response text on success, or None on failure.
    """
    keys_to_try: List[str] = []
    primary = api_key or os.getenv("GEMINI_API_KEY")
    if primary:
        keys_to_try.append(primary)
    backup = os.getenv("GEMINI_API_KEY_BACKUP")
    if backup and backup not in keys_to_try:
        keys_to_try.append(backup)

    if not keys_to_try:
        return None

    try:
        from google import genai
        from google.genai import types
    except ImportError:
        logger.warning("⚠️  google-genai package missing.")
        return None

    contents = [prompt] + images

    for k_idx, key in enumerate(keys_to_try):
        try:
            client = genai.Client(api_key=key)
        except Exception:
            continue

        for model in models:
            try:
                logger.info(f"Calling Gemini Vision model '{model}' with {len(images)} keyframe image(s)...")
                response = client.models.generate_content(
                    model=model,
                    contents=contents,
                )
                text = response.text.strip()
                logger.info(f"Gemini Vision model '{model}' responded successfully.")
                return text
            except Exception as e:
                reason = _classify_error(model, e)
                logger.warning(f"⚠️  Vision call failed on '{model}': {reason}")

    return None

