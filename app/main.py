from fastapi import FastAPI
from app.routers import users, items, user_items, auth, llm

app = FastAPI(title="FFirst API", version="0.1.0")

# تسجيل الراوترات
app.include_router(users.router, prefix="/api")
app.include_router(items.router, prefix="/api")
app.include_router(user_items.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(llm.router)  # هنا اللجوء لراوتر LLM