from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_active_user, get_optional_current_user
from app.models.user import User
from app.schemas.engine import VideoGenerateRequest, VideoResponse, VideoHistoryItem
from app.services.engine_service import (
    process_video_generation,
    get_user_video_history,
    get_video_by_id
)

router = APIRouter(prefix="/engine", tags=["Engine"])


@router.post("/generate", response_model=VideoResponse)
def generate_video_endpoint(
    request: VideoGenerateRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Trigger the AI Teaching Engine pipeline to generate a Manim video lesson.
    If authenticated, links video generation history to user profile.
    """
    return process_video_generation(db=db, request=request, current_user=current_user)


@router.get("/videos", response_model=List[VideoHistoryItem])
def get_user_videos(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieve history of video generation tasks created by current authenticated user.
    """
    return get_user_video_history(db=db, user=current_user, skip=skip, limit=limit)


@router.get("/videos/{video_id}", response_model=VideoHistoryItem)
def get_video_details(
    video_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Get generation details and output video file path for a specific video ID.
    """
    return get_video_by_id(db=db, video_id=video_id, user=current_user)
