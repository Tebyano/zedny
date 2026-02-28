from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel

from app.database import get_db
from app.schemas.user import UserCreate, UserResponse, UserLogin
from app.repositories.user_repository import UserRepository
from app.core.auth_utils import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,  
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


class AuthResponse(BaseModel):
    user: UserResponse
    access_token: str
    token_type: str = "bearer"


def get_user_by_email(db: Session, email: str):
    return UserRepository(db).get_by_email(email)


def get_user_by_username(db: Session, username: str):
    return UserRepository(db).get_by_username(username)


@router.post("/register", response_model=AuthResponse, status_code=201)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # يدعم UserCreate سواء فيها username أو user_name
    username = getattr(user, "username", None) or getattr(user, "user_name", None)
    if not username:
        raise HTTPException(status_code=400, detail="Username is required")

    if get_user_by_email(db, user.email):
        raise HTTPException(status_code=409, detail="Email already registered")
    if get_user_by_username(db, username):
        raise HTTPException(status_code=409, detail="Username already registered")

    hashed_pwd = hash_password(user.password)

    try:
        new_user = UserRepository(db).create_user(
            username=username,
            email=user.email,
            hashed_password=hashed_pwd,
        )
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email or username already exists")

    token = create_access_token(data={"sub": str(new_user.id)})

    return {"user": new_user, "access_token": token, "token_type": "bearer"}


@router.post("/login", response_model=AuthResponse)
def login(credentials: UserLogin = Body(...), db: Session = Depends(get_db)):
    user = get_user_by_username(db, credentials.username)

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(data={"sub": str(user.id)})

    return {"user": user, "access_token": token, "token_type": "bearer"}


# @router.get("/me")
# def me(current_user=Depends(get_current_user)):
#     return {
#         "id": current_user.id,
#         "username": current_user.username,
#         "email": current_user.email,
#     }