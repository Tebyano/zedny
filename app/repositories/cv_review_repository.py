from sqlalchemy.orm import Session
from app.models.cv_review_model import CvReview

class CvReviewRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: dict) -> CvReview:
        obj = CvReview(**data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj