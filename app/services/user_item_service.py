from sqlalchemy.orm import Session
from app.repositories.user_item_repository import UserItemRepository
from app.schemas.user_item import UserItemCreate

class UserItemService:
    def __init__(self, db: Session):
        self.repo = UserItemRepository(db)

    def assign_item(self, assignment: UserItemCreate):
        return self.repo.assign_item_to_user(
            assignment.user_id,
            assignment.item_id
        )

    def get_user_items(self):
        return self.repo.get_all_user_items()