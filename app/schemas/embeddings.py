from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional, List


class SaveEmbeddingRequest(BaseModel):
    text: str = Field(..., min_length=1)
    model: Optional[str] = None
    input_type: str = "search_document"
    truncate: str = "END"

    conversation_id: Optional[UUID] = None
    message_id: Optional[UUID] = None


class SaveEmbeddingResponse(BaseModel):
    id: UUID
    dims: int


class SearchEmbeddingsRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = 5
    conversation_id: Optional[UUID] = None


class SearchHit(BaseModel):
    id: UUID
    content: Optional[str] = None
    message_id: Optional[UUID] = None
    conversation_id: Optional[UUID] = None
    score: float  # أعلى = أقرب


class SearchEmbeddingsResponse(BaseModel):
    dims: int
    hits: List[SearchHit]