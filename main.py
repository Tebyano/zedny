from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import sql

# =========================

# =========================
DATABASE_CONFIG = {
    "host": "localhost",
    "dbname": "mydatabase",
    "user": "tebyan",
    "password": "secret123",
    "port": 5432
}

app = FastAPI(title="FastAPI + PostgreSQL CRUD - Users & Items")

# =========================

# =========================
def get_db():
    conn = psycopg2.connect(**DATABASE_CONFIG)
    try:
        yield conn
    finally:
        conn.close()

# =========================

# =========================
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

create_tables()

# =========================
# Pydantic Schemas
# =========================
class UserCreate(BaseModel):
    user_name: str
    email: str

class UserResponse(UserCreate):
    id: int

class ItemCreate(BaseModel):
    item_name: str

class ItemResponse(ItemCreate):
    item_id: int

class UserItemCreate(BaseModel):
    user_id: int
    item_id: int

# =========================
# CRUD Endpoints
# =========================

# USERS
@app.post("/users", response_model=UserResponse)
def create_user(user: UserCreate, db=Depends(get_db)):
    cursor = db.cursor(cursor_factory=RealDictCursor)
    cursor.execute(
        "INSERT INTO users (user_name, email) VALUES (%s, %s) RETURNING id, user_name, email",
        (user.user_name, user.email)
    )
    db.commit()
    return cursor.fetchone()

@app.get("/users", response_model=List[UserResponse])
def read_users(db=Depends(get_db)):
    cursor = db.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()

# ITEMS
@app.post("/items", response_model=ItemResponse)
def create_item(item: ItemCreate, db=Depends(get_db)):
    cursor = db.cursor(cursor_factory=RealDictCursor)
    cursor.execute(
        "INSERT INTO items (item_name) VALUES (%s) RETURNING item_id, item_name",
        (item.item_name,)
    )
    db.commit()
    return cursor.fetchone()

@app.get("/items", response_model=List[ItemResponse])
def read_items(db=Depends(get_db)):
    cursor = db.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM items")
    return cursor.fetchall()

# USER_ITEM
@app.post("/user_item")
def assign_item(user_item: UserItemCreate, db=Depends(get_db)):
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO user_item (user_id, item_id) VALUES (%s, %s) RETURNING user_id, item_id",
        (user_item.user_id, user_item.item_id)
    )
    db.commit()
    return {"user_id": user_item.user_id, "item_id": user_item.item_id}

@app.get("/user_item")
def get_user_items(db=Depends(get_db)):
    cursor = db.cursor(cursor_factory=RealDictCursor)
    cursor.execute("""
        SELECT ui.user_id, u.user_name, ui.item_id, i.item_name
        FROM user_item ui
        JOIN users u ON ui.user_id = u.id
        JOIN items i ON ui.item_id = i.item_id
    """)
    return cursor.fetchall()