import json
import logging
from typing import List, Optional
from engine.models import LessonPlan, ScenePlan, GEMINI_MODEL_CASCADE
from engine.gemini_client import gemini_generate
from engine.prompts import SCENE_PLANNER_PROMPT

logger = logging.getLogger(__name__)


class ScenePlanner:
    """Stage 2: Converts Lesson Plan and Problem Approach into detailed sequential visual scenes."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    def plan_scenes(self, lesson_plan: LessonPlan) -> List[ScenePlan]:
        prompt = SCENE_PLANNER_PROMPT.format(
            topic=lesson_plan.topic,
            extracted_parameters=lesson_plan.extracted_parameters.model_dump_json(),
            approach=lesson_plan.approach.model_dump_json(),
            presentation_script_outline=lesson_plan.presentation_script_outline
        )

        text = gemini_generate(prompt, models=GEMINI_MODEL_CASCADE, api_key=self.api_key)
        if text:
            try:
                if text.startswith("```"):
                    text = text.strip("`").replace("json", "").strip()
                data = json.loads(text)
                return [ScenePlan(**item) for item in data]
            except Exception as e:
                logger.warning(f"Failed to parse Gemini response as ScenePlan JSON: {e}. Using fallback.")

        # Fallback Scene breakdown using actual extracted parameters
        params = lesson_plan.extracted_parameters
        arr_vals = params.input_data or [1, 3, 5, 7, 9]
        target_val = params.target_value if params.target_value is not None else 7
        arr_str = ", ".join(map(str, arr_vals))

        return [
            ScenePlan(
                scene_number=1,
                title="Problem Statement & Array Setup",
                phase="Problem Setup",
                explanation=f"Show sorted array [{arr_str}] and target {target_val}.",
                visual_description=f"Display array [{arr_str}] centered. Add text header 'Search Target: {target_val}'.",
                voiceover_script=f"Let's solve the problem: search for target {target_val} in the sorted array {arr_str} using Binary Search."
            ),
            ScenePlan(
                scene_number=2,
                title="Pointer Initialization & Middle Element Comparison",
                phase="Approach Walkthrough",
                explanation=f"Set low=0, high={len(arr_vals)-1}, compute mid index. Compare mid element with target {target_val}.",
                visual_description=f"Place low pointer at index 0, high pointer at index {len(arr_vals)-1}, mid pointer at index {len(arr_vals)//2}. Highlight middle value in yellow.",
                voiceover_script=f"We set low at index 0 and high at index {len(arr_vals)-1}. The middle index is {len(arr_vals)//2} with value {arr_vals[len(arr_vals)//2]}. We compare this middle value with our target {target_val}."
            ),
            ScenePlan(
                scene_number=3,
                title="State Transition & Target Match",
                phase="Conclusion",
                explanation=f"Move pointers until index containing target {target_val} is located.",
                visual_description=f"Move pointers to target index. Highlight matching target element {target_val} in green.",
                voiceover_script=f"We adjust our search space and locate target {target_val}. Binary Search finishes efficiently in logarithmic time."
            )
        ]
