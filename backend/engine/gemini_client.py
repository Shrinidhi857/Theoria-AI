"""
Shared Gemini cascade client.
Tries each model in GEMINI_MODEL_CASCADE order; first successful call wins.
"""

import os
import logging
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


def _classify_error(model: str, e: Exception) -> str:
    """Return a terse, actionable reason for the failure."""
    msg = str(e)
    if "429" in msg or "RESOURCE_EXHAUSTED" in msg:
        return f"quota exceeded on '{model}' — trying next model"
    if "404" in msg or "NOT_FOUND" in msg:
        return f"model '{model}' not available for your API key — trying next model"
    if "401" in msg or "403" in msg:
        return f"authentication error on '{model}' — check GEMINI_API_KEY"
    return f"'{model}' failed: {msg[:80]}"


def gemini_generate(prompt: str, models: list, api_key: Optional[str] = None) -> Optional[str]:
    """
    Call Gemini generateContent with cascade fallback across `models` list.

    Args:
        prompt:   The text prompt to send.
        models:   Ordered list of model IDs to try.
        api_key:  Gemini API key. Falls back to GEMINI_API_KEY env var.

    Returns:
        Response text on first success, or None if all models fail.
    """
    key = api_key or os.getenv("GEMINI_API_KEY")
    if not key:
        logger.warning("⚠️  GEMINI_API_KEY is not set. Set it in .env: GEMINI_API_KEY=AIzaSy...")
        return None

    try:
        from google import genai
    except ImportError:
        logger.warning("⚠️  google-genai package missing. Run: pip install google-genai")
        return None

    client = genai.Client(api_key=key)

    for model in models:
        try:
            logger.info(f"Calling Gemini model: {model}")
            response = client.models.generate_content(
                model=model,
                contents=prompt,
            )
            text = response.text.strip()
            logger.info(f"Model '{model}' responded successfully.")
            return text
        except Exception as e:
            reason = _classify_error(model, e)
            logger.warning(f"⚠️  {reason}")

    logger.warning("⚠️  All Gemini models in cascade failed. Using structured fallback.")
    return None
