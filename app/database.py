import psycopg2
from psycopg2.extras import RealDictCursor
from app.config import DATABASE_CONFIG

def get_db():
    conn = psycopg2.connect(**DATABASE_CONFIG)
    try:
        yield conn
    finally:
        conn.close()