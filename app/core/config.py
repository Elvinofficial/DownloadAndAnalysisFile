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

    source_api_base_url: str = Field(alias="SOURCE_API_BASE_URL")
    source_api_candidate_id: str = Field(alias="SOURCE_API_CANDIDATE_ID")

    download_storage_path: Path = Field(alias="DOWNLOAD_STORAGE_PATH")
    novosibirsk_timezone: str = Field(alias="NOVOSIBIRSK_TIMEZONE")

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
    def absolute_download_storage_path(self) -> Path:
        path = self.download_storage_path

        if path.is_absolute():
            return path

        return BASE_DIR / path


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
