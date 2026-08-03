from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class VideoGenerateRequest(BaseModel):
    topic: str = Field(..., example="Explain Binary Search", description="Teaching topic or algorithm prompt")


class VideoResponse(BaseModel):
    id: Optional[int] = None
    status: str = "completed"
    video: str = Field(..., description="Local path to generated MP4 video")
    video_url: Optional[str] = Field(None, description="Public S3 URL or server stream URL")
    topic: str
    prompt: Optional[str] = None
    extracted_parameters: Optional[Dict[str, Any]] = None
    approach: Optional[Dict[str, Any]] = None
    dsl_code: Optional[Any] = None
    manim_code: Optional[str] = None
    created_at: Optional[datetime] = None
    usage_count: Optional[int] = None
    usage_limit: Optional[int] = None


class VideoHistoryItem(BaseModel):
    id: int
    topic: str
    prompt: Optional[str] = None
    status: str
    video_path: Optional[str] = None
    video_url: Optional[str] = None
    extracted_parameters: Optional[Dict[str, Any]] = None
    approach: Optional[Dict[str, Any]] = None
    dsl_code: Optional[Any] = None
    manim_code: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserUsageResponse(BaseModel):
    usage_count: int
    usage_limit: int
    is_limit_reached: bool

