from psycopg2.extras import RealDictCursor

def create_user(db, user_name: str, email: str) -> dict:
    cursor = db.cursor(cursor_factory=RealDictCursor)
    cursor.execute(
        "INSERT INTO users (user_name, email) VALUES (%s, %s) RETURNING id, user_name, email",
        (user_name, email)
    )
    db.commit()
    return cursor.fetchone()

def get_all_users(db) -> list:
    cursor = db.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT id, user_name, email FROM users")
    return cursor.fetchall()