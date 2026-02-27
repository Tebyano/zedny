import os
import tempfile

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status, BackgroundTasks
from sqlalchemy.orm import Session
from uuid import UUID, uuid4

from app.database import get_db, SessionLocal
from app.core.auth_utils import get_current_user

from app.client.llm_client import cohere_client
from app.services.chat_service import ChatService

from app.client.llm_client.cohere_client import embed_text
from app.client.llm_client.storage_client import StorageClient

from app.models.chat_model import Conversation, Message
from app.models.embedding_model import MessageEmbedding

from app.models.video_model import Video, VideoChunk
from app.schemas.video import IngestVideoResponse, VideoOut, SearchVideoRequest, SearchVideoResponse, SearchHit
from app.services.video_ingest_service import process_video_ingest

from app.schemas.llm import (
    LLMRequest,
    LLMResponse,
    ChatRequest,
    ChatResponse,
    ConversationOut,
    MessageOut,
    EmbedRequest,
    EmbedResponse,
    UploadPDFResponse,
    UploadImageResponse,
)

router = APIRouter(prefix="/llm", tags=["LLM"])

EMBED_MODEL = "embed-english-v3.0"
EMBED_DIMS = 1024


@router.post("/generate", response_model=LLMResponse)
async def generate_text_endpoint(request: LLMRequest):
    text = cohere_client.generate_text(prompt=request.prompt, max_tokens=request.max_tokens)
    return {"text": text}


@router.post("/embed", response_model=EmbedResponse)
def embed_endpoint(
    payload: EmbedRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    vec = embed_text(
        text=payload.text,
        model=EMBED_MODEL,
        input_type="search_document",
        truncate="END",
    )

    if len(vec) != EMBED_DIMS:
        raise HTTPException(
            status_code=400,
            detail=f"Embedding dims mismatch: got {len(vec)}, expected {EMBED_DIMS}",
        )

    row = MessageEmbedding(
        user_id=current_user.id,
        content=payload.text,
        embedding=vec,
        model=EMBED_MODEL,
    )
    db.add(row)
    db.commit()
    db.refresh(row)

    return {"saved_id": row.id, "dims": len(vec), "embedding": vec}


@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = ChatService(db)

    result = service.handle_chat(
        user_id=current_user.id,
        conversation_id=payload.conversation_id,
        content=payload.content,
        model=payload.model,
        max_tokens=payload.max_tokens,
        temperature=payload.temperature,
        history_limit=payload.history_limit,
    )

    mode = result.get("mode")

    if mode == "list":
        convs = result.get("conversations", [])
        return {
            "mode": "list",
            "conversations": [ConversationOut.model_validate(c) for c in convs],
        }

    if mode == "history":
        conv = result.get("conversation")
        msgs = result.get("messages", [])
        if conv is None:
            return {"mode": "history", "conversation": None, "messages": []}

        return {
            "mode": "history",
            "conversation": ConversationOut.model_validate(conv),
            "messages": [MessageOut.model_validate(m) for m in msgs],
        }

    if mode == "send":
        conv = result.get("conversation")
        msgs = result.get("messages", [])

        if conv is None:
            raise HTTPException(status_code=500, detail="ChatService returned no conversation")

        return {
            "mode": "send",
            "conversation": ConversationOut.model_validate(conv),
            "reply": result.get("reply"),
            "messages": [MessageOut.model_validate(m) for m in msgs],
        }

    raise HTTPException(status_code=500, detail=f"Unknown mode from ChatService: {mode}")


@router.post("/upload-pdf", response_model=UploadPDFResponse)
async def upload_pdf_endpoint(
    file: UploadFile = File(...),
    conversation_id: UUID | None = Form(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty file")

    conv = None
    if conversation_id:
        conv = (
            db.query(Conversation)
            .filter(Conversation.id == conversation_id, Conversation.user_id == current_user.id)
            .first()
        )

    if conv is None:
        conv = Conversation(user_id=current_user.id, title=f"PDF: {(file.filename or '')[:60]}")
        db.add(conv)
        db.commit()
        db.refresh(conv)

    storage = StorageClient(use_service_role=True)
    path = f"user_{current_user.id}/{uuid4()}_{file.filename or 'file.pdf'}"

    upload_result = storage.upload_bytes(
        path=path,
        content=data,
        content_type="application/pdf",
        upsert=True,
    )

    safe_path = upload_result.get("_path") or path
    url = storage.get_public_url(safe_path)

    msg = Message(
        conversation_id=conv.id,
        role="user",
        content=f"Uploaded PDF: {file.filename}",
        file_url=url,
        file_path=safe_path,
        file_name=file.filename,
        file_mime="application/pdf",
        file_size_bytes=len(data),
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)

    return UploadPDFResponse(
        conversation_id=conv.id,
        message_id=msg.id,
        file_name=file.filename,
        url=url,
        path=safe_path,
        size_bytes=len(data),
    )


@router.post("/upload-image", response_model=UploadImageResponse)
async def upload_image_endpoint(
    file: UploadFile = File(...),
    conversation_id: UUID | None = Form(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Only image files are allowed. Got: {file.content_type}",
        )

    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty file")

    max_bytes = 10 * 1024 * 1024
    if len(data) > max_bytes:
        raise HTTPException(status_code=400, detail="Image too large (max 10MB)")

    conv = None
    if conversation_id:
        conv = (
            db.query(Conversation)
            .filter(Conversation.id == conversation_id, Conversation.user_id == current_user.id)
            .first()
        )

    if conv is None:
        conv = Conversation(user_id=current_user.id, title=f"Image: {(file.filename or '')[:60]}")
        db.add(conv)
        db.commit()
        db.refresh(conv)

    storage = StorageClient(use_service_role=True)
    filename = file.filename or "image"
    path = f"user_{current_user.id}/{uuid4()}_{filename}"

    upload_result = storage.upload_bytes(
        path=path,
        content=data,
        content_type=file.content_type,
        upsert=True,
    )

    safe_path = upload_result.get("_path") or path
    url = storage.get_public_url(safe_path)

    msg = Message(
        conversation_id=conv.id,
        role="user",
        content=f"Uploaded image: {filename}",
        file_url=url,
        file_path=safe_path,
        file_name=filename,
        file_mime=file.content_type,
        file_size_bytes=len(data),
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)

    return UploadImageResponse(
        conversation_id=conv.id,
        message_id=msg.id,
        file_name=filename,
        file_mime=file.content_type,
        url=url,
        path=safe_path,
        size_bytes=len(data),
    )


# =========================
# ✅ VIDEO INGEST ENDPOINTS
# =========================

@router.post("/ingest-video", response_model=IngestVideoResponse)
async def ingest_video_endpoint(
    background_tasks: BackgroundTasks,
    youtube_url: str | None = Form(None),
    file: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if (not youtube_url and not file) or (youtube_url and file):
        raise HTTPException(status_code=400, detail="Send either youtube_url OR file")

    video = Video(
        user_id=current_user.id,
        source_type="youtube" if youtube_url else "upload",
        source_url=youtube_url,
        status="processing",
    )
    db.add(video)
    db.commit()
    db.refresh(video)

    tmp_path = None
    filename = None

    if file:
        filename = file.filename
        suffix = os.path.splitext(filename or "")[1] or ".mp4"
        fd, tmp_path = tempfile.mkstemp(suffix=suffix)
        os.close(fd)
        content = await file.read()
        with open(tmp_path, "wb") as f:
            f.write(content)

    def job():
        s = SessionLocal()
        try:
            process_video_ingest(
                db=s,
                video_id=video.id,
                user_id=current_user.id,
                source_type=video.source_type,
                youtube_url=youtube_url,
                uploaded_video_path=tmp_path,
                uploaded_filename=filename,
            )
        finally:
            s.close()
            if tmp_path and os.path.exists(tmp_path):
                os.remove(tmp_path)

    background_tasks.add_task(job)
    return IngestVideoResponse(video_id=video.id, status="processing")


@router.get("/videos/{video_id}", response_model=VideoOut)
def get_video_endpoint(
    video_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    v = db.query(Video).filter(Video.id == video_id, Video.user_id == current_user.id).first()
    if not v:
        raise HTTPException(status_code=404, detail="Video not found")

    return VideoOut(
        video_id=v.id,
        status=v.status,
        source_type=v.source_type,
        source_url=v.source_url,
        storage_url=v.storage_url,
        title=v.title,
        description=v.description,
        duration_seconds=v.duration_seconds,
        transcript=v.transcript,
        error=v.error,
    )


@router.post("/videos/search", response_model=SearchVideoResponse)
def search_video_chunks_endpoint(
    payload: SearchVideoRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    qvec = embed_text(
        text=payload.query,
        model=EMBED_MODEL,
        input_type="search_query",
        truncate="END",
    )

    rows = (
        db.query(VideoChunk)
        .filter(
            VideoChunk.user_id == current_user.id,
            VideoChunk.video_id == payload.video_id,
        )
        .order_by(VideoChunk.embedding.cosine_distance(qvec))
        .limit(payload.top_k)
        .all()
    )

    hits = [SearchHit(chunk_index=r.chunk_index, content=r.content) for r in rows]
    return SearchVideoResponse(video_id=payload.video_id, hits=hits)