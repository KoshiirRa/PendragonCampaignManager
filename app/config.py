from functools import lru_cache
from typing import Literal

from pydantic import SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:54322/postgres"
    app_env: Literal["development", "test", "migration", "production"] = "development"
    api_prefix: str = "/api/v1"
    api_key: SecretStr | None = None
    cors_origins: str = ""
    public_base_url: str = "http://localhost:8000"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @model_validator(mode="after")
    def require_production_secrets(self) -> "Settings":
        if self.app_env == "production":
            if self.api_key is None:
                raise ValueError("API_KEY is required when APP_ENV=production")
            if len(self.api_key.get_secret_value()) < 32:
                raise ValueError("API_KEY must contain at least 32 characters in production")
            if make_url(self.database_url).host in {"localhost", "127.0.0.1", "::1"}:
                raise ValueError("A non-local DATABASE_URL is required when APP_ENV=production")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
