from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class VideoGeneration(Base):
    __tablename__ = "video_generations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=True)
    
    topic = Column(String(500), nullable=False)
    status = Column(String(50), default="pending", nullable=False)  # pending, processing, completed, failed
    video_path = Column(String(1024), nullable=True)
    
    # Store engine metadata output
    extracted_parameters = Column(JSON, nullable=True)
    approach = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationship
    owner = relationship("User", back_populates="videos")

    def __repr__(self):
        return f"<VideoGeneration id={self.id} topic='{self.topic}' status='{self.status}'>"
