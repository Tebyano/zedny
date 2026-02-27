from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.schemas.user import UserCreate, UserResponse, UserLogin
from app.repositories.user_repository import UserRepository
from app.core.auth_utils import hash_password, verify_password, create_access_token

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]  # ✅ موحد
)


class AuthResponse(BaseModel):
    user: UserResponse
    access_token: str
    token_type: str = "bearer"


def get_user_by_email(db: Session, email: str):
    repo = UserRepository(db)
    return repo.get_by_email(email)


def get_user_by_username(db: Session, username: str):
    repo = UserRepository(db)
    return repo.get_by_username(username)


def create_user_in_db(db: Session, user_name: str, email: str, hashed_pwd: str):
    repo = UserRepository(db)
    return repo.create(user_name=user_name, email=email, hashed_password=hashed_pwd)


@router.post("/register", response_model=AuthResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):

    if get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pwd = hash_password(user.password)

    new_user = create_user_in_db(db, user.user_name, user.email, hashed_pwd)

    # ✅ FIXED (كان غلط قبل كده)
    token = create_access_token(data={"sub": str(new_user.id)})

    return {
        "user": new_user,
        "access_token": token,
        "token_type": "bearer"
    }


@router.post("/login", response_model=AuthResponse)
def login(credentials: UserLogin = Body(...), db: Session = Depends(get_db)):

    user = get_user_by_username(db, credentials.username)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    token = create_access_token(data={"sub": str(user.id)})

    return {
        "user": user,
        "access_token": token,
        "token_type": "bearer"
    }