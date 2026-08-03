import os
import logging
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.core.config import settings
from app.models.user import User
from app.models.video import VideoGeneration
from app.schemas.engine import VideoGenerateRequest, VideoResponse, VideoHistoryItem, UserUsageResponse
from app.services.s3_service import s3_service
from engine.pipeline import generate_video

logger = logging.getLogger(__name__)


def get_user_generation_count(db: Session, user_id: int) -> int:
    """Returns total successful or processing video generations created by user."""
    return db.query(VideoGeneration).filter(
        VideoGeneration.user_id == user_id,
        VideoGeneration.status.in_(["completed", "processing"])
    ).count()


def get_user_usage(db: Session, user: User) -> UserUsageResponse:
    """Returns usage stats for user including max generation limit."""
    count = get_user_generation_count(db, user.id)
    limit = settings.MAX_GENERATIONS_PER_USER
    return UserUsageResponse(
        usage_count=count,
        usage_limit=limit,
        is_limit_reached=(count >= limit)
    )


def process_video_generation(
    db: Session,
    request: VideoGenerateRequest,
    current_user: Optional[User] = None
) -> VideoResponse:
    """
    Triggers AI Teaching Engine pipeline for requested topic, checks user generation limits,
    uploads MP4 output to S3 if configured, records metadata in database, and returns VideoResponse.
    """
    user_id = current_user.id if current_user else None

    # Enforce per-user generation quota limit if user is authenticated
    usage_count = 0
    usage_limit = settings.MAX_GENERATIONS_PER_USER

    if user_id:
        usage_count = get_user_generation_count(db, user_id)
        if usage_count >= usage_limit:
            logger.warning(f"User ID {user_id} reached generation limit ({usage_count}/{usage_limit}).")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"You have reached your maximum limit of {usage_limit} video generations. Please upgrade your account to generate more."
            )

    # Create pending record in database
    video_record = VideoGeneration(
        user_id=user_id,
        topic=request.topic,
        prompt=request.topic,
        status="processing"
    )
    db.add(video_record)
    db.commit()
    db.refresh(video_record)

    try:
        # Run AI Video Pipeline
        result: Dict[str, Any] = generate_video(request.topic)
        
        local_video_path = result.get("video")
        s3_url = None
        file_size = None

        if local_video_path and os.path.exists(local_video_path):
            file_size = os.path.getsize(local_video_path)
            # Upload to AWS S3 if credentials & bucket are configured
            s3_url = s3_service.upload_video(local_video_path, s3_key=f"videos/user_{user_id or 0}_vid_{video_record.id}.mp4")

        # Update record with output metadata & intermediate DSL code
        video_record.status = "completed"
        video_record.video_path = local_video_path
        video_record.video_url = s3_url or local_video_path
        video_record.file_size_bytes = file_size
        video_record.extracted_parameters = result.get("extracted_parameters")
        video_record.approach = result.get("approach")
        video_record.dsl_code = result.get("dsl_code")
        video_record.manim_code = result.get("manim_code")
        db.commit()
        db.refresh(video_record)

        new_usage_count = get_user_generation_count(db, user_id) if user_id else usage_count + 1

        return VideoResponse(
            id=video_record.id,
            status="completed",
            video=local_video_path or "",
            video_url=video_record.video_url,
            topic=request.topic,
            prompt=request.topic,
            extracted_parameters=result.get("extracted_parameters"),
            approach=result.get("approach"),
            dsl_code=result.get("dsl_code"),
            manim_code=result.get("manim_code"),
            created_at=video_record.created_at,
            usage_count=new_usage_count,
            usage_limit=usage_limit
        )
    except Exception as e:
        logger.error(f"Error during video generation for topic '{request.topic}': {e}", exc_info=True)
        video_record.status = "failed"
        video_record.error = str(e)
        db.commit()
        if isinstance(e, HTTPException):
            raise e
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
