def assign_item_to_user(db, user_id: int, item_id: int) -> dict:
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO user_item (user_id, item_id) VALUES (%s, %s) RETURNING user_id, item_id",
        (user_id, item_id)
    )
    db.commit()
    row = cursor.fetchone()
    return {"user_id": row[0], "item_id": row[1]}

def get_all_user_items(db) -> list:
    cursor = db.cursor(cursor_factory=RealDictCursor)
    cursor.execute("""
        SELECT ui.user_id, u.user_name, ui.item_id, i.item_name
        FROM user_item ui
        JOIN users u ON ui.user_id = u.id
        JOIN items i ON ui.item_id = i.item_id
    """)
    return cursor.fetchall()