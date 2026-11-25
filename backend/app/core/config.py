from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    auth_mode: str = "dev_stub"          # "dev_stub" now; real auth in Phase 11
    dev_user_id: str = "00000000-0000-0000-0000-000000000001"

    database_url: str
    redis_url: str = "redis://redis:6379/0"
    frontend_origin: str = "http://localhost:3000"


settings = Settings()