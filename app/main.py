from fastapi import FastAPI
from app.routers import users, items, user_items

app = FastAPI(title="FastAPI + PostgreSQL CRUD - Users & Items")

app.include_router(users.router)
app.include_router(items.router)
app.include_router(user_items.router)