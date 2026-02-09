from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import sql, Error as PGError

# =========================

# =========================
SUPERUSER_CONFIG = {
    "host": "localhost",
    "dbname": "postgres",
    "user": "admin",
    "password": "12345",
    "port": 5432
}

DB_NAME = "inventory_db"

# =========================
# 
# =========================
def create_database():
    conn = psycopg2.connect(**SUPERUSER_CONFIG)
    conn.autocommit = True
    cursor = conn.cursor()
    cursor.execute(
        sql.SQL("SELECT 1 FROM pg_database WHERE datname = %s"), [DB_NAME]
    )
    exists = cursor.fetchone()
    if not exists:
        cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_NAME)))
        print(f"Database '{DB_NAME}' created.")
    cursor.close()
    conn.close()

create_database()

# =========================

# =========================
DATABASE_CONFIG = {
    "host": "localhost",
    "dbname": "mydb",   # 
    "user": "admin",
    "password": "12345",
    "port": 5432
}

app = FastAPI(title="FastAPI + PostgreSQL CRUD - Products")

# =========================
# DB CONNECTION
# =========================
def get_db():
    conn = psycopg2.connect(**DATABASE_CONFIG)
    try:
        yield conn
    finally:
        conn.close()

# ======================
# =========================
def create_table():
    conn = psycopg2.connect(**DATABASE_CONFIG)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            product_name VARCHAR(200) NOT NULL,
            quantity INT DEFAULT 0
        );
        """
    )
    conn.commit()
    cursor.close()
    conn.close()

create_table()

# =========================
# Pydantic Schemas
# =========================
class ProductCreate(BaseModel):
    product_name: str
    quantity: Optional[int] = 0

class ProductResponse(ProductCreate):
    id: int

# =========================
# CRUD Endpoints
# =========================

# CREATE
@app.post("/products", response_model=ProductResponse)
def create_product(product: ProductCreate, db=Depends(get_db)):
    cursor = db.cursor(cursor_factory=RealDictCursor)
    cursor.execute(
        """
        INSERT INTO products (product_name, quantity)
        VALUES (%s, %s)
        RETURNING id, product_name, quantity
        """,
        (product.product_name, product.quantity)
    )
    db.commit()
    return cursor.fetchone()

# READ ALL
@app.get("/products", response_model=List[ProductResponse])
def read_products(db=Depends(get_db)):
    cursor = db.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM products")
    return cursor.fetchall()

# READ ONE
@app.get("/products/{product_id}", response_model=ProductResponse)
def read_product(product_id: int, db=Depends(get_db)):
    cursor = db.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
    product = cursor.fetchone()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

# UPDATE
@app.put("/products/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, product: ProductCreate, db=Depends(get_db)):
    cursor = db.cursor(cursor_factory=RealDictCursor)
    cursor.execute(
        """
        UPDATE products
        SET product_name = %s, quantity = %s
        WHERE id = %s
        RETURNING id, product_name, quantity
        """,
        (product.product_name, product.quantity, product_id)
    )
    updated = cursor.fetchone()
    if not updated:
        raise HTTPException(status_code=404, detail="Product not found")
    db.commit()
    return updated

# DELETE
@app.delete("/products/{product_id}")
def delete_product(product_id: int, db=Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("DELETE FROM products WHERE id = %s RETURNING id", (product_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Product not found")
    db.commit()
    return {"message": "Product deleted"}