from app.repositories.user_repository import create_user, get_all_users
from app.schemas.user import UserCreate, UserResponse

def create_new_user(db, user: UserCreate) -> UserResponse:
    return UserResponse(**create_user(db, user.user_name, user.email))

def get_users(db) -> list[UserResponse]:
    return [UserResponse(**u) for u in get_all_users(db)]