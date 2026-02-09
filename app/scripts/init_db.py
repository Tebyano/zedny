import psycopg2
from app.config import DATABASE_CONFIG

def create_tables():
    conn = psycopg2.connect(**DATABASE_CONFIG)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            user_name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS items (
            item_id SERIAL PRIMARY KEY,
            item_name VARCHAR(255) NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_item (
            id SERIAL PRIMARY KEY,
            user_id INT NOT NULL,
            item_id INT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (item_id) REFERENCES items(item_id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("All tables created successfully!")

if __name__ == "__main__":
    create_tables()