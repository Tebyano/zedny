from sqlalchemy.orm import Session
from app.repositories.item_repository import ItemRepository
from app.schemas.item import ItemCreate

class ItemService:
    def __init__(self, db: Session):
        self.repo = ItemRepository(db)

    def create_new_item(self, item: ItemCreate):
        return self.repo.create_item(item.item_name)

    def get_items(self):
        return self.repo.get_all_items()