from pydantic import BaseModel

class ItemCreate(BaseModel):
    item_name: str

class ItemResponse(ItemCreate):
    item_id: int