# app/models/__init__.py
from app.database import Base
from app.models.user_model import User
from app.models.item_model import Item
from app.models.user_item_model import UserItem

__all__ = ["Base", "User", "Item", "UserItem"]