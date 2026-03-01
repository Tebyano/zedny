from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional, List


class IngestVideoResponse(BaseModel):
    video_id: UUID
    status: str  # ready|failed

    source_type: str
    source_url: Optional[str] = None
    storage_url: Optional[str] = None

    title: Optional[str] = None
    description: Optional[str] = None
    duration_seconds: Optional[int] = None
    transcript: Optional[str] = None

    chunks_count: int = 0
    error: Optional[str] = None


class VideoOut(BaseModel):
    video_id: UUID
    status: str

    source_type: str
    source_url: Optional[str] = None
    storage_url: Optional[str] = None

    title: Optional[str] = None
    description: Optional[str] = None
    duration_seconds: Optional[int] = None
    transcript: Optional[str] = None
    error: Optional[str] = None


class SearchVideoRequest(BaseModel):
    video_id: UUID
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)


class SearchHit(BaseModel):
    chunk_index: int
    content: str


class SearchVideoResponse(BaseModel):
    video_id: UUID
    hits: List[SearchHit]