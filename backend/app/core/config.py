from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    auth_mode: str = "dev_stub"  # "dev_stub" now; Supabase Auth in Phase 11
    dev_user_id: str = "00000000-0000-0000-0000-000000000001"

    database_url: str

    supabase_url: str = ""
    supabase_service_key: str = ""
    supabase_storage_bucket: str = "resumes"

    redis_url: str = "redis://redis:6379/0"
    frontend_origin: str = "http://localhost:3000"

    # Resume upload limits
    max_upload_mb: int = 5
    max_resume_pages: int = 10
    max_resumes_per_user: int = 5
    extraction_min_chars: int = 200
    max_extracted_chars: int = 60000

    @field_validator("database_url")
    @classmethod
    def use_psycopg3_driver(cls, v: str) -> str:
        if v.startswith("postgres://"):
            v = "postgresql://" + v[len("postgres://"):]
        if v.startswith("postgresql://"):
            v = "postgresql+psycopg://" + v[len("postgresql://"):]
        return v


settings = Settings()