from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = Field(default="development", alias="APP_ENV")
    app_base_url: str = Field(default="http://localhost:3000", alias="APP_BASE_URL")
    public_app_name: str = Field(default="Tsubo", alias="PUBLIC_APP_NAME")

    database_url: str = Field(
        default="postgresql+asyncpg://tsubo:tsubo@localhost:5432/tsubo",
        alias="DATABASE_URL",
    )
    database_url_sync: str = Field(
        default="postgresql://tsubo:tsubo@localhost:5432/tsubo",
        alias="DATABASE_URL_SYNC",
    )

    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")

    opensearch_url: str = Field(default="http://localhost:9200", alias="OPENSEARCH_URL")
    opensearch_username: str | None = Field(default=None, alias="OPENSEARCH_USERNAME")
    opensearch_password: str | None = Field(default=None, alias="OPENSEARCH_PASSWORD")
    opensearch_index_listings: str = Field(
        default="canonical_listings",
        alias="OPENSEARCH_INDEX_LISTINGS",
    )

    auth_secret: str = Field(default="change-me-in-production-use-32-chars-min", alias="AUTH_SECRET")
    admin_bootstrap_email: str = Field(default="admin@tsubo.local", alias="ADMIN_BOOTSTRAP_EMAIL")

    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://127.0.0.1:3000"],
        alias="CORS_ORIGINS",
    )

    fx_fawaz_primary_url: str = Field(
        default="https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies",
        alias="FX_FAWAZ_PRIMARY_URL",
    )
    fx_fawaz_fallback_url: str = Field(
        default="https://latest.currency-api.pages.dev/v1/currencies",
        alias="FX_FAWAZ_FALLBACK_URL",
    )
    fx_frankfurter_url: str = Field(
        default="https://api.frankfurter.dev",
        alias="FX_FRANKFURTER_URL",
    )
    fx_cache_ttl_seconds: int = Field(default=3600, alias="FX_CACHE_TTL_SECONDS")

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"


@lru_cache
def get_settings() -> Settings:
    return Settings()
