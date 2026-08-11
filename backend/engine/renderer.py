import os
import sys
import shutil
import tempfile
import subprocess
import logging
from typing import Optional

try:
    from app.core.logging_config import setup_colored_logging
    logger = setup_colored_logging(__name__)
except ImportError:
    logger = logging.getLogger(__name__)


DEFAULT_FALLBACK_MANIM = """from manim import *

class GeneratedScene(Scene):
    def construct(self):
        title = Text("Concept Visualization", font_size=36, color=WHITE).to_edge(UP)
        arr_vgroup = VGroup()
        vals = [1, 3, 5, 7, 9, 11, 13]
        for i, val in enumerate(vals):
            sq = Square(side_length=0.9, color=BLUE)
            txt = Text(str(val), font_size=22)
            cell = VGroup(sq, txt)
            if i > 0:
                cell.next_to(arr_vgroup[-1], RIGHT, buff=0.05)
            arr_vgroup.add(cell)
        arr_vgroup.move_to([0, 0, 0])
        
        ptr_arrow = Arrow(start=[0, -1.2, 0], end=[0, -0.5, 0], color=YELLOW, buff=0.1)
        ptr_txt = Text("target = 9", font_size=20, color=YELLOW).next_to(ptr_arrow, DOWN, buff=0.1)
        ptr = VGroup(ptr_arrow, ptr_txt).move_to([0, -1.2, 0])

        self.play(Write(title), FadeIn(arr_vgroup))
        self.wait(0.5)
        self.play(FadeIn(ptr))
        self.play(Indicate(arr_vgroup[4], color=YELLOW), run_time=1.5)
        self.wait(1)
"""


class ManimRenderer:
    """Stage 6: Renders generated Python Manim code into an MP4 video file using Manim CLI."""

    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def render(self, code_string: str, scene_class_name: str = "GeneratedScene", quality: str = "l", output_filename: str = "manim_raw.mp4") -> str:
        """
        Renders the Python code string to an MP4 video file.
        Returns the absolute filepath to the rendered MP4 video.
        """
        # Attempt rendering provided code string
        result_path = self._try_render_code(code_string, scene_class_name, quality, output_filename)
        if result_path:
            return result_path

        # Secondary fallback: Render default structured Manim scene code
        logger.warning("Primary Manim code failed. Attempting fallback Manim scene compilation...")
        fallback_path = self._try_render_code(DEFAULT_FALLBACK_MANIM, scene_class_name, quality, output_filename)
        if fallback_path:
            return fallback_path

        # Final fallback: FFmpeg dark gradient canvas
        fallback_mp4 = os.path.abspath(os.path.join(self.output_dir, output_filename))
        self._create_fallback_video(fallback_mp4)
        return fallback_mp4

    def _try_render_code(self, code_string: str, scene_class_name: str, quality: str, output_filename: str) -> Optional[str]:
        with tempfile.TemporaryDirectory() as tmpdir:
            script_path = os.path.join(tmpdir, "scene.py")
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(code_string)

            cmd = [sys.executable, "-m", "manim", "-q" + quality, "--format=mp4", "--media_dir", tmpdir, script_path, scene_class_name]
            logger.info(f"Executing Manim render command: {' '.join(cmd)}")

            try:
                result = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=120
                )

                if result.returncode == 0:
                    for root, dirs, files in os.walk(tmpdir):
                        for file in files:
                            if file.endswith(".mp4"):
                                generated_mp4 = os.path.join(root, file)
                                dest_mp4 = os.path.abspath(os.path.join(self.output_dir, output_filename))
                                shutil.copy(generated_mp4, dest_mp4)
                                logger.info(f"Manim render successful: {dest_mp4}")
                                return dest_mp4

                logger.error(f"Manim CLI returncode {result.returncode}.\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}")
            except Exception as e:
                logger.error(f"Manim render error: {e}", exc_info=True)

        return None

    def _create_fallback_video(self, output_path: str):
        """Creates a sleek dark themed 5-second test video using FFmpeg if Manim render fails."""
        ffmpeg_cmd = shutil.which("ffmpeg")
        if not ffmpeg_cmd:
            try:
                import imageio_ffmpeg
                ffmpeg_cmd = imageio_ffmpeg.get_ffmpeg_exe()
            except Exception:
                ffmpeg_cmd = "ffmpeg"

        # Dark sleek background (#121212)
        cmd = [
            ffmpeg_cmd,
            "-y",
            "-f", "lavfi",
            "-i", "color=c=0x121212:s=1280x720:d=5",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            output_path
        ]
        try:
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            logger.info(f"Fallback video created at {output_path}")
        except Exception as e:
            logger.error(f"Could not create fallback video: {e}")
            with open(output_path, "wb") as f:
                f.write(b"")
