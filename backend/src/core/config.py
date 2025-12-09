from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Search Monitor"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/ai_search_monitor"
    
    # Ingestion
    OPENAI_API_KEY: str | None = None
    OPENAI_OPP_MODEL: str = "gpt-4o-mini"
    ENABLE_LINKEDIN: bool = False

    # Ingestion Concurrency
    INGEST_MAX_DETAIL_CONCURRENCY_SEO: int = 5
    INGEST_MAX_DETAIL_CONCURRENCY_LINKEDIN: int = 3
    INGEST_MAX_UPSERT_CONCURRENCY: int = 8
    OPENAI_OPP_MAX_CONCURRENCY: int = 3
    OPENAI_OPP_MAX_RETRIES: int = 4
    
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

@lru_cache
def get_settings():
    return Settings()

settings = get_settings()
