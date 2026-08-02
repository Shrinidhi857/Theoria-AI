import os
import sys
import json
import logging

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from engine.pipeline import generate_video

# ── Colored logging setup ──────────────────────────────────────────────────────
try:
    import colorlog
    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter(
        fmt="%(log_color)s%(asctime)s [%(levelname)-8s]%(reset)s %(cyan)s%(name)s%(reset)s: %(message)s",
        datefmt="%H:%M:%S",
        log_colors={
            "DEBUG":    "white",
            "INFO":     "green",
            "WARNING":  "yellow,bold",
            "ERROR":    "red,bold",
            "CRITICAL": "red,bold,bg_white",
        },
        secondary_log_colors={
            "message": {
                "WARNING":  "yellow",
                "ERROR":    "red",
                "CRITICAL": "red",
            }
        }
    ))
    logging.root.setLevel(logging.INFO)
    logging.root.addHandler(handler)
    # Suppress noisy google / httpx DEBUG logs
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("google_genai").setLevel(logging.WARNING)

except ImportError:
    # Fallback to plain logging if colorlog is not available
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

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
