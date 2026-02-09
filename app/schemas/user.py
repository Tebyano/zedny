from pydantic import BaseModel

class UserCreate(BaseModel):
    user_name: str
    email: str

class UserResponse(UserCreate):
    id: int