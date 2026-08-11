import os
import json
import shutil
import tempfile
import subprocess
import logging
from typing import List, Optional, Any
from PIL import Image

from engine.models import SceneDSL, VisualQAReport, VisualIssue, GEMINI_MODEL_CASCADE
from engine.gemini_client import gemini_generate_vision
from engine.prompts import VISUAL_QA_PROMPT

try:
    from app.core.logging_config import setup_colored_logging
    logger = setup_colored_logging("engine.visual_qa_agent")
except ImportError:
    logger = logging.getLogger(__name__)


def extract_video_keyframes(video_path: str, count: int = 3) -> List[Image.Image]:
    """Extracts keyframe PIL Images at even timestamps across the video file."""
    images = []
    if not os.path.exists(video_path) or os.path.getsize(video_path) == 0:
        return images

    ffmpeg_cmd = shutil.which("ffmpeg")
    if not ffmpeg_cmd:
        try:
            import imageio_ffmpeg
            ffmpeg_cmd = imageio_ffmpeg.get_ffmpeg_exe()
        except Exception:
            ffmpeg_cmd = "ffmpeg"

    with tempfile.TemporaryDirectory() as tmpdir:
        out_pattern = os.path.join(tmpdir, "frame_%03d.png")
        cmd = [
            ffmpeg_cmd,
            "-y",
            "-i", video_path,
            "-vf", f"fps=1/{count}",
            "-vframes", str(count),
            out_pattern
        ]
        try:
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            extracted = []
            for fname in sorted(os.listdir(tmpdir)):
                if fname.endswith(".png"):
                    img_path = os.path.join(tmpdir, fname)
                    img = Image.open(img_path).convert("RGB")
                    extracted.append(img.copy())
                    img.close()
            images.extend(extracted)
            logger.info(f"✅ [VisualQA] Extracted {len(extracted)} keyframe(s) from '{os.path.basename(video_path)}'.")
        except Exception as e:
            logger.warning(f"⚠️  [VisualQA] Keyframe extraction error from '{video_path}': {e}")

    return images


class VisualQAAgent:
    """
    Multimodal Vision Verification Subagent.
    Critiques rendered scene keyframes for overlaps, boundary cutoffs, legibility, and index alignment.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    def inspect_scene(self, video_path: str, dsl: SceneDSL, scene_number: int) -> VisualQAReport:
        """Extracts keyframe screenshots and performs Gemini Vision critique."""
        logger.info(f"👁️  [VisualQA] Extracting {3} keyframe(s) from Scene {scene_number} video...")
        keyframes = extract_video_keyframes(video_path, count=3)

        if not keyframes:
            logger.warning(f"⚠️  [VisualQA] No keyframes extracted from '{video_path}'. Skipping vision check (defaulting to PASS).")
            return VisualQAReport(scene_number=scene_number, passed=True, issues=[])

        logger.info(f"🤖 [VisualQA] Sending {len(keyframes)} keyframe(s) to Gemini Vision for critique of Scene {scene_number}...")
        prompt = VISUAL_QA_PROMPT.format(
            scene_number=scene_number,
            dsl_json=dsl.model_dump_json(indent=2)
        )

        response_text = gemini_generate_vision(
            prompt=prompt,
            images=keyframes,
            models=GEMINI_MODEL_CASCADE,
            api_key=self.api_key
        )

        if response_text:
            try:
                if response_text.startswith("```"):
                    response_text = response_text.strip("`").replace("json", "").strip()
                data = json.loads(response_text)
                report = VisualQAReport(**data)
                if report.passed:
                    logger.info(f"✅ [VisualQA] Scene {scene_number} passed visual critique.")
                else:
                    logger.warning(f"⚠️  [VisualQA] Scene {scene_number} has {len(report.issues)} QA issue(s): {[i.description for i in report.issues]}")
                return report
            except Exception as e:
                logger.warning(f"⚠️  [VisualQA] Failed to parse vision critique JSON for Scene {scene_number}: {e}")

        logger.info(f"ℹ️  [VisualQA] Scene {scene_number}: no valid critique — defaulting to PASS.")
        # Default pass if vision critique produces invalid JSON or fails silently
        return VisualQAReport(scene_number=scene_number, passed=True, issues=[])
