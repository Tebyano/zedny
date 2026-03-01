from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
import traceback

from app.database import get_db
from app.schemas.cv_review import CvReviewOut
from app.services.cv_review_service import CvReviewService
from app.core.auth_utils import get_current_user

router = APIRouter(prefix="/cv-review", tags=["CV Review"])

@router.post("", response_model=CvReviewOut)
async def cv_review_endpoint(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        service = CvReviewService(db, bucket="cv-files")
        return await service.review_cv(file)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
