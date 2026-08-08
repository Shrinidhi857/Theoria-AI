import os
from typing import List
from pydantic import Field

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
except ImportError:
    from pydantic import BaseSettings  # type: ignore

# Always resolve .env relative to this file's location (backend/.env)
# so credentials load correctly regardless of where uvicorn/python is invoked from.
_ENV_FILE = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
_ENV_FILE = os.path.abspath(_ENV_FILE)


class Settings(BaseSettings):
    PROJECT_NAME: str = "Theoria AI Engine API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str = Field(
        default="postgresql://postgres:shri1234@127.0.0.1:5432/theoria_db",
        description="PostgreSQL Database URL e.g. postgresql://user:pass@host:5432/theoria_db"
    )

    # JWT Authentication
    SECRET_KEY: str = Field(
        default="theoria_ai_super_secret_jwt_signing_key_2026_change_in_production",
        description="Secret key for JWT token signing"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Google OAuth
    GOOGLE_CLIENT_ID: str = Field(default="", description="Google OAuth Client ID")
    GOOGLE_CLIENT_SECRET: str = Field(default="", description="Google OAuth Client Secret")

    # CORS Settings — override in .env with BACKEND_CORS_ORIGINS=["https://your-domain.com"]
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://54.91.51.85:8000",
        "*",
    ]

    # Gemini Engine API Key
    GEMINI_API_KEY: str = Field(default="", description="Google Gemini API Key")
    GEMINI_API_KEY_BACKUP: str = Field(default="", description="Google Gemini Backup API Key")
    GEMINI_MODEL: str = "gemini-2.5-flash"

    # User Usage Limits
    MAX_GENERATIONS_PER_USER: int = Field(default=10, description="Max allowed video generations per user account")

    # AWS S3 Storage Config
    AWS_S3_BUCKET: str = Field(default="", description="AWS S3 Bucket Name for storing videos")
    AWS_ACCESS_KEY_ID: str = Field(default="", description="AWS Access Key ID")
    AWS_SECRET_ACCESS_KEY: str = Field(default="", description="AWS Secret Access Key")
    AWS_REGION: str = Field(default="us-east-1", description="AWS S3 Region")
    AWS_S3_CUSTOM_DOMAIN: str = Field(default="", description="Optional CloudFront or S3 custom domain")

    # Neo4j Knowledge Graph Config
    NEO4J_ENABLED: bool = Field(default=True, description="Enable or disable Neo4j Knowledge Graph integration")
    NEO4J_URI: str = Field(default="", description="Neo4j Connection URI e.g. neo4j+s://xxxx.databases.neo4j.io")
    NEO4J_USERNAME: str = Field(default="neo4j", description="Neo4j Username")
    NEO4J_PASSWORD: str = Field(default="", description="Neo4j Password")
    NEO4J_DATABASE: str = Field(default="neo4j", description="Neo4j Database Name")

    model_config = SettingsConfigDict(
        env_file=_ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()

