import os
import shutil
import subprocess
import logging

try:
    from app.core.logging_config import setup_colored_logging
    logger = setup_colored_logging("engine.narration")
except ImportError:
    logger = logging.getLogger(__name__)


class NarrationGenerator:
    """Stage 7: Synthesizes voice audio narration from text using gTTS or fallback synthesis."""

    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_narration(self, voice_text: str, filename: str = "narration.mp3") -> str:
        """
        Synthesizes speech from voice_text and saves to filename in output_dir.
        Returns the absolute filepath to the generated audio file.
        """
        output_path = os.path.abspath(os.path.join(self.output_dir, filename))

        if not voice_text:
            voice_text = "Binary search works by dividing the search interval in half."

        try:
            from gtts import gTTS
            tts = gTTS(text=voice_text, lang="en")
            tts.save(output_path)
            logger.info(f"🎹 [TTS] gTTS narration synthesized successfully → {output_path}")
            return output_path
        except Exception as e:
            logger.warning(f"⚠️  [TTS] gTTS narration failed ({e}). Generating fallback FFmpeg sine audio...")

        # Fallback audio generation using FFmpeg sine wave if gTTS is unavailable
        self._create_fallback_audio(output_path)
        return output_path

    def _create_fallback_audio(self, output_path: str):
        """Generates a 5-second silence/tone audio file via FFmpeg."""
        ffmpeg_cmd = shutil.which("ffmpeg") or "ffmpeg"
        cmd = [
            ffmpeg_cmd,
            "-y",
            "-f", "lavfi",
            "-i", "anullsrc=r=44100:cl=stereo",
            "-t", "5",
            "-q:a", "9",
            "-acodec", "libmp3lame",
            output_path
        ]
        try:
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            logger.info(f"✅ [TTS] Fallback silence audio created at: {output_path}")
        except Exception as e:
            logger.error(f"❌ [TTS] Could not create fallback audio: {e}")
            with open(output_path, "wb") as f:
                f.write(b"")
