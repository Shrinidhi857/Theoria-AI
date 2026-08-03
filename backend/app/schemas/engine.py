from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class VideoGenerateRequest(BaseModel):
    topic: str = Field(..., example="Explain Binary Search", description="Teaching topic or algorithm prompt")


class VideoResponse(BaseModel):
    id: Optional[int] = None
    status: str = "completed"
    video: str = Field(..., description="Path or URL to generated MP4 video")
    topic: str
    extracted_parameters: Optional[Dict[str, Any]] = None
    approach: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None


class VideoHistoryItem(BaseModel):
    id: int
    topic: str
    status: str
    video_path: Optional[str] = None
    extracted_parameters: Optional[Dict[str, Any]] = None
    approach: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
