from sqlalchemy import Column, Integer, String, Text, DateTime, func, ARRAY
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.database import Base


class CvReview(Base):
    __tablename__ = "cv_reviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    original_filename = Column(String(255), nullable=True)
    file_name = Column(Text, nullable=True)
    file_url = Column(Text, nullable=True)
    cv_file_path = Column(String(500), nullable=True)
    cv_file_url = Column(String(1000), nullable=True)

    raw_text = Column(Text, nullable=True)
    candidate_name = Column(Text, nullable=True)

    years_of_experience = Column(Integer, nullable=True)
    technical_skills = Column(ARRAY(Text), nullable=True)

    graduation_year = Column(Integer, nullable=True)
    university = Column(Text, nullable=True)
    faculty = Column(Text, nullable=True)

    extraction_source = Column(String(50), nullable=False, default="rules")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())