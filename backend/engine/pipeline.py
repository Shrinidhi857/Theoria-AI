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
        
        scene_videos = []
        all_dsls = []
        all_manim_code = []
        
        for idx, scene in enumerate(scenes):
            scene_number = scene.scene_number or (idx + 1)
            logger.info(f"=== Processing Scene {scene_number} / {len(scenes)}: {scene.title} ===")
            
            # 3. Animation Planner (Produces Animation DSL JSON)
            logger.info(f"Step 3: Planning Animation DSL JSON for Scene {scene_number}...")
            dsl = self.animation_planner.plan_animation(scene)
            all_dsls.append(dsl.model_dump())
            
            # 4. DSL Validator
            logger.info(f"Step 4: Validating Animation DSL for Scene {scene_number}...")
            try:
                self.validator.validate(dsl)
                logger.info(f"DSL Validation Successful for Scene {scene_number}.")
            except Exception as val_err:
                logger.warning(f"DSL Validation failed for Scene {scene_number}: {val_err}. Proceeding best-effort.")
            
            # 5. Manim Code Generator (Python converts DSL JSON to Manim Code)
            logger.info(f"Step 5: Generating Manim Code from DSL for Scene {scene_number}...")
            manim_code = self.manim_generator.generate_code(dsl)
            all_manim_code.append(manim_code)
            
            # 6. Manim Renderer (Renders MP4 video)
            logger.info(f"Step 6: Rendering Manim Scene {scene_number} to MP4...")
            raw_video_filename = f"manim_raw_scene_{scene_number}.mp4"
            raw_video = self.renderer.render(manim_code, output_filename=raw_video_filename)
            
            # 7. Narration Generator (Generates TTS audio)
            logger.info(f"Step 7: Generating Voice Narration Audio for Scene {scene_number}...")
            narration_audio_filename = f"narration_scene_{scene_number}.mp3"
            narration_audio = self.narration.generate_narration(dsl.voice, filename=narration_audio_filename)
            
            # 8. FFmpeg Merge (Merges video and voice audio for this scene)
            logger.info(f"Step 8: Merging Video and Narration Audio for Scene {scene_number}...")
            merged_video_filename = f"merged_scene_{scene_number}.mp4"
            merged_scene_video = self.merger.merge(raw_video, narration_audio, output_filename=merged_video_filename)
            
            scene_videos.append(merged_scene_video)

        # 9. Concat all scene videos into a final output video
        logger.info(f"=== Concatenating {len(scene_videos)} scene videos into final.mp4 ===")
        final_video = self.merger.concat_videos(scene_videos, output_filename="final.mp4")
        
        logger.info(f"Pipeline Completed Successfully! Final Combined Video: {final_video}")

        return {
            "video": final_video,
            "topic": topic,
            "extracted_parameters": params.model_dump(),
            "approach": approach.model_dump(),
            "dsl_code": all_dsls,
            "manim_code": "\n\n# --- SCENE SEPARATOR ---\n\n".join(all_manim_code)
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
