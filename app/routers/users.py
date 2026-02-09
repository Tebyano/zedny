from fastapi import APIRouter, Depends
from typing import List
from app.database import get_db
from app.schemas.user import UserCreate, UserResponse
from app.services.user_service import create_new_user, get_users

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, db=Depends(get_db)):
    return create_new_user(db, user)

@router.get("/", response_model=List[UserResponse])
def read_users(db=Depends(get_db)):
    return get_users(db)