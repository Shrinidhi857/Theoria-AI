import logging
from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
from app.db.base import Base

logger = logging.getLogger(__name__)

db_url = settings.DATABASE_URL

is_postgres = db_url.startswith("postgresql") or db_url.startswith("postgres")

if is_postgres:
    engine = create_engine(
        db_url,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
        echo=False,
    )
else:
    # SQLite fallback (dev only)
    engine = create_engine(
        db_url,
        connect_args={"check_same_thread": False},
        echo=False,
    )

try:
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    db_display = db_url.split('@')[-1] if '@' in db_url else db_url
    logger.info(f"✅ Database connected: {db_display}")
except Exception as e:
    logger.error(f"❌ Database connection failed: {e}")
    raise RuntimeError(
        f"Cannot connect to database. Check DATABASE_URL in .env.\nURL: {db_url}\nError: {e}"
    )

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
