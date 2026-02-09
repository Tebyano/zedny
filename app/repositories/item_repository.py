from psycopg2.extras import RealDictCursor

def create_item(db, item_name: str) -> dict:
    cursor = db.cursor(cursor_factory=RealDictCursor)
    cursor.execute(
        "INSERT INTO items (item_name) VALUES (%s) RETURNING item_id, item_name",
        (item_name,)
    )
    db.commit()
    return cursor.fetchone()

def get_all_items(db) -> list:
    cursor = db.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT item_id, item_name FROM items")
    return cursor.fetchall()