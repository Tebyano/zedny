from pydantic import BaseModel, EmailStr, Field, field_validator
from uuid import UUID

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str 

    @field_validator('password')
    @classmethod
    def validate_password_length(cls, v):
        if len(v.encode('utf-8')) > 72:
            raise ValueError('password is too long')
        return v


class UserResponse(BaseModel):
    id: UUID
    username: str
    email: EmailStr

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    username: str
    password: str
    email: EmailStr
