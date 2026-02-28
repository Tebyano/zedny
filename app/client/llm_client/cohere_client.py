from __future__ import annotations

import os
from typing import Any

import cohere
from app.core.config import settings


def _extract_text_from_chat_response(response: Any) -> str | None:
    """
    يدعم أكثر من شكل لرد Cohere V2:
    - response.message.content = [{text: "..."}]
    - أو response.text
    """
    msg = getattr(response, "message", None)
    content = getattr(msg, "content", None) if msg else None

    if content:
        for block in content:
            text = getattr(block, "text", None)
            if text:
                return text

    text = getattr(response, "text", None)
    if text:
        return text

    return None


def _is_model_removed_error(e: Exception) -> bool:
    s = str(e).lower()
    return ("was removed" in s) or ("status_code: 404" in s and "model" in s) or ("model not found" in s)


def _sanitize_model_name(m: str | None) -> str | None:
    if not m:
        return m
    if m.strip().lower() == "command":
        return "command-r"
    return m.strip()


FALLBACK_MODELS = ["command-r-08-2024", "c4ai-aya-expanse-32b"]

_api_key = getattr(settings, "cohere_api_key", None) or os.getenv("COHERE_API_KEY")
co = cohere.ClientV2(_api_key) if _api_key else None


def chat_completion(
    messages: list[dict],
    max_tokens: int = 200,
    temperature: float = 0.7,
    model: str | None = None,
) -> str:
    if not co:
        return "Error: Cohere client not initialized. Set COHERE_API_KEY."

    primary_model = (
        _sanitize_model_name(model)
        or _sanitize_model_name(getattr(settings, "cohere_model", None) or os.getenv("COHERE_MODEL"))
        or "command-r"
    )

    models_to_try: list[str] = []
    for m in [primary_model, *FALLBACK_MODELS]:
        m = _sanitize_model_name(m)
        if m and m not in models_to_try:
            models_to_try.append(m)

    last_err: Exception | None = None

    for m in models_to_try:
        try:
            response = co.chat(
                model=m,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            text = _extract_text_from_chat_response(response)
            if text:
                return text
            return "Error: Empty response text from Cohere Chat API."
        except Exception as e:
            last_err = e
            # لو الخطأ مش خاص بموديل متشال/غير موجود، اكسري بدل ما نكمل
            if not _is_model_removed_error(e):
                break

    return f"Error: {str(last_err)}" if last_err else "Error: Unknown Cohere error."


def generate_text(
    prompt: str,
    max_tokens: int = 200,
    temperature: float = 0.7,
    model: str | None = None,
) -> str:
    return chat_completion(
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=temperature,
        model=model,
    )


def embed_text(
    text: str,
    model: str | None = None,
    input_type: str = "search_document",
    truncate: str = "END",
) -> list[float]:
    """
    ترجع embedding واحدة لنص واحد.
    """
    if not co:
        raise RuntimeError("Cohere client not initialized. Set COHERE_API_KEY.")

    embed_model = (
        _sanitize_model_name(model)
        or _sanitize_model_name(getattr(settings, "cohere_embed_model", None) or os.getenv("COHERE_EMBED_MODEL"))
        or "embed-english-v3.0"
    )

    resp = co.embed(
        model=embed_model,
        texts=[text],
        input_type=input_type,
        truncate=truncate,
    )

    embeddings = getattr(resp, "embeddings", None)

    # Case 1: embeddings is list[list[float]]
    if isinstance(embeddings, list) and embeddings and isinstance(embeddings[0], list):
        return embeddings[0]

    # Case 2: embeddings is an object with .float
    floats = getattr(embeddings, "float", None) if embeddings is not None else None
    if isinstance(floats, list) and floats and isinstance(floats[0], list):
        return floats[0]

    raise RuntimeError(f"Unexpected embed response format: {resp}")