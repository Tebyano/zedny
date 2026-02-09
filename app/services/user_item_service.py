from app.repositories.user_item_repository import assign_item_to_user, get_all_user_items
from app.schemas.user_item import UserItemCreate, UserItemResponse

def assign_item(db, assignment: UserItemCreate) -> dict:
    return assign_item_to_user(db, assignment.user_id, assignment.item_id)

def get_user_items(db) -> list:
    # ممكن تعمل mapping أفضل لو عايز response model معقد
    return get_all_user_items(db)