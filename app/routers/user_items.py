from fastapi import APIRouter, Depends
from app.database import get_db
from app.schemas.user_item import UserItemCreate
from app.services.user_item_service import assign_item, get_user_items

router = APIRouter(prefix="/user_item", tags=["user-item"])

@router.post("/")
def assign_item_to_user(assignment: UserItemCreate, db=Depends(get_db)):
    return assign_item(db, assignment)

@router.get("/")
def list_user_items(db=Depends(get_db)):
    return get_user_items(db)