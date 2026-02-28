import uuid
from sqlalchemy import Column, Text, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector

from app.database import Base


class MessageEmbedding(Base):
    __tablename__ = "message_embeddings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    content = Column(Text, nullable=True)

    # ✅ لازم تطابق vector(1024) في Supabase
    embedding = Column(Vector(1024), nullable=False)

    model = Column(String(100), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)