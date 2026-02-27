# app/routers/llm.py

from fastapi import APIRouter
from pydantic import BaseModel
from app.client.llm_client import cohere_client  # استدعاء الملف كامل

router = APIRouter(
    prefix="/llm",
    tags=["LLM"]
)

class LLMRequest(BaseModel):
    prompt: str
    max_tokens: int = 50

@router.post("/generate")
async def generate_text_endpoint(request: LLMRequest):
    text = cohere_client.generate_text(
        prompt=request.prompt,
        max_tokens=request.max_tokens
    )
    return {"text": text}