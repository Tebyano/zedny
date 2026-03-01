import json
import re
import uuid
from typing import List, Optional, Tuple

import fitz  # PyMuPDF
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.repositories.cv_review_repository import CvReviewRepository
from app.client.llm_client.storage_client import StorageClient
from app.client.llm_client.cohere_client import chat_completion


class CvReviewService:
    def __init__(self, db: Session, bucket: str = "cv-files"):
        self.db = db
        self.repo = CvReviewRepository(db)
        self.storage = StorageClient(bucket=bucket)
        self.bucket = bucket

    async def review_cv(self, file: UploadFile) -> dict:
        if file.content_type != "application/pdf":
            raise ValueError("Only PDF files are allowed.")

        pdf_bytes = await file.read()

        object_key = f"cvs/{uuid.uuid4().hex}.pdf"
        self._upload_pdf(bucket=self.bucket, object_key=object_key, content=pdf_bytes)
        file_url = self._get_file_url(bucket=self.bucket, object_key=object_key)

        text = self._extract_text_from_pdf(pdf_bytes)

        # استخدام Cohere لاستخراج المعلومات
        extracted = self._extract_with_cohere(text)

        candidate_name = extracted.get("candidate_name")
        years_exp = extracted.get("years_of_experience")
        skills = extracted.get("technical_skills", [])
        grad_year = extracted.get("graduation_year")
        university = extracted.get("university")
        faculty = extracted.get("faculty")

        obj = self.repo.create({
            "original_filename": file.filename,
            "file_name": file.filename,
            "file_url": file_url,
            "cv_file_path": object_key,
            "cv_file_url": file_url,
            "raw_text": text,
            "candidate_name": candidate_name,
            "years_of_experience": years_exp,
            "technical_skills": skills,
            "graduation_year": grad_year,
            "university": university,
            "faculty": faculty,
            "extraction_source": "cohere",
        })

        return {
            "id": obj.id,
            "cv_file_url": obj.cv_file_url,
            "candidate_name": obj.candidate_name,
            "years_of_experience": obj.years_of_experience,
            "technical_skills": skills,
            "graduation_year": obj.graduation_year,
            "university": obj.university,
            "faculty": obj.faculty,
            "extraction_source": obj.extraction_source,
        }

    def _extract_with_cohere(self, text: str) -> dict:
        prompt = f"""Extract the following information from this CV text and return ONLY a valid JSON object with no extra text:

{{
  "candidate_name": "full name of the candidate or null",
  "years_of_experience": integer or null,
  "technical_skills": ["list", "of", "technical", "skills"],
  "graduation_year": integer or null,
  "university": "university name or null",
  "faculty": "faculty/department name or null"
}}

CV Text:
{text[:4000]}

Return only the JSON object, nothing else."""

        response = chat_completion(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.1,
        )

        try:
            # نظف الرد من أي markdown
            clean = response.strip()
            clean = re.sub(r"```json|```", "", clean).strip()
            return json.loads(clean)
        except Exception:
            return {}

    def _upload_pdf(self, bucket: str, object_key: str, content: bytes) -> None:
        if hasattr(self.storage, "upload_bytes"):
            self.storage.upload_bytes(
                bucket=bucket,
                path=object_key,
                content=content,
                content_type="application/pdf"
            )
            return
        if hasattr(self.storage, "upload_file"):
            self.storage.upload_file(content, object_key)
            return
        raise RuntimeError("StorageClient does not expose a supported upload method.")

    def _get_file_url(self, bucket: str, object_key: str) -> str:
        if hasattr(self.storage, "get_public_url"):
            try:
                return self.storage.get_public_url(object_key)
            except TypeError:
                return self.storage.get_public_url(bucket=bucket, path=object_key)
        if hasattr(self.storage, "create_signed_url"):
            return self.storage.create_signed_url(bucket=bucket, path=object_key, expires_in=3600)
        return ""

    def _extract_text_from_pdf(self, pdf_bytes: bytes) -> str:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        texts = [page.get_text("text") for page in doc]
        return "\n".join(texts).strip()