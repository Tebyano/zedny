from sqlalchemy.orm import Session
from app.models.item_model import Item

class ItemRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_item(self, item_name: str) -> Item:
        new_item = Item(item_name=item_name)
        self.db.add(new_item)
        self.db.commit()
        self.db.refresh(new_item)
        return new_item

    def get_all_items(self) -> list[Item]:
        return self.db.query(Item).all()