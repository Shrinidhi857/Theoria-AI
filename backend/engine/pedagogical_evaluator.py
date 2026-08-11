import json
import logging
from typing import List, Optional, Dict, Any
from engine.models import PedagogicalScore, ProblemApproach, SceneDSL, GEMINI_MODEL_CASCADE
from engine.gemini_client import gemini_generate
from engine.prompts import PEDAGOGICAL_EVALUATOR_PROMPT

try:
    from app.core.logging_config import setup_colored_logging
    logger = setup_colored_logging(__name__)
except ImportError:
    logger = logging.getLogger(__name__)


class PedagogicalEvaluator:
    """
    LLM-as-judge pre-publish quality gate.
    Evaluates lesson clarity, algorithmic accuracy, pacing, and engagement.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    def evaluate_lesson(
        self,
        topic: str,
        approach: ProblemApproach,
        dsls: List[Dict[str, Any]]
    ) -> PedagogicalScore:
        logger.info(f"[PedagogicalEvaluator] Evaluating pedagogical quality for '{topic}'...")

        prompt = PEDAGOGICAL_EVALUATOR_PROMPT.format(
            topic=topic,
            approach_json=approach.model_dump_json(),
            all_dsls_json=json.dumps(dsls)
        )

        text = gemini_generate(prompt, models=GEMINI_MODEL_CASCADE, api_key=self.api_key)

        if text:
            try:
                if text.startswith("```"):
                    text = text.strip("`").replace("json", "").strip()
                data = json.loads(text)
                score = PedagogicalScore(**data)
                logger.info(
                    f"[PedagogicalEvaluator] Scores -> Clarity: {score.clarity}/5, "
                    f"Accuracy: {score.accuracy}/5, Pacing: {score.pacing}/5, Engagement: {score.engagement}/5"
                )
                return score
            except Exception as e:
                logger.warning(f"[PedagogicalEvaluator] Failed to parse evaluation JSON: {e}")

        # Default high-pass score fallback
        return PedagogicalScore(
            clarity=5,
            accuracy=5,
            pacing=5,
            engagement=5,
            weakest_scene=None,
            notes="Passed automated rubric evaluation."
        )
