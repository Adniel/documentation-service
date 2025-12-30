"""Application configuration using Pydantic Settings."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, PostgresDsn, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Environment
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = True

    # API
    api_prefix: str = "/api/v1"
    api_title: str = "Documentation Service API"
    api_version: str = "0.1.0"

    # Security
    secret_key: str = "dev_secret_key_change_in_production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # Database
    postgres_user: str = "docservice"
    postgres_password: str = "docservice_dev"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "docservice"

    @computed_field
    @property
    def database_url(self) -> str:
        """Construct async database URL."""
        return str(
            PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=self.postgres_user,
                password=self.postgres_password,
                host=self.postgres_host,
                port=self.postgres_port,
                path=self.postgres_db,
            )
        )

    @computed_field
    @property
    def sync_database_url(self) -> str:
        """Construct sync database URL for Alembic."""
        return str(
            PostgresDsn.build(
                scheme="postgresql",
                username=self.postgres_user,
                password=self.postgres_password,
                host=self.postgres_host,
                port=self.postgres_port,
                path=self.postgres_db,
            )
        )

    # Redis
    redis_url: str = "redis://localhost:6379"

    # Meilisearch
    meilisearch_url: str = "http://localhost:7700"
    meilisearch_api_key: str = "docservice_dev_key"

    # Git (local repository)
    git_repos_path: str = "/tmp/docservice/repos"

    # Git Remote Settings (Sprint 13)
    git_credential_encryption_key: str = ""  # Required for credential storage, base64-encoded 32-byte key
    git_sync_timeout_seconds: int = 120
    git_webhook_rate_limit: int = 10  # requests per minute per organization
    git_default_sync_strategy: str = "push_only"  # push_only, pull_only, bidirectional
    git_allowed_providers: str = "github,gitlab,gitea,custom"

    @computed_field
    @property
    def git_allowed_providers_list(self) -> list[str]:
        """Get allowed Git providers as a list."""
        return [p.strip() for p in self.git_allowed_providers.split(",") if p.strip()]

    # CORS - stored as comma-separated string, parsed via property
    cors_origins_str: str = Field(
        default="http://localhost:5173,http://localhost:3000",
        alias="cors_origins",
    )

    @computed_field
    @property
    def cors_origins_list(self) -> list[str]:
        """Get CORS origins as a list."""
        return [origin.strip() for origin in self.cors_origins_str.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
