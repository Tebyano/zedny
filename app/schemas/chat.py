from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class ConversationCreate(BaseModel):
    title: Optional[str] = Field(None, description="Optional conversation title")


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

    # لو حابة نفس file fields هنا كمان:
    file_url: Optional[str] = None
    file_path: Optional[str] = None
    file_name: Optional[str] = None
    file_mime: Optional[str] = None
    file_size_bytes: Optional[int] = None


class SendMessageRequest(BaseModel):
    content: str = Field(..., description="User message")
    max_tokens: int = 200
    temperature: float = 0.7
    model: str = "command-r-08-2024"


class SendMessageResponse(BaseModel):
    reply: str
    conversation_id: UUID