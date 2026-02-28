from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

if settings.use_supabase:
    DATABASE_URL = (
        f"postgresql://{settings.supa_db_user}:"
        f"{settings.supa_db_password}@"
        f"{settings.supa_db_host}:"
        f"{settings.supa_db_port}/"
        f"{settings.supa_db_name}"
    )
    engine = create_engine(DATABASE_URL, connect_args={"sslmode": "require"})
else:
    DATABASE_URL = (
        f"postgresql://{settings.local_db_user}:"
        f"{settings.local_db_password}@"
        f"{settings.local_db_host}:"
        f"{settings.local_db_port}/"
        f"{settings.local_db_name}"
    )
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()