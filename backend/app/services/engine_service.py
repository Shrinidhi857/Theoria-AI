import logging
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.models.video import VideoGeneration
from app.schemas.engine import VideoGenerateRequest, VideoResponse, VideoHistoryItem
from engine.pipeline import generate_video

logger = logging.getLogger(__name__)


def process_video_generation(
    db: Session,
    request: VideoGenerateRequest,
    current_user: Optional[User] = None
) -> VideoResponse:
    """
    Triggers AI Teaching Engine pipeline for requested topic, records metadata in database,
    and returns formatted VideoResponse.
    """
    user_id = current_user.id if current_user else None

    # Create pending record in database
    video_record = VideoGeneration(
        user_id=user_id,
        topic=request.topic,
        status="processing"
    )
    db.add(video_record)
    db.commit()
    db.refresh(video_record)

    try:
        # Run AI Video Pipeline
        result: Dict[str, Any] = generate_video(request.topic)
        
        # Update record with output metadata
        video_record.status = "completed"
        video_record.video_path = result.get("video")
        video_record.extracted_parameters = result.get("extracted_parameters")
        video_record.approach = result.get("approach")
        db.commit()
        db.refresh(video_record)

        return VideoResponse(
            id=video_record.id,
            status="completed",
            video=result.get("video", ""),
            topic=request.topic,
            extracted_parameters=result.get("extracted_parameters"),
            approach=result.get("approach"),
            created_at=video_record.created_at
        )
    except Exception as e:
        logger.error(f"Error during video generation for topic '{request.topic}': {e}", exc_info=True)
        video_record.status = "failed"
        video_record.error = str(e)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Video engine processing failed: {str(e)}"
        )


def get_user_video_history(
    db: Session,
    user: User,
    skip: int = 0,
    limit: int = 50
) -> List[VideoHistoryItem]:
    """Retrieve video generation history for authenticated user."""
    records = db.query(VideoGeneration).filter(
        VideoGeneration.user_id == user.id
    ).order_by(VideoGeneration.created_at.desc()).offset(skip).limit(limit).all()
    
    return [VideoHistoryItem.model_validate(rec) for rec in records]


def get_video_by_id(
    db: Session,
    video_id: int,
    user: Optional[User] = None
) -> VideoHistoryItem:
    """Retrieve details for specific video generation record."""
    query = db.query(VideoGeneration).filter(VideoGeneration.id == video_id)
    if user:
        query = query.filter(VideoGeneration.user_id == user.id)
    
    record = query.first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Video with ID {video_id} not found."
        )
    
    return VideoHistoryItem.model_validate(record)
