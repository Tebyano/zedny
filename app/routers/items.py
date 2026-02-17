from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.item import ItemCreate, ItemResponse
from app.services.item_service import ItemService

router = APIRouter(
    prefix="/items",
    tags=["Items"]  # ✅ موحد
)


@router.post("/", response_model=ItemResponse)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    service = ItemService(db)
    new_item = service.create_new_item(item)
    return ItemResponse(
        item_id=new_item.item_id,
        item_name=new_item.item_name
    )


@router.get("/", response_model=List[ItemResponse])
def read_items(db: Session = Depends(get_db)):
    service = ItemService(db)
    items = service.get_items()
    return [
        ItemResponse(
            item_id=i.item_id,
            item_name=i.item_name
        )
        for i in items
    ]