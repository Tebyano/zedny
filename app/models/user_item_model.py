from sqlalchemy import Column, Integer, ForeignKey, Table
from app.database import Base

# لو UserItem جدول many-to-many
UserItem = Table(
    'user_items',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('item_id', Integer, ForeignKey('items.id'), primary_key=True),
    extend_existing=True
)
