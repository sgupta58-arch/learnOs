from functools import lru_cache
from typing import Literal

from pydantic import Field, PostgresDsn, RedisDsn, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    APP_ENV: Literal["development", "testing", "production"] = "development"
    APP_NAME: str = "LearnOS"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    DATABASE_URL: PostgresDsn
    TEST_DATABASE_URL: PostgresDsn | None = None

    REDIS_URL: RedisDsn

    JWT_SECRET_KEY: SecretStr
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    CORS_ORIGINS: list[str] = Field(default=["http://localhost:3000"])

    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            import json

            try:
                parsed = json.loads(value)
                if isinstance(parsed, list):
                    return parsed
            except json.JSONDecodeError:
                return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @property
    def is_development(self) -> bool:
        return self.APP_ENV == "development"

    @property
    def is_testing(self) -> bool:
        return self.APP_ENV == "testing"

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    @property
    def database_url_sync(self) -> str:
        """Return sync database URL for Alembic migrations."""
        url = str(self.DATABASE_URL)
        return url.replace("postgresql+asyncpg://", "postgresql://")

    @property
    def effective_database_url(self) -> str:
        """Return the appropriate database URL based on environment."""
        if self.is_testing and self.TEST_DATABASE_URL:
            return str(self.TEST_DATABASE_URL)
        return str(self.DATABASE_URL)


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
