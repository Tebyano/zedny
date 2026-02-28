from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class LLMRequest(BaseModel):
    prompt: str
    max_tokens: int = 50


class LLMResponse(BaseModel):
    text: str


class ChatRequest(BaseModel):
    conversation_id: Optional[UUID] = None
    content: Optional[str] = None

    max_tokens: int = 200
    temperature: float = 0.7

    model: Optional[str] = Field(
        default=None,
        description="Optional. If omitted, server uses COHERE_MODEL from .env",
    )
    history_limit: int = 20


class ConversationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: Optional[str] = None
    created_at: datetime


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    role: str
    content: str
    created_at: datetime

    file_url: Optional[str] = None
    file_path: Optional[str] = None
    file_name: Optional[str] = None
    file_mime: Optional[str] = None
    file_size_bytes: Optional[int] = None


class ChatResponse(BaseModel):
    mode: str  # list | history | send
    conversation: Optional[ConversationOut] = None
    reply: Optional[str] = None
    messages: Optional[List[MessageOut]] = None
    conversations: Optional[List[ConversationOut]] = None


# ✅ Embed: text فقط + حفظ تلقائي
class EmbedRequest(BaseModel):
    text: str = Field(..., min_length=1)


class EmbedResponse(BaseModel):
    saved_id: UUID
    dims: int
    embedding: List[float]


class UploadPDFResponse(BaseModel):
    conversation_id: UUID
    message_id: UUID
    file_name: str
    url: str
    path: str
    size_bytes: int


class UploadImageResponse(BaseModel):
    conversation_id: UUID
    message_id: UUID
    file_name: str
    file_mime: str
    url: str
    path: str
    size_bytes: int