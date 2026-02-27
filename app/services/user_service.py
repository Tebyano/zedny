from sqlalchemy.orm import Session
from app.schemas.user import UserCreate
from app.repositories.user_repository import UserRepository
from app.core.auth_utils import hash_password


class UserService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def create_new_user(self, user: UserCreate):
        hashed_pwd = hash_password(user.password)
        return self.repo.create_user(
            username=user.username,
            email=user.email,
            hashed_password=hashed_pwd
        )

    def get_user(self, user_id: int):
        return self.repo.get_by_id(user_id)

    def get_user_by_email(self, email: str):
        return self.repo.get_by_email(email)

    def get_all_users(self):
        return self.repo.get_all()