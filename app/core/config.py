from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator


class Settings(BaseSettings):
    use_supabase: bool = True

    local_db_host: str
    local_db_name: str
    local_db_user: str
    local_db_password: str
    local_db_port: int

    supa_db_host: str
    supa_db_name: str
    supa_db_user: str
    supa_db_password: str
    supa_db_port: int

    cohere_api_key: str
    cohere_model: str = "command-r-08-2024"

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("use_supabase", mode="before")
    @classmethod
    def parse_bool(cls, v):
        if isinstance(v, str):
            return v.lower() in ("1", "true", "yes")
        return bool(v)
    supabase_url: str
    supabase_anon_key: str
    supabase_service_role_key: str
    supabase_storage_bucket: str = "chat-files"


settings = Settings()