import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from engine.lesson_planner import LessonPlanner
from engine.scene_planner import ScenePlanner
from engine.animation_planner import AnimationPlanner
from engine.dsl_validator import DSLValidator
from engine.manim_generator import ManimCodeGenerator
from engine.renderer import ManimRenderer
from engine.narration import NarrationGenerator
from engine.ffmpeg_merge import FFmpegMerger
from engine.models import PipelineResult

logger = logging.getLogger(__name__)


class VideoPipeline:
    """End-to-end orchestration pipeline for AI Teaching Engine."""

    def __init__(self, api_key: Optional[str] = None):
        self.lesson_planner = LessonPlanner()
        self.scene_planner = ScenePlanner()
        self.animation_planner = AnimationPlanner()
        self.validator = DSLValidator()
        self.manim_generator = ManimCodeGenerator()
        self.renderer = ManimRenderer()
        self.narration = NarrationGenerator()
        self.merger = FFmpegMerger()

    def run(self, topic: str) -> Dict[str, Any]:
        """
        Executes complete pipeline:
        Lesson Planner (Parameter Extraction & Approach Thinking) -> Scene Planner ->
        Animation Planner -> DSL Validator -> Manim Generator -> Renderer -> Voice Narration -> FFmpeg Merge
        """
        logger.info(f"=== Starting AI Teaching Engine Pipeline for: '{topic}' ===")

        # 1. Lesson Planner & Problem Thinking Phase
        logger.info("Step 1: Analyzing Problem, Extracting Parameters & Formulating Approach...")
        lesson_plan = self.lesson_planner.plan_lesson(topic)
        params = lesson_plan.extracted_parameters
        approach = lesson_plan.approach

        logger.info(f"   [Extracted Topic/Algorithm]: {params.algorithm_or_topic}")
        if params.input_data:
            logger.info(f"   [Parsed Input Dataset]: {params.input_data}")
        if params.target_value is not None:
            logger.info(f"   [Parsed Search Target]: {params.target_value}")

        logger.info("   [Deep Problem Thinking & Approach]:")
        logger.info(f"     • Understanding: {approach.problem_understanding}")
        logger.info(f"     • Strategy: {approach.naive_vs_optimal}")
        for step in approach.step_by_step_execution:
            logger.info(f"     • Execution Step: {step}")
        logger.info(f"     • Complexity: {approach.time_and_space_complexity}")

        # 2. Scene Planner
        logger.info("Step 2: Planning Multi-Scene Presentation...")
        scenes = self.scene_planner.plan_scenes(lesson_plan)
        first_scene = scenes[0]

        # 3. Animation Planner (Produces Animation DSL JSON)
        logger.info("Step 3: Planning Animation DSL JSON...")
        dsl = self.animation_planner.plan_animation(first_scene)

        # 4. DSL Validator
        logger.info("Step 4: Validating Animation DSL...")
        self.validator.validate(dsl)
        logger.info("DSL Validation Successful.")

        # 5. Manim Code Generator (Python converts DSL JSON to Manim Code)
        logger.info("Step 5: Generating Manim Code from DSL...")
        manim_code = self.manim_generator.generate_code(dsl)

        # 6. Manim Renderer (Renders MP4 video)
        logger.info("Step 6: Rendering Manim Scene to MP4...")
        raw_video = self.renderer.render(manim_code)

        # 7. Narration Generator (Generates TTS audio)
        logger.info("Step 7: Generating Voice Narration Audio...")
        narration_audio = self.narration.generate_narration(dsl.voice)

        # 8. FFmpeg Merge (Merges video and voice audio)
        logger.info("Step 8: Merging Video and Narration Audio...")
        final_video = self.merger.merge(raw_video, narration_audio)

        logger.info(f"Pipeline Completed Successfully! Final Output Video: {final_video}")

        return {
            "video": final_video,
            "topic": topic,
            "extracted_parameters": params.model_dump(),
            "approach": approach.model_dump()
        }


def generate_video(topic: str) -> Dict[str, Any]:
    """
    Main entrypoint function requested by specification.
    Returns:
    {
        "video": "output/final.mp4",
        "topic": topic,
        "extracted_parameters": {...},
        "approach": {...}
    }
    """
    pipeline = VideoPipeline()
    return pipeline.run(topic)
