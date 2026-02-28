import uuid
from sqlalchemy import Column, Text, Integer, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector

from app.database import Base


class Video(Base):
    __tablename__ = "videos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    source_type = Column(String, nullable=False)  # upload|youtube
    source_url = Column(Text, nullable=True)
    storage_path = Column(Text, nullable=True)
    storage_url = Column(Text, nullable=True)

    title = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    transcript = Column(Text, nullable=True)

    status = Column(String, nullable=False, server_default="processing") 
    error = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class VideoChunk(Base):
    __tablename__ = "video_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)

    embedding = Column(Vector(1024), nullable=False)  
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)