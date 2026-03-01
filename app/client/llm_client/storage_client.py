import os
import re
import unicodedata
import httpx
from typing import Optional


def _sanitize_object_key(key: str) -> str:
    key = (key or "").strip().replace("\\", "/")

    parts = []
    for part in key.split("/"):
        part = part.strip()
        if not part:
            continue

        part = unicodedata.normalize("NFKD", part)
        part = part.encode("ascii", "ignore").decode("ascii")
        part = re.sub(r"\s+", "_", part)
        part = re.sub(r"[^a-zA-Z0-9._-]", "", part)

        if not part:
            part = "file"

        parts.append(part)

    return "/".join(parts)


class StorageClient:
    def __init__(self, use_service_role: bool = True, bucket: str | None = None):
        self.supabase_url = os.getenv("SUPABASE_URL")
        if not self.supabase_url:
            raise RuntimeError("Missing SUPABASE_URL in environment")

        self.key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") if use_service_role else os.getenv("SUPABASE_ANON_KEY")
        if not self.key:
            raise RuntimeError(
                "Missing SUPABASE_SERVICE_ROLE_KEY" if use_service_role else "Missing SUPABASE_ANON_KEY"
            )

        self.bucket = bucket  # بس، من غير fallback للـ env
        if not self.bucket:
            raise RuntimeError("bucket is required")

    def upload_bytes(
        self,
        path: str,
        content: Optional[bytes] = None,  # llm.py بيستخدم content=
        data: Optional[bytes] = None,     # دعم إضافي
        content_type: str = "application/pdf",
        upsert: bool = True,
        **kwargs,
    ) -> dict:
        blob = content if content is not None else data
        if blob is None:
            raise ValueError("upload_bytes requires 'content' or 'data' (bytes).")

        safe_path = _sanitize_object_key(path)

        url = f"{self.supabase_url.rstrip('/')}/storage/v1/object/{self.bucket}/{safe_path}"

        headers = {
            "authorization": f"Bearer {self.key}",
            "apikey": self.key,
            "content-type": str(content_type),
            "x-upsert": "true" if upsert else "false",
        }

        with httpx.Client(timeout=120) as client:
            resp = client.post(url, headers=headers, content=blob)

        if resp.status_code not in (200, 201):
            raise RuntimeError(
                f"Supabase upload failed ({resp.status_code}): {resp.text}\n"
                f"Original path: {path}\nSanitized path: {safe_path}"
            )

        # رجّعي safe_path عشان تقدري تبني URL صح حتى لو الاسم اتغير
        try:
            payload = resp.json()
        except Exception:
            payload = {"status_code": resp.status_code, "text": resp.text}

        payload["_path"] = safe_path
        return payload

    def get_public_url(self, path: str) -> str:
        # URL للـ public bucket
        safe_path = _sanitize_object_key(path)
        return f"{self.supabase_url.rstrip('/')}/storage/v1/object/public/{self.bucket}/{safe_path}"