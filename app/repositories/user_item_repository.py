from sqlalchemy.orm import Session
from app.models.user_model import User
from app.models.item_model import Item
from app.models.user_item_model import UserItem

class UserItemRepository:
    def __init__(self, db: Session):
        self.db = db

    def assign_item_to_user(self, user_id: int, item_id: int) -> UserItem:
        assignment = UserItem(user_id=user_id, item_id=item_id)
        self.db.add(assignment)
        self.db.commit()
        self.db.refresh(assignment)
        return assignment

    def get_all_user_items(self):
        return self.db.query(UserItem).all()