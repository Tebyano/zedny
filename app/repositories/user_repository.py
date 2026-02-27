from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.user_model import User
from uuid import UUID

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, username: str, email: str, hashed_password: str):
        new_user = User(username=username, email=email, hashed_password=hashed_password)
        self.db.add(new_user)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise
        self.db.refresh(new_user)
        return new_user

    def get_by_id(self, user_id: UUID):
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str):
        return self.db.query(User).filter(User.email == email).first()

    def get_by_username(self, username: str):
        return self.db.query(User).filter(User.username == username).first()

    def get_all(self):
        return self.db.query(User).all()