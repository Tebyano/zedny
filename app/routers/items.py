from fastapi import APIRouter, Depends
from typing import List
from app.database import get_db
from app.schemas.item import ItemCreate, ItemResponse
from app.services.item_service import create_new_item, get_items

router = APIRouter(prefix="/items", tags=["items"])

@router.post("/", response_model=ItemResponse)
def create_item(item: ItemCreate, db=Depends(get_db)):
    return create_new_item(db, item)

@router.get("/", response_model=List[ItemResponse])
def read_items(db=Depends(get_db)):
    return get_items(db)