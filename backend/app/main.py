import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.db.session import init_db
from app.db.neo4j import init_neo4j_driver, close_neo4j_driver
from app.api.v1.router import api_v1_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler initializing DB tables, Neo4j connection, and output directory."""
    logger.info("Initializing Relational Database Tables...")
    try:
        init_db()
    except Exception as e:
        logger.error(f"Error during DB initialization: {e}")
    
    logger.info("Initializing Neo4j Knowledge Graph Driver...")
    try:
        init_neo4j_driver()
    except Exception as e:
        logger.warning(f"Error during Neo4j initialization: {e}")

    # Ensure output directory exists for video storage
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "output"))
    os.makedirs(output_dir, exist_ok=True)
    logger.info(f"Video Output directory ready: {output_dir}")
    
    yield
    logger.info("Shutting down Application and closing database drivers...")
    close_neo4j_driver()



app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Professional FastAPI Backend with PostgreSQL, JWT Auth (Email & Google OAuth), and AI Engine Integration",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan
)

# CORS Configuration
_cors_origins = settings.BACKEND_CORS_ORIGINS
_allow_all_origins = "*" in _cors_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if _allow_all_origins else _cors_origins,
    allow_credentials=not _allow_all_origins,  # credentials can't be used with wildcard
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static Files Mount for Output Videos
output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "output"))
os.makedirs(output_path, exist_ok=True)
app.mount("/output", StaticFiles(directory=output_path), name="output")

# Router Registration
app.include_router(api_v1_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["Health"])
@app.get(f"{settings.API_V1_STR}/health", tags=["Health"])
def health_check():
    """Service health check endpoint."""
    return {
        "status": "ok",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
