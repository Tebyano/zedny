from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID

class CvReviewOut(BaseModel):
    id: UUID
    cv_file_url: Optional[str] = None
    candidate_name: Optional[str] = None
    years_of_experience: Optional[int] = None
    technical_skills: List[str] = []
    graduation_year: Optional[int] = None
    university: Optional[str] = None
    faculty: Optional[str] = None
    extraction_source: str

    class Config:
        from_attributes = True