from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class VideoGeneration(Base):
    __tablename__ = "video_generations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=True)
    
    topic = Column(String(500), nullable=False)
    prompt = Column(Text, nullable=True)  # Full raw user prompt/input
    status = Column(String(50), default="pending", nullable=False)  # pending, processing, completed, failed
    video_path = Column(String(1024), nullable=True)
    video_url = Column(String(2048), nullable=True)  # S3 public object URL or CDN URL
    file_size_bytes = Column(Integer, nullable=True)
    
    # Store engine metadata output & intermediate animation DSL code
    extracted_parameters = Column(JSON, nullable=True)
    approach = Column(JSON, nullable=True)
    dsl_code = Column(JSON, nullable=True)  # Intermediate animation DSL JSON structure
    manim_code = Column(Text, nullable=True)  # Generated Python Manim script
    error = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationship
    owner = relationship("User", back_populates="videos")

    def __repr__(self):
        return f"<VideoGeneration id={self.id} topic='{self.topic}' status='{self.status}'>"
