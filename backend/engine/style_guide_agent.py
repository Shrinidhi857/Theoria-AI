import json
import logging
from typing import Optional
from engine.models import StyleGuide, GEMINI_MODEL_CASCADE
from engine.gemini_client import gemini_generate
from engine.prompts import STYLE_GUIDE_PROMPT

try:
    from app.core.logging_config import setup_colored_logging
    logger = setup_colored_logging(__name__)
except ImportError:
    logger = logging.getLogger(__name__)


class StyleGuideAgent:
    """
    Formulates a cohesive visual style guide (palette, fonts, pointer colors)
    before scene fan-out to guarantee visual consistency across parallel scenes.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    def generate_style_guide(self, topic: str) -> StyleGuide:
        prompt = STYLE_GUIDE_PROMPT.format(topic=topic)
        text = gemini_generate(prompt, models=GEMINI_MODEL_CASCADE, api_key=self.api_key)

        if text:
            try:
                if text.startswith("```"):
                    text = text.strip("`").replace("json", "").strip()
                data = json.loads(text)
                return StyleGuide(**data)
            except Exception as e:
                logger.warning(f"[StyleGuideAgent] Failed to parse StyleGuide JSON: {e}. Using default style contract.")

        return StyleGuide()
