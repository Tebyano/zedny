from typing import Optional
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.chat_model import Conversation, Message


class ChatRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_conversation(self, user_id: int, title: str | None = None) -> Conversation:
        conv = Conversation(user_id=user_id, title=title)
        self.db.add(conv)
        self.db.commit()
        self.db.refresh(conv)
        return conv

    def list_conversations(self, user_id: int) -> list[Conversation]:
        return (
            self.db.query(Conversation)
            .filter(Conversation.user_id == user_id)
            .order_by(Conversation.created_at.desc())
            .all()
        )

    # ✅ نسخة "هادية" (مفيهاش raise) — ترجع None لو مش موجود
    def get_conversation_for_user(self, user_id: int, conversation_id: UUID) -> Optional[Conversation]:
        return (
            self.db.query(Conversation)
            .filter(Conversation.id == conversation_id, Conversation.user_id == user_id)
            .first()
        )

    # ✅ نسخة "صارمة" لو محتاجاها في endpoints معينة
    def get_conversation_for_user_or_404(self, user_id: int, conversation_id: UUID) -> Conversation:
        conv = self.get_conversation_for_user(user_id=user_id, conversation_id=conversation_id)
        if not conv:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return conv

    def set_title_if_empty(self, conv: Conversation, title: str) -> Conversation:
        if not conv.title:
            conv.title = (title or "")[:255]
            self.db.add(conv)
            self.db.commit()
            self.db.refresh(conv)
        return conv

    def add_message(self, conversation_id: UUID, role: str, content: str) -> Message:
        msg = Message(conversation_id=conversation_id, role=role, content=content)
        self.db.add(msg)
        self.db.commit()
        self.db.refresh(msg)
        return msg

    def get_messages(self, conversation_id: UUID) -> list[Message]:
        return (
            self.db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .all()
        )

    def get_last_messages(self, conversation_id: UUID, limit: int) -> list[Message]:
        msgs = (
            self.db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
            .all()
        )
        return list(reversed(msgs))