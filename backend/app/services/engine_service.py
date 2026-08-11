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

try:
    from app.core.logging_config import setup_colored_logging
    logger = setup_colored_logging(__name__)
except ImportError:
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
            logger.warning(f"🚫 [Quota Exceeded] User ID {user_id} has reached generation limit ({usage_count}/{usage_limit}). HTTP 429 returned.")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"You have reached your maximum limit of {usage_limit} video generations. Please upgrade your account to generate more."
            )
        logger.info(f"✅ [Quota OK] User ID {user_id} — usage {usage_count}/{usage_limit}.")

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
    logger.info(f"📝 [DB] Created VideoGeneration record ID={video_record.id} for topic='{request.topic}' (status=processing).")

    try:
        # Run AI Video Pipeline
        logger.info(f"🚀 [Pipeline] Starting Multi-Agent AI Video Engine for topic='{request.topic}'...")
        result: Dict[str, Any] = generate_video(request.topic, user_id=user_id)
        
        local_video_path = result.get("video")
        s3_url = None
        file_size = None

        if local_video_path:
            # Always resolve to an absolute path — pipeline may return a relative one
            abs_video_path = os.path.abspath(local_video_path)
            logger.info(f"📹 [Pipeline] Video path returned: '{local_video_path}' → resolved to '{abs_video_path}'")

            if os.path.exists(abs_video_path):
                file_size = os.path.getsize(abs_video_path)
                logger.info(f"✅ [Pipeline] Video confirmed on disk — size: {file_size:,} bytes ({file_size / 1024:.1f} KB).")

                if s3_service.is_configured:
                    logger.info(f"☁️  [S3] S3 configured — starting upload for video record ID={video_record.id}...")
                    s3_url = s3_service.upload_video(
                        abs_video_path,
                        s3_key=f"videos/user_{user_id or 0}_vid_{video_record.id}.mp4"
                    )
                    if s3_url:
                        logger.info(f"✅ [S3] Upload successful! Public URL: {s3_url}")
                    else:
                        logger.warning("⚠️  [S3] Upload returned None — falling back to local video path.")
                else:
                    logger.info("ℹ️  [S3] Not configured. Serving video from local path.")
            else:
                logger.error(f"❌ [Pipeline] Video file NOT found at resolved path: '{abs_video_path}'. Check renderer output.")

        # Use S3 URL if upload succeeded, otherwise fall back to local path
        video_url_to_store = s3_url or local_video_path

        # Update record with output metadata & intermediate DSL code
        video_record.status = "completed"
        video_record.video_path = local_video_path
        video_record.video_url = video_url_to_store
        video_record.file_size_bytes = file_size
        video_record.extracted_parameters = result.get("extracted_parameters")
        video_record.approach = result.get("approach")
        video_record.dsl_code = result.get("dsl_code")
        video_record.manim_code = result.get("manim_code")
        db.commit()
        db.refresh(video_record)
        logger.info(f"✅ [DB] VideoGeneration record ID={video_record.id} updated — status=completed.")

        # Ingest knowledge metadata into Neo4j Global Knowledge Graph (Graceful Try-Except)
        try:
            knowledge_meta = result.get("knowledge_metadata")
            if knowledge_meta:
                from app.services.graph_service import GraphService, validate_and_clean_metadata
                logger.info(f"🔗 [Neo4j] Ingesting knowledge metadata for lesson ID={video_record.id} into Knowledge Graph...")
                meta_obj = validate_and_clean_metadata(knowledge_meta)
                GraphService.ingest_knowledge_metadata(
                    lesson_id=str(video_record.id),
                    title=request.topic,
                    user_id=user_id,
                    metadata=meta_obj
                )
                logger.info(f"✅ [Neo4j] Knowledge metadata ingested successfully for topic='{request.topic}'.")
        except Exception as graph_err:
            logger.warning(f"⚠️  [Neo4j] Post-generation graph update error (non-fatal): {graph_err}")

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
        logger.error(f"❌ [Pipeline ERROR] Video generation FAILED for topic='{request.topic}': {e}", exc_info=True)
        video_record.status = "failed"
        video_record.error = str(e)
        db.commit()
        logger.error(f"❌ [DB] VideoGeneration record ID={video_record.id} marked as FAILED.")
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
