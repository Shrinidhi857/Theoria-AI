import asyncio
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from engine.orchestrator_graph import EngineOrchestrator

try:
    from app.core.logging_config import setup_colored_logging
    logger = setup_colored_logging(__name__)
except ImportError:
    logger = logging.getLogger(__name__)


class VideoPipeline:
    """
    End-to-end multi-agent orchestration pipeline for AI Teaching Engine.
    Delegates to EngineOrchestrator (parallel scene fan-out, self-repair loops, visual QA, pedagogical eval).
    """

    def __init__(self, api_key: Optional[str] = None):
        self.orchestrator = EngineOrchestrator(api_key=api_key)

    def run(self, topic: str, user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Executes complete multi-agent pipeline synchronously (wrapping async event loop if needed).
        """
        logger.info(f"=== Starting AI Teaching Engine Pipeline (v2 Multi-Agent) for: '{topic}' ===")
        
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            try:
                import nest_asyncio
                nest_asyncio.apply()
                return loop.run_until_complete(self.orchestrator.run_pipeline(topic, user_id=user_id))
            except Exception:
                # Fallback if nested event loop run is prevented
                future = asyncio.run_coroutine_threadsafe(
                    self.orchestrator.run_pipeline(topic, user_id=user_id), loop
                )
                return future.result()
        else:
            return asyncio.run(self.orchestrator.run_pipeline(topic, user_id=user_id))



def generate_video(topic: str, user_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Main entrypoint function requested by specification.
    """
    pipeline = VideoPipeline()
    return pipeline.run(topic, user_id=user_id)
