import json
import re
import logging
from typing import Optional
from engine.models import ScenePlan, SceneDSL, DSLObject, DSLAnimation, GEMINI_MODEL_CASCADE
from engine.gemini_client import gemini_generate
from engine.prompts import ANIMATION_PLANNER_PROMPT

logger = logging.getLogger(__name__)


class AnimationPlanner:
    """Stage 3: Converts a ScenePlan into a strictly defined Animation DSL JSON."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    def plan_animation(self, scene_plan: ScenePlan) -> SceneDSL:
        prompt = ANIMATION_PLANNER_PROMPT.format(
            title=scene_plan.title,
            phase=scene_plan.phase,
            explanation=scene_plan.explanation,
            visual_description=scene_plan.visual_description,
            voiceover_script=scene_plan.voiceover_script
        )

        text = gemini_generate(prompt, models=GEMINI_MODEL_CASCADE, api_key=self.api_key)
        if text:
            try:
                if text.startswith("```"):
                    text = text.strip("`").replace("json", "").strip()
                data = json.loads(text)
                return SceneDSL(**data)
            except Exception as e:
                logger.warning(f"Failed to parse Gemini response as SceneDSL JSON: {e}. Using fallback DSL.")

        # Fallback DSL: Extract numbers or default to [1, 3, 5, 7, 9] and target 7
        nums = [int(n) for n in re.findall(r'\b\d+\b', scene_plan.explanation + " " + scene_plan.visual_description)]
        arr_vals = [1, 3, 5, 7, 9]
        target_val = 7

        if len(nums) >= 2:
            target_val = nums[-1]
            arr_vals = nums[:-1]

        target_idx = 3
        if target_val in arr_vals:
            target_idx = arr_vals.index(target_val)

        mid_idx = len(arr_vals) // 2

        return SceneDSL(
            scene_title=scene_plan.title,
            objects=[
                DSLObject(
                    id="target_txt",
                    type="text",
                    text=f"Search Target: {target_val}",
                    color="GREEN",
                    position=[0.0, 2.0, 0.0]
                ),
                DSLObject(
                    id="array1",
                    type="array",
                    values=arr_vals,
                    position=[0.0, 0.5, 0.0],
                    color="BLUE"
                ),
                DSLObject(
                    id="mid_ptr",
                    type="pointer",
                    label="mid",
                    position=[0.0, -1.2, 0.0],
                    color="YELLOW"
                )
            ],
            animations=[
                DSLAnimation(type="FadeIn", target="target_txt", duration=0.8),
                DSLAnimation(type="FadeIn", target="array1", duration=1.0),
                DSLAnimation(type="FadeIn", target="mid_ptr", duration=0.8),
                DSLAnimation(type="Highlight", target="array1", index=mid_idx, color="YELLOW", duration=1.2),
                DSLAnimation(type="MovePointer", pointer="mid_ptr", to=target_idx, duration=1.0),
                DSLAnimation(type="Highlight", target="array1", index=target_idx, color="GREEN", duration=1.5),
                DSLAnimation(type="Wait", duration=1.0)
            ],
            voice=scene_plan.voiceover_script or f"Searching for target {target_val} in array."
        )
