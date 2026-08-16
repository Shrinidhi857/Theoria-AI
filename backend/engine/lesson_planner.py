import json
import re
import logging
from typing import Optional, List, Dict, Any
from engine.models import (
    LessonPlan,
    ExtractedParameters,
    ProblemApproach,
    KnowledgeMetadata,
    GEMINI_MODEL_CASCADE
)
from engine.gemini_client import gemini_generate
from engine.prompts import LESSON_PLANNER_PROMPT

try:
    from app.core.logging_config import setup_colored_logging
    logger = setup_colored_logging(__name__)
except ImportError:
    logger = logging.getLogger(__name__)


def _extract_params_from_topic(topic: str) -> ExtractedParameters:
    """Helper to extract numbers/target dynamically from prompt if available."""
    # Find numbers in topic like "array 1 3 5 7 9 and search 7" or "[1, 3, 5, 7, 9]"
    nums = [int(n) for n in re.findall(r'\b\d+\b', topic)]
    
    target_val = None
    target_match = re.search(r'(?:search|find|target)\s+(\d+)', topic, re.IGNORECASE)
    if target_match:
        target_val = int(target_match.group(1))

    if nums:
        # If target was found, remove it from array values if it was at the very end
        input_data = nums
        if target_val is not None and nums and nums[-1] == target_val and len(nums) > 1:
            input_data = nums[:-1]
        elif target_val is None and len(nums) > 1:
            target_val = nums[-1]
            input_data = nums[:-1]
    else:
        input_data = [1, 3, 5, 7, 9]
        target_val = 7

    algo_name = "Binary Search"
    if "merge" in topic.lower():
        algo_name = "Merge Sort"
    elif "dijkstra" in topic.lower():
        algo_name = "Dijkstra's Algorithm"
    elif "recursion" in topic.lower():
        algo_name = "Recursion"

    return ExtractedParameters(
        algorithm_or_topic=algo_name,
        input_data=input_data,
        target_value=target_val,
        problem_type="LeetCode / Algorithmic Walkthrough"
    )


class LessonPlanner:
    """Stage 1: Analyzes teaching request, extracts parameters, and formulates problem approach & lesson plan."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    def plan_lesson(self, topic: str, graph_context: Optional[str] = None) -> LessonPlan:
        ctx_str = f"\n{graph_context}\n" if graph_context else ""
        prompt = LESSON_PLANNER_PROMPT.format(topic=topic, graph_context=ctx_str)

        text = gemini_generate(prompt, models=GEMINI_MODEL_CASCADE, api_key=self.api_key)
        if text:
            try:
                if text.startswith("```"):
                    text = text.strip("`").replace("json", "").strip()
                data = json.loads(text)
                return LessonPlan(**data)
            except Exception as e:
                logger.warning(f"Failed to parse Gemini response as LessonPlan JSON: {e}. Using structured fallback.")

        # Structured Fallback with Dynamic Parameter Extraction
        params = _extract_params_from_topic(topic)
        input_str = ", ".join(map(str, params.input_data)) if params.input_data else "1, 3, 5, 7, 9"
        target_str = str(params.target_value) if params.target_value is not None else "7"

        return LessonPlan(
            topic=topic,
            extracted_parameters=params,
            approach=ProblemApproach(
                problem_understanding=f"Search for target {target_str} in sorted array [{input_str}] using {params.algorithm_or_topic}.",
                naive_vs_optimal=f"Brute force inspects elements sequentially in O(n) time. {params.algorithm_or_topic} eliminates half the search space each step in O(log n) time.",
                step_by_step_execution=[
                    f"1. Initialize low=0, high={len(params.input_data)-1 if params.input_data else 4}.",
                    f"2. Compute mid index, check if array[mid] == {target_str}.",
                    f"3. Adjust pointers based on comparison until target {target_str} is located."
                ],
                time_and_space_complexity="Time Complexity: O(log n), Space Complexity: O(1)."
            ),
            overview=f"Visual step-by-step breakdown of {params.algorithm_or_topic} operating on input [{input_str}] for target {target_str}.",
            learning_objectives=[
                f"Understand search space reduction in {params.algorithm_or_topic}.",
                f"Trace pointer state transitions to locate target {target_str}."
            ],
            presentation_script_outline=[
                f"Introduce problem: Search for {target_str} in array [{input_str}].",
                "Set low, high, and compute mid index.",
                "Compare middle value against target and adjust pointers.",
                f"Target {target_str} found! Summarize complexity."
            ],
            knowledge_metadata=KnowledgeMetadata(
                primary_concept=params.algorithm_or_topic,
                concepts=["Algorithms", "Searching"],
                algorithms=[params.algorithm_or_topic],
                data_structures=["Array"],
                prerequisites=["Array", "Sorting"],
                related_concepts=["Linear Search", "Two Pointer"],
                complexity=["O(log n)", "O(1)"]
            )
        )

