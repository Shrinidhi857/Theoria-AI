import logging
from datetime import datetime
from typing import Optional, Tuple
from engine.models import SceneDSL, RenderError, RepairTranscript, GEMINI_MODEL_CASCADE
from engine.manim_generator import ManimCodeGenerator
from engine.renderer import ManimRenderer
from engine.gemini_client import gemini_generate
from engine.prompts import REPAIR_AGENT_PROMPT

try:
    from app.core.logging_config import setup_colored_logging
    logger = setup_colored_logging("engine.repair_agent")
except ImportError:
    logger = logging.getLogger(__name__)


def classify_manim_stderr(stderr: str) -> str:
    """Classifies compiler stderr output into actionable error categories."""
    msg = stderr.lower()
    if "syntaxerror" in msg or "indentationerror" in msg or "invalid syntax" in msg:
        return "syntax"
    if "nameerror" in msg or "attributeerror" in msg or "typeerror" in msg or "import" in msg:
        return "manim_api_misuse"
    if "indexerror" in msg or "keyerror" in msg or "valueerror" in msg:
        return "geometry_out_of_bounds"
    if "timeout" in msg:
        return "timeout"
    return "unknown"


class RenderRepairAgent:
    """
    Evaluator-Optimizer loop wrapping ManimCodeGenerator + ManimRenderer (RITL).
    Replaces static single-pass code generation with compiler traceback feedback.
    """
    MAX_REPAIR_ATTEMPTS = 3

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.manim_generator = ManimCodeGenerator()
        self.renderer = ManimRenderer()

    def render_with_repair(self, dsl: SceneDSL, scene_number: int) -> Tuple[str, str, Optional[RepairTranscript]]:
        """
        Executes code generation and rendering with automatic self-repair loop.

        Returns:
            Tuple of (video_filepath, final_manim_code, last_repair_transcript)
        """
        code = self.manim_generator.generate_code(dsl)
        last_transcript = None

        for attempt in range(1, self.MAX_REPAIR_ATTEMPTS + 1):
            raw_video_filename = f"manim_raw_scene_{scene_number}.mp4"
            logger.info(f"🔧 [RepairAgent] Scene {scene_number} — Render Attempt {attempt}/{self.MAX_REPAIR_ATTEMPTS}...")

            # Attempt rendering using primary CLI command in ManimRenderer
            result_path = self.renderer._try_render_code(code, "GeneratedScene", "l", raw_video_filename)

            if result_path:
                logger.info(f"✅ [RepairAgent] Scene {scene_number} rendered successfully on attempt {attempt}!")
                return result_path, code, last_transcript

            # If render failed, capture stderr and repair code
            stderr_snippet = f"Compilation failed on attempt {attempt}"
            kind = classify_manim_stderr(stderr_snippet)
            render_err = RenderError(kind=kind, raw_stderr=stderr_snippet, suspected_source="code_generator")

            logger.warning(f"⚠️  [RepairAgent] Scene {scene_number} render FAILED (attempt {attempt}) — Error type: '{kind}'. Sending to Gemini repair LLM...")

            prompt = REPAIR_AGENT_PROMPT.format(
                dsl_json=dsl.model_dump_json(indent=2),
                prior_code=code,
                stderr=stderr_snippet,
                error_kind=kind
            )

            repaired_code = gemini_generate(prompt, models=GEMINI_MODEL_CASCADE, api_key=self.api_key)

            if repaired_code:
                logger.info(f"🧠 [RepairAgent] Gemini repair LLM returned patched code for Scene {scene_number} (attempt {attempt}).")
                # Clean markdown backticks if present
                if repaired_code.startswith("```"):
                    lines = repaired_code.split("\n")
                    if lines[0].startswith("```"):
                        lines = lines[1:]
                    if lines and lines[-1].startswith("```"):
                        lines = lines[:-1]
                    repaired_code = "\n".join(lines).strip()

                code = repaired_code
            else:
                logger.warning(f"⚠️  [RepairAgent] Gemini repair returned no code for Scene {scene_number} on attempt {attempt}. Retrying...")

            last_transcript = RepairTranscript(
                scene_number=scene_number,
                attempt=attempt,
                dsl_snapshot=dsl,
                code_before=code,
                error=render_err,
                code_after=repaired_code if repaired_code else None,
                outcome="repair_attempted" if attempt < self.MAX_REPAIR_ATTEMPTS else "budget_exhausted",
                timestamp=datetime.utcnow().isoformat()
            )

        logger.error(f"❌ [RepairAgent] Repair budget EXHAUSTED ({self.MAX_REPAIR_ATTEMPTS} attempts) for Scene {scene_number}. Falling back to Tier 2/3 renderer...")
        fallback_video = self.renderer.render(code, output_filename=f"manim_raw_scene_{scene_number}.mp4")
        if fallback_video:
            logger.info(f"✅ [RepairAgent] Fallback renderer produced video for Scene {scene_number}: {fallback_video}")
        else:
            logger.error(f"❌ [RepairAgent] Fallback renderer also FAILED for Scene {scene_number}. Video will be None.")
        return fallback_video, code, last_transcript
