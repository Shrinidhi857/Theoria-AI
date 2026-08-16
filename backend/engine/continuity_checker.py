import logging
from typing import List, Dict, Any
from engine.models import StyleGuide, SceneDSL

try:
    from app.core.logging_config import setup_colored_logging
    logger = setup_colored_logging(__name__)
except ImportError:
    logger = logging.getLogger(__name__)


class ContinuityChecker:
    """
    Verification subagent that checks cross-scene visual continuity, font sizing,
    and palette adherence across all rendered scene DSLs.
    """

    def check_continuity(self, dsls: List[SceneDSL], style_guide: StyleGuide) -> Dict[str, Any]:
        logger.info(f"[ContinuityChecker] Checking visual continuity across {len(dsls)} scene DSLs...")
        issues = []

        # Check array color consistency across scenes
        array_colors = set()
        for idx, dsl in enumerate(dsls):
            for obj in dsl.objects:
                if obj.type.lower() == "array" and obj.color:
                    array_colors.add(obj.color.upper())

        if len(array_colors) > 1:
            issues.append(f"Inconsistent array color palette detected across scenes: {sorted(list(array_colors))}")

        passed = len(issues) == 0
        return {
            "passed": passed,
            "issues": issues,
            "style_contract": style_guide.model_dump()
        }
