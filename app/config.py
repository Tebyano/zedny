from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    db_host: str = "localhost"
    db_name: str = "mydatabase"
    db_user: str = "tebyan"
    db_password: str = "secret123"
    db_port: int = 5432

    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)

settings = Settings()

DATABASE_CONFIG = {
    "host": settings.db_host,
    "dbname": settings.db_name,
    "user": settings.db_user,
    "password": settings.db_password,
    "port": settings.db_port,
}