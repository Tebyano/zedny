import os
from typing import Optional, Dict, Any, List
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.client.llm_client import cohere_client
from app.models.chat_model import Conversation, Message


def _default_model() -> str:
    return os.getenv("COHERE_MODEL", "command-r")


class ChatService:
    def __init__(self, db: Session):
        self.db = db

    def _list_conversations(self, user_id: int) -> List[Conversation]:
        return (
            self.db.query(Conversation)
            .filter(Conversation.user_id == user_id)
            .order_by(desc(Conversation.created_at))
            .all()
        )

    def _get_conversation(self, user_id: int, conversation_id: UUID) -> Optional[Conversation]:
        return (
            self.db.query(Conversation)
            .filter(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id,
            )
            .first()
        )

    def _create_conversation(self, user_id: int, title: Optional[str] = None) -> Conversation:
        conv = Conversation(user_id=user_id, title=title)
        self.db.add(conv)
        self.db.commit()
        self.db.refresh(conv)
        return conv

    def _get_messages(self, conversation_id: UUID, limit: int) -> List[Message]:
        q = (
            self.db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(desc(Message.created_at))
        )
        if limit and limit > 0:
            q = q.limit(limit)

        # رجّعهم بالترتيب الصحيح (قديم -> جديد)
        return list(reversed(q.all()))

    def _cohere_reply(
        self,
        user_message: str,
        history: List[Message],
        model: Optional[str],
        temperature: float,
        max_tokens: int,
    ) -> str:
        chosen_model = model or _default_model()

        chat_history = []
        for m in history:
            if m.role == "user":
                chat_history.append({"role": "USER", "message": m.content})
            elif m.role == "assistant":
                chat_history.append({"role": "CHATBOT", "message": m.content})

        if hasattr(cohere_client, "chat"):
            resp = cohere_client.chat(
                message=user_message,
                model=chosen_model,
                chat_history=chat_history[:-1] if chat_history else [],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return getattr(resp, "text", None) or str(resp)

        if hasattr(cohere_client, "generate_text"):
            prompt = ""
            for h in history:
                prompt += f"{h.role.upper()}: {h.content}\n"
            prompt += "ASSISTANT:"
            return cohere_client.generate_text(prompt=prompt, max_tokens=max_tokens)

        raise RuntimeError("No supported Cohere method found on cohere_client (chat/generate_text).")

    def handle_chat(
        self,
        user_id: int,
        conversation_id: Optional[UUID],
        content: Optional[str],
        model: Optional[str],
        max_tokens: int,
        temperature: float,
        history_limit: int,
    ) -> Dict[str, Any]:
        # 1) لو content فاضية:
        # - لو conversation_id فاضي => list
        # - لو conversation_id موجود => history (ولو مش موجودة نعمل واحدة جديدة بدل 404)
        if not content:
            if conversation_id is None:
                convs = self._list_conversations(user_id=user_id)
                return {"mode": "list", "conversations": convs}

            conv = self._get_conversation(user_id=user_id, conversation_id=conversation_id)
            if conv is None:
                # بدل "Conversation not found" نبدأ محادثة جديدة
                conv = self._create_conversation(user_id=user_id, title=None)

            msgs = self._get_messages(conversation_id=conv.id, limit=history_limit)
            return {"mode": "history", "conversation": conv, "messages": msgs}

        # 2) content موجود => send
        # المطلوب: conversation_id اختياري
        # - لو None => محادثة جديدة
        # - لو موجود بس مش لاقيها => محادثة جديدة (fallback) بدل 404
        if conversation_id is None:
            conv = self._create_conversation(user_id=user_id, title=content[:60])
        else:
            conv = self._get_conversation(user_id=user_id, conversation_id=conversation_id)
            if conv is None:
                conv = self._create_conversation(user_id=user_id, title=content[:60])

        # أضف رسالة اليوزر
        user_msg = Message(conversation_id=conv.id, role="user", content=content)
        self.db.add(user_msg)
        self.db.commit()

        # هات history (بعد إضافة رسالة اليوزر)
        history_msgs = self._get_messages(conversation_id=conv.id, limit=history_limit)

        # ولّد رد
        reply_text = self._cohere_reply(
            user_message=content,
            history=history_msgs,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        # أضف رد المساعد
        assistant_msg = Message(conversation_id=conv.id, role="assistant", content=reply_text)
        self.db.add(assistant_msg)
        self.db.commit()

        # رجّع messages (يشمل رد المساعد)
        final_msgs = self._get_messages(conversation_id=conv.id, limit=history_limit)

        return {
            "mode": "send",
            "conversation": conv,
            "reply": reply_text,
            "messages": final_msgs,
        }