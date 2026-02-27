from fastapi import FastAPI
from dotenv import load_dotenv
from pathlib import Path

from app.routers import users, items, user_items, auth, llm
from app.database import Base, engine

# ✅ register tables so create_all can see them
import app.models.user_model
import app.models.chat_model
import app.models.embedding_model
import app.models.video_model  # ✅ NEW

load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / ".env")

app = FastAPI(title="FFirst API", version="0.1.0")

app.include_router(users.router, prefix="/api")
app.include_router(items.router, prefix="/api")
app.include_router(user_items.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(llm.router)

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)