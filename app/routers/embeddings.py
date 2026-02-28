from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.auth_utils import get_current_user
from app.client.llm_client.cohere_client import embed_text

from app.models.embedding_model import MessageEmbedding
from app.schemas.embeddings import (
    SaveEmbeddingRequest, SaveEmbeddingResponse,
    SearchEmbeddingsRequest, SearchEmbeddingsResponse, SearchHit
)

router = APIRouter(prefix="/embeddings", tags=["Embeddings"])

EMBED_DIMS = 1024  # عدّليها لو dims عندك مختلفة


@router.post("/save", response_model=SaveEmbeddingResponse)
def save_embedding(
    payload: SaveEmbeddingRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    vec = embed_text(
        text=payload.text,
        model=payload.model or "embed-english-v3.0",
        input_type=payload.input_type,
        truncate=payload.truncate,
    )

    if len(vec) != EMBED_DIMS:
        raise HTTPException(status_code=400, detail=f"Embedding dims mismatch: got {len(vec)}, expected {EMBED_DIMS}")

    row = MessageEmbedding(
        user_id=current_user.id,
        conversation_id=payload.conversation_id,
        message_id=payload.message_id,
        content=payload.text,
        embedding=vec,
        model=payload.model or "embed-english-v3.0",
    )
    db.add(row)
    db.commit()
    db.refresh(row)

    return SaveEmbeddingResponse(id=row.id, dims=len(vec))


@router.post("/search", response_model=SearchEmbeddingsResponse)
def search_embeddings(
    payload: SearchEmbeddingsRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    qvec = embed_text(
        text=payload.query,
        model="embed-english-v3.0",
        input_type="search_query",
        truncate="END",
    )

    if len(qvec) != EMBED_DIMS:
        raise HTTPException(status_code=400, detail=f"Embedding dims mismatch: got {len(qvec)}, expected {EMBED_DIMS}")

    query = db.query(MessageEmbedding).filter(MessageEmbedding.user_id == current_user.id)

    if payload.conversation_id:
        query = query.filter(MessageEmbedding.conversation_id == payload.conversation_id)

    # cosine_distance: الأصغر = أقرب
    rows = (
        query.order_by(MessageEmbedding.embedding.cosine_distance(qvec))
        .limit(payload.top_k)
        .all()
    )

    hits = []
    for r in rows:
        # score بسيط: 1 - distance (تقريبًا)
        # (distance عادة بين 0 و 2 حسب التمثيل، لكن ده كفاية كمؤشر)
        dist = float(r.embedding.cosine_distance(qvec))  # قد لا تعمل كقيمة مباشرة في بايثون في بعض الإصدارات
        hits.append(
            SearchHit(
                id=r.id,
                content=r.content,
                message_id=r.message_id,
                conversation_id=r.conversation_id,
                score=1.0 - dist,
            )
        )

    return SearchEmbeddingsResponse(dims=len(qvec), hits=hits)