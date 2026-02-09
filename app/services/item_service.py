from app.repositories.item_repository import create_item, get_all_items
from app.schemas.item import ItemCreate, ItemResponse

def create_new_item(db, item: ItemCreate) -> ItemResponse:
    return ItemResponse(**create_item(db, item.item_name))

def get_items(db) -> list[ItemResponse]:
    return [ItemResponse(**i) for i in get_all_items(db)]