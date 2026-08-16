import os
import shutil
import subprocess
import logging

try:
    from app.core.logging_config import setup_colored_logging
    logger = setup_colored_logging("engine.ffmpeg_merge")
except ImportError:
    logger = logging.getLogger(__name__)


class FFmpegMerger:
    """Stage 8: Merges rendered Manim video and TTS audio file into a single synchronized MP4 video."""

    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def merge(self, video_path: str, audio_path: str, output_filename: str = "final.mp4") -> str:
        """
        Combines video and audio streams using FFmpeg.
        Returns the absolute filepath to the final merged MP4 video file.
        """
        final_path = os.path.abspath(os.path.join(self.output_dir, output_filename))
        
        # Resolve ffmpeg executable location (system PATH or imageio_ffmpeg package)
        ffmpeg_cmd = shutil.which("ffmpeg")
        if not ffmpeg_cmd:
            try:
                import imageio_ffmpeg
                ffmpeg_cmd = imageio_ffmpeg.get_ffmpeg_exe()
            except Exception:
                ffmpeg_cmd = "ffmpeg"

        # Check if video and audio exist
        if not os.path.exists(video_path) or os.path.getsize(video_path) == 0:
            logger.warning(f"Video file missing or empty: {video_path}")
        if not os.path.exists(audio_path) or os.path.getsize(audio_path) == 0:
            logger.warning(f"Audio file missing or empty: {audio_path}")

        cmd = [
            ffmpeg_cmd,
            "-y",
            "-i", video_path,
            "-i", audio_path,
            "-c:v", "copy",
            "-c:a", "aac",
            "-shortest",
            final_path
        ]

        logger.info(f"Executing FFmpeg merge command: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=60
            )

            if result.returncode == 0 and os.path.exists(final_path):
                logger.info(f"FFmpeg merge succeeded: {final_path}")
                return final_path
            
            logger.warning(f"FFmpeg merge returned non-zero code {result.returncode}. Stderr: {result.stderr}")
        except Exception as e:
            logger.warning(f"FFmpeg merge command execution failed ({e}). Falling back to video copy.")

        # Fallback if audio merge fails: copy video directly as final.mp4
        if os.path.exists(video_path):
            shutil.copy(video_path, final_path)
            return final_path

        # Create dummy file if needed
        with open(final_path, "wb") as f:
            f.write(b"")
        return final_path

    def concat_videos(self, video_paths: list, output_filename: str = "final.mp4") -> str:
        """
        Concatenates multiple video files into one using FFmpeg demuxer.
        Returns the absolute filepath to the final merged/concatenated video.
        """
        final_path = os.path.abspath(os.path.join(self.output_dir, output_filename))
        if not video_paths:
            logger.warning("No video paths provided for concatenation.")
            return final_path

        # Resolve ffmpeg path
        ffmpeg_cmd = shutil.which("ffmpeg")
        if not ffmpeg_cmd:
            try:
                import imageio_ffmpeg
                ffmpeg_cmd = imageio_ffmpeg.get_ffmpeg_exe()
            except Exception:
                ffmpeg_cmd = "ffmpeg"

        # Create a text file listing all videos
        txt_path = os.path.abspath(os.path.join(self.output_dir, "concat_list.txt"))
        try:
            with open(txt_path, "w", encoding="utf-8") as f:
                for vp in video_paths:
                    safe_path = vp.replace("\\", "/")
                    f.write(f"file '{safe_path}'\n")

            cmd = [
                ffmpeg_cmd,
                "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", txt_path,
                "-c", "copy",
                final_path
            ]

            logger.info(f"Executing FFmpeg concat command: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=90
            )

            if result.returncode == 0 and os.path.exists(final_path):
                logger.info(f"FFmpeg concat succeeded: {final_path}")
                return final_path
            
            logger.warning(f"FFmpeg concat returned non-zero code {result.returncode}. Stderr: {result.stderr}")
        except Exception as e:
            logger.error(f"FFmpeg concat failed: {e}", exc_info=True)
        finally:
            if os.path.exists(txt_path):
                try:
                    os.remove(txt_path)
                except Exception:
                    pass

        # Fallback: Copy the first video if concat fails
        if video_paths and os.path.exists(video_paths[0]):
            shutil.copy(video_paths[0], final_path)
            return final_path

        return final_path
