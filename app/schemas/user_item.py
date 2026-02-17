from pydantic import BaseModel

class UserItemCreate(BaseModel):
    user_id: int
    item_id: int
    id: int

class UserItemResponse(BaseModel):  
    user_id: int
    item_id: int
    id: int