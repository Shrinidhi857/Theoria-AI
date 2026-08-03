import logging
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
from app.db.base import Base

logger = logging.getLogger(__name__)

# Determine connect args and create engine with fallback resilience
db_url = settings.DATABASE_URL
connect_args = {}

if db_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False

try:
    engine = create_engine(
        db_url,
        connect_args=connect_args,
        pool_pre_ping=True if not db_url.startswith("sqlite") else False
    )
    # Test connection
    with engine.connect() as conn:
        pass
    logger.info(f"Successfully connected to database: {db_url.split('@')[-1] if '@' in db_url else db_url}")
except Exception as e:
    logger.warning(f"Could not connect to configured DB ({db_url}): {e}. Falling back to SQLite temporary database.")
    fallback_url = "sqlite:///./theoria_fallback.db"
    engine = create_engine(fallback_url, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Create all database tables on application startup."""
    # Import all models to ensure they register with Base.metadata
    from app.models.user import User  # noqa
    from app.models.video import VideoGeneration  # noqa
    
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized successfully.")


def get_db() -> Generator[Session, None, None]:
    """Dependency generator providing SQLAlchemy database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
