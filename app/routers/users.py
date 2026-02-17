from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import UserCreate, UserResponse
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db)):
    service = UserService(db)
    return service.get_all_users()


@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    service = UserService(db)
    return service.create_new_user(user)
