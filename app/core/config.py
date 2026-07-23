from functools import lru_cache
from pathlib import Path

from pydantic import Field, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = Field(alias="APP_NAME")
    app_env: str = Field(alias="APP_ENV")
    app_debug: bool = Field(alias="APP_DEBUG")

    postgres_db: str = Field(alias="POSTGRES_DB")
    postgres_user: str = Field(alias="POSTGRES_USER")
    postgres_password: str = Field(alias="POSTGRES_PASSWORD")
    postgres_host: str = Field(alias="POSTGRES_HOST")
    postgres_port: int = Field(alias="POSTGRES_PORT")

    redis_url: RedisDsn = Field(alias="REDIS_URL")

    source_api_url: str = Field(alias="SOURCE_API_URL")
    source_api_candidate_id: str = Field(
        alias="SOURCE_API_CANDIDATE_ID"
    )
    source_api_timeout_seconds: float = Field(
        alias="SOURCE_API_TIMEOUT_SECONDS"
    )

    storage_root: Path = Field(alias="STORAGE_ROOT")

    novosibirsk_timezone: str = Field(
        alias="NOVOSIBIRSK_TIMEZONE"
    )

    @property
    def database_url(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=self.postgres_user,
            password=self.postgres_password,
            host=self.postgres_host,
            port=self.postgres_port,
            path=self.postgres_db,
        )

    @property
    def absolute_storage_root(self) -> Path:
        if self.storage_root.is_absolute():
            return self.storage_root

        return BASE_DIR / self.storage_root


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()