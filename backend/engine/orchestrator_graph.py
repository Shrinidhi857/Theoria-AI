import os
import asyncio
import logging
from typing import Dict, Any, List, Optional, TypedDict

from engine.models import (
    LessonPlan, ScenePlan, SceneDSL, StyleGuide,
    PedagogicalScore, RepairTranscript, VisualQAReport
)
from engine.lesson_planner import LessonPlanner
from engine.scene_planner import ScenePlanner
from engine.animation_planner import AnimationPlanner
from engine.dsl_validator import DSLValidator
from engine.repair_agent import RenderRepairAgent
from engine.visual_qa_agent import VisualQAAgent
from engine.style_guide_agent import StyleGuideAgent
from engine.continuity_checker import ContinuityChecker
from engine.narration import NarrationGenerator
from engine.ffmpeg_merge import FFmpegMerger
from engine.pedagogical_evaluator import PedagogicalEvaluator

try:
    from app.core.logging_config import setup_colored_logging
    logger = setup_colored_logging(__name__)
except ImportError:
    logger = logging.getLogger(__name__)


class EngineState(TypedDict):
    topic: str
    user_id: Optional[int]
    graph_context: str
    lesson_plan: Optional[LessonPlan]
    scenes: List[ScenePlan]
    style_guide: Optional[StyleGuide]
    scene_videos: List[str]
    all_dsls: List[Dict[str, Any]]
    all_manim_code: List[str]
    transcripts: List[RepairTranscript]
    qa_reports: List[VisualQAReport]
    final_video: str
    pedagogical_score: Optional[PedagogicalScore]


class EngineOrchestrator:
    """
    Multi-Agent Graph Orchestrator for AI Teaching Engine.
    Executes scene fan-out in parallel (bounded by Semaphore(3)), self-healing render repair loops,
    multimodal visual QA checks, and pedagogical pre-publish evaluation.
    """

    def __init__(self, api_key: Optional[str] = None, concurrency_limit: int = 3):
        self.api_key = api_key
        self.semaphore = asyncio.Semaphore(concurrency_limit)
        
        self.lesson_planner = LessonPlanner(api_key=api_key)
        self.scene_planner = ScenePlanner(api_key=api_key)
        self.animation_planner = AnimationPlanner(api_key=api_key)
        self.validator = DSLValidator()
        self.repair_agent = RenderRepairAgent(api_key=api_key)
        self.visual_qa_agent = VisualQAAgent(api_key=api_key)
        self.style_guide_agent = StyleGuideAgent(api_key=api_key)
        self.continuity_checker = ContinuityChecker()
        self.narration_generator = NarrationGenerator()
        self.merger = FFmpegMerger()
        self.pedagogical_evaluator = PedagogicalEvaluator(api_key=api_key)

    async def _process_single_scene(self, scene: ScenePlan, idx: int, total_scenes: int, style_guide: StyleGuide) -> Dict[str, Any]:
        """Processes a single scene within the parallel semaphore ceiling."""
        async with self.semaphore:
            scene_number = scene.scene_number or (idx + 1)
            logger.info(f"🎥 [Scene {scene_number}/{total_scenes}] Starting parallel worker — '{scene.title}'")

            # 1. Animation Planner (DSL JSON)
            logger.info(f"🎨 [Scene {scene_number}] Generating Animation DSL...")
            dsl = self.animation_planner.plan_animation(scene)

            # Apply StyleGuide color preference if default
            if dsl.objects and style_guide:
                for obj in dsl.objects:
                    if obj.type.lower() == "pointer" and style_guide.pointer_color:
                        obj.color = style_guide.pointer_color

            # 2. DSL Validator
            logger.info(f"🔍 [Scene {scene_number}] Validating Animation DSL...")
            try:
                self.validator.validate(dsl)
                logger.info(f"✅ [Scene {scene_number}] DSL validation passed.")
            except Exception as val_err:
                logger.warning(f"⚠️  [Scene {scene_number}] DSL validation warning: {val_err}")

            # 3. Render & Repair Agent (RITL Loop, max 3 attempts)
            logger.info(f"🔧 [Scene {scene_number}] Starting Render & Repair Agent (RITL loop, max 3 attempts)...")
            raw_video, manim_code, transcript = self.repair_agent.render_with_repair(dsl, scene_number)
            logger.info(f"✅ [Scene {scene_number}] Render complete — raw video at: {raw_video}")

            # 4. Visual QA Agent (Multimodal Vision Check)
            logger.info(f"👁️  [Scene {scene_number}] Running Visual QA Agent (multimodal keyframe critique)...")
            qa_report = self.visual_qa_agent.inspect_scene(raw_video, dsl, scene_number)
            if qa_report.passed:
                logger.info(f"✅ [Scene {scene_number}] Visual QA passed — no blocking issues.")
            else:
                blocking = [i for i in qa_report.issues if i.severity == "blocking"]
                cosmetic = [i for i in qa_report.issues if i.severity == "cosmetic"]
                if blocking:
                    logger.warning(f"⚠️  [Scene {scene_number}] Visual QA: {len(blocking)} BLOCKING issue(s) detected: {[i.description for i in blocking]}")
                if cosmetic:
                    logger.info(f"💡 [Scene {scene_number}] Visual QA: {len(cosmetic)} cosmetic issue(s) noted (non-blocking).")

            # 5. Narration Synthesis (TTS)
            logger.info(f"🎹 [Scene {scene_number}] Synthesizing voice narration (TTS)...")
            narration_filename = f"narration_scene_{scene_number}.mp3"
            audio_path = self.narration_generator.generate_narration(dsl.voice, filename=narration_filename)
            logger.info(f"✅ [Scene {scene_number}] Narration ready at: {audio_path}")

            # 6. Per-Scene FFmpeg Merge
            logger.info(f"🎥 [Scene {scene_number}] Merging video + narration audio with FFmpeg...")
            merged_filename = f"merged_scene_{scene_number}.mp4"
            merged_video = self.merger.merge(raw_video, audio_path, output_filename=merged_filename)
            logger.info(f"✅ [Scene {scene_number}] Merged scene video ready: {merged_video}")

            return {
                "scene_number": scene_number,
                "video": merged_video,
                "dsl": dsl.model_dump(),
                "manim_code": manim_code,
                "transcript": transcript,
                "qa_report": qa_report
            }

    async def run_pipeline(self, topic: str, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Runs the complete multi-agent orchestration graph asynchronously."""
        logger.info(f"🧠 [Orchestrator] ========= Starting Multi-Agent Pipeline v2 =========")
        logger.info(f"📚 [Orchestrator] Topic: '{topic}' | User ID: {user_id}")

        # Step 0: Neo4j Knowledge Graph Context Injection
        logger.info("🔗 [Neo4j] Pre-retrieving Knowledge Graph context...")
        graph_context = ""
        try:
            from app.services.graph_service import GraphService
            graph_context = GraphService.get_graph_context_for_prompt(topic, user_id=user_id)
            if graph_context:
                logger.info(f"✅ [Neo4j] Graph context injected into prompt for '{topic}' ({len(graph_context)} chars).")
            else:
                logger.info("ℹ️  [Neo4j] No existing graph context found for this topic. Proceeding fresh.")
        except Exception as graph_err:
            logger.warning(f"⚠️  [Neo4j] Graph context retrieval skipped (non-fatal): {graph_err}")

        # Step 1: Lesson Planner
        logger.info("📌 [Stage 1] Lesson Planner — Extracting parameters & formulating approach...")
        lesson_plan = self.lesson_planner.plan_lesson(topic, graph_context=graph_context)
        params = lesson_plan.extracted_parameters
        approach = lesson_plan.approach
        knowledge_meta = lesson_plan.knowledge_metadata.model_dump() if lesson_plan.knowledge_metadata else None
        logger.info(f"✅ [Stage 1] Lesson Plan complete — Algorithm: '{params.algorithm_or_topic}' | Type: '{params.problem_type}'")

        # Step 2: Scene Planner
        logger.info("🎦 [Stage 2] Scene Planner — Breaking lesson into visual scenes...")
        scenes = self.scene_planner.plan_scenes(lesson_plan)
        logger.info(f"✅ [Stage 2] Scene Plan complete — {len(scenes)} scene(s) planned.")

        # Step 2.5: Style Guide Agent
        logger.info("🎨 [Stage 2.5] Style Guide Agent — Generating visual style contract...")
        style_guide = self.style_guide_agent.generate_style_guide(topic)
        logger.info(f"✅ [Stage 2.5] Style guide ready — Primary: {style_guide.palette.get('primary')}, Highlight: {style_guide.highlight_color}")

        # Step 3-8: Parallel Scene Fan-out (asyncio.gather with Semaphore(3))
        logger.info(f"⚡ [Fan-out] Dispatching {len(scenes)} scene(s) in PARALLEL (concurrency limit=3)...")
        tasks = [
            self._process_single_scene(scene, idx, len(scenes), style_guide)
            for idx, scene in enumerate(scenes)
        ]
        results = await asyncio.gather(*tasks)

        # Sort results by scene number
        results.sort(key=lambda r: r["scene_number"])
        logger.info(f"✅ [Fan-out] All {len(results)} scene(s) processed and sorted.")

        scene_videos = [r["video"] for r in results]
        all_dsls = [r["dsl"] for r in results]
        all_manim_code = [r["manim_code"] for r in results]

        # Step 8.5: Continuity Checker
        logger.info("🔎 [Stage 8.5] Continuity Checker — Verifying cross-scene visual consistency...")
        dsl_objs = [SceneDSL(**d) for d in all_dsls]
        continuity_res = self.continuity_checker.check_continuity(dsl_objs, style_guide)
        if continuity_res["passed"]:
            logger.info("✅ [Continuity] All scenes passed visual consistency check.")
        else:
            logger.warning(f"⚠️  [Continuity] Issues detected: {continuity_res['issues']}")

        # Step 9: FFmpeg Multi-Scene Concat Demuxer
        logger.info(f"🎥 [Stage 9] Concatenating {len(scene_videos)} scene video(s) into final.mp4...")
        final_video = self.merger.concat_videos(scene_videos, output_filename="final.mp4")
        logger.info(f"✅ [Stage 9] Final video ready at: {final_video}")

        # Step 9.5: Pedagogical Evaluator (Pre-publish Quality Gate)
        logger.info("🎓 [Stage 9.5] Pedagogical Evaluator — Running LLM-as-judge quality assessment...")
        pedagogical_score = self.pedagogical_evaluator.evaluate_lesson(topic, approach, all_dsls)
        logger.info(
            f"✅ [Pedagogical] Score — Clarity: {pedagogical_score.clarity}/5 | "
            f"Accuracy: {pedagogical_score.accuracy}/5 | "
            f"Pacing: {pedagogical_score.pacing}/5 | "
            f"Engagement: {pedagogical_score.engagement}/5"
        )

        logger.info(f"🏆 [Orchestrator] ========= Multi-Agent Pipeline COMPLETE! Final video: {final_video} =========")

        return {
            "video": final_video,
            "topic": topic,
            "extracted_parameters": params.model_dump(),
            "approach": approach.model_dump(),
            "dsl_code": all_dsls,
            "manim_code": "\n\n# --- SCENE SEPARATOR ---\n\n".join(all_manim_code),
            "knowledge_metadata": knowledge_meta,
            "style_guide": style_guide.model_dump(),
            "continuity": continuity_res,
            "pedagogical_score": pedagogical_score.model_dump()
        }
