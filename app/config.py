from pydantic_settings import BaseSettings
from functools import lru_cache

# todo dotenv?
class Settings(BaseSettings):
    database_url: str = "sqlite:///./app.db"

    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # Worker
    worker_enabled: bool = True
    worker_poll_interval: int = 10
    worker_threads: int = 1

    # App
    app_name: str = "ML Backend"
    debug: bool = True
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
