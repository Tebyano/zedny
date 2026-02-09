from pydantic import BaseModel

class UserItemCreate(BaseModel):
    user_id: int
    item_id: int

class UserItemResponse(BaseModel):  # اختياري لو عايز response أفضل
    user_id: int
    item_id: int