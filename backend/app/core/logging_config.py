import logging
import sys
from typing import Optional


def setup_colored_logging(name: Optional[str] = None, log_level: int = logging.INFO) -> logging.Logger:
    """
    Sets up global colored logging and returns a named child logger (idempotent).

    Call once from main.py to configure the root logger globally, OR call from
    any module as a drop-in replacement for logging.getLogger(__name__).

    Color scheme:
      - DEBUG    : white
      - INFO     : green bold   ✅
      - WARNING  : yellow bold  ⚠️
      - ERROR    : red bold     ❌
      - CRITICAL : red bold, white background
    """
    root_logger = logging.getLogger()

    # Only configure root logger once — idempotent (check for existing handlers)
    if not root_logger.handlers:
        root_logger.setLevel(log_level)

        # Force UTF-8 on stdout so emoji characters (✅ ❌ ⚠️) render on all platforms
        import io
        utf8_stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True)

        try:
            import colorlog

            handler = colorlog.StreamHandler(utf8_stdout)
            handler.setLevel(log_level)
            handler.setFormatter(
                colorlog.ColoredFormatter(
                    fmt=(
                        "%(log_color)s%(asctime)s [%(levelname)-8s]%(reset)s "
                        "%(cyan)s%(name)s%(reset)s  %(message_log_color)s%(message)s%(reset)s"
                    ),
                    datefmt="%H:%M:%S",
                    log_colors={
                        "DEBUG":    "white",
                        "INFO":     "green,bold",
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
                    },
                    reset=True,
                    style="%",
                )
            )
        except ImportError:
            # Graceful fallback if colorlog is not installed
            handler = logging.StreamHandler(utf8_stdout)
            handler.setLevel(log_level)
            handler.setFormatter(
                logging.Formatter(
                    fmt="%(asctime)s [%(levelname)-8s] %(name)s: %(message)s",
                    datefmt="%H:%M:%S",
                )
            )

        root_logger.addHandler(handler)

        # Suppress noisy third-party library loggers
        for noisy in ["httpx", "google_genai", "boto3", "botocore", "urllib3",
                      "hpack", "h2", "httpcore", "watchfiles"]:
            logging.getLogger(noisy).setLevel(logging.WARNING)

        logging.getLogger("uvicorn.access").setLevel(logging.INFO)

    # Return named child logger if name provided, else return root logger
    if name:
        return logging.getLogger(name)
    return root_logger
