from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "bola1 API"
    environment: str = "development"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/bola1"
    jwt_secret_key: str = "change-me-to-a-long-random-secret-key"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    backend_cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])

    # External football data provider (optional – enables /admin/matches/sync)
    # Compatible with football-data.org v4; adapt mapping for other providers.
    football_api_base_url: str = ""
    football_api_key: str = ""
    # Minimum seconds between consecutive sync calls (protects free-tier rate limits).
    football_api_sync_cooldown_seconds: int = 300

    # Public URL of the frontend (used to build absolute invite links)
    frontend_url: str = "http://localhost:3000"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("backend_cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
