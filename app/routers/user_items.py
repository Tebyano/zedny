from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.user_item import UserItemCreate, UserItemResponse
from app.services.user_item_service import UserItemService

router = APIRouter(
    prefix="/user_items",
    tags=["User Items"]  # ✅ موحد
)


@router.post("/", response_model=UserItemResponse)
def assign_item_to_user(assignment: UserItemCreate, db: Session = Depends(get_db)):
    service = UserItemService(db)
    result = service.assign_item(assignment)
    return UserItemResponse(
        user_id=result.user_id,
        item_id=result.item_id
    )


@router.get("/", response_model=List[UserItemResponse])
def list_user_items(db: Session = Depends(get_db)):
    service = UserItemService(db)
    assignments = service.get_user_items()
    return [
        UserItemResponse(
            user_id=a.user_id,
            item_id=a.item_id
        )
        for a in assignments
    ]