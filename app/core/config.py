from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator

class Settings(BaseSettings):
    use_supabase: bool = False

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

    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True
    )

    @field_validator("use_supabase", mode="before")
    @classmethod
    def parse_use_supabase(cls, v):
        if isinstance(v, str):
            return v in ('1', 'true', 'True', 'TRUE')
        return bool(v)

settings = Settings()
