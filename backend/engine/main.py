import os
import sys
import json
import logging

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from engine.pipeline import generate_video

from app.core.logging_config import setup_colored_logging

# Initialize global colored logging
setup_colored_logging()
logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────

import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

BANNER = """
==========================================
     AI TEACHING ENGINE  PoC BACKEND     
==========================================
"""


def main():
    topic = sys.argv[1] if len(sys.argv) > 1 else "Explain Binary Search"
    print(BANNER)
    print(f"  >> Topic: \"{topic}\"\n")

    result = generate_video(topic)

    print("\n  [DONE] Pipeline completed!")
    print("  ------------------------------------------")
    print(json.dumps(result, indent=4))
    print("  ------------------------------------------\n")


if __name__ == "__main__":
    main()
