import logging
from typing import Optional
from contextlib import contextmanager

try:
    from neo4j import GraphDatabase, Driver, Session
    NEO4J_DRIVER_INSTALLED = True
except ImportError:
    GraphDatabase = None  # type: ignore
    Driver = None  # type: ignore
    Session = None  # type: ignore
    NEO4J_DRIVER_INSTALLED = False

from app.core.config import settings

try:
    from app.core.logging_config import setup_colored_logging
    logger = setup_colored_logging(__name__)
except ImportError:
    logger = logging.getLogger(__name__)

_driver_instance: Optional[Driver] = None


def init_neo4j_driver() -> Optional[Driver]:
    """
    Initializes the reusable global Neo4j driver using configured settings.
    If Neo4j is disabled, credentials missing, or connection fails, logs warning and returns None cleanly.
    """
    global _driver_instance

    if not settings.NEO4J_ENABLED:
        logger.info("[Neo4j] Graph integration disabled (NEO4J_ENABLED=false).")
        _driver_instance = None
        return None

    if not NEO4J_DRIVER_INSTALLED:
        logger.warning("[Neo4j] 'neo4j' package not installed in environment. Continuing without graph support.")
        _driver_instance = None
        return None

    if not settings.NEO4J_URI or not settings.NEO4J_PASSWORD:
        logger.warning("[Neo4j] NEO4J_URI or NEO4J_PASSWORD not configured. Continuing without graph support.")
        _driver_instance = None
        return None

    try:
        logger.info(f"[Neo4j] Connecting to driver at {settings.NEO4J_URI}...")
        driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD)
        )
        driver.verify_connectivity()
        _driver_instance = driver
        logger.info("✅ [Neo4j] Connected successfully!")
        return _driver_instance
    except Exception as e:
        logger.warning(f"⚠️ [Neo4j] Connectivity verification failed: {e}. Graph unavailable; continuing lesson generation without graph context.")
        _driver_instance = None
        return None


def get_neo4j_driver() -> Optional[Driver]:
    """Returns currently active global Neo4j Driver instance, if available."""
    global _driver_instance
    return _driver_instance


def close_neo4j_driver() -> None:
    """Gracefully closes active Neo4j driver connection on shutdown."""
    global _driver_instance
    if _driver_instance:
        try:
            logger.info("[Neo4j] Closing Neo4j driver connection...")
            _driver_instance.close()
            logger.info("[Neo4j] Driver connection closed.")
        except Exception as e:
            logger.error(f"[Neo4j] Error closing driver connection: {e}")
        finally:
            _driver_instance = None


def is_neo4j_available() -> bool:
    """Check if active, working Neo4j driver connection exists."""
    return _driver_instance is not None


@contextmanager
def get_neo4j_session(database: Optional[str] = None):
    """
    Context manager providing a safe Neo4j session.
    If Neo4j is unavailable or fails, yields None so caller can fallback gracefully.
    """
    driver = get_neo4j_driver()
    if not driver:
        yield None
        return

    db_name = database or settings.NEO4J_DATABASE or "neo4j"
    session = None
    try:
        session = driver.session(database=db_name)
        yield session
    except Exception as e:
        logger.warning(f"⚠️ [Neo4j] Error creating session or running transaction: {e}")
        yield None
    finally:
        if session:
            try:
                session.close()
            except Exception:
                pass
