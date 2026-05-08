from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_path: str = Field(default="./prodkit-auth.sqlite3", alias="AUTH_DATABASE_PATH")
    secret_key: str = Field(default="dev-only-change-me", alias="AUTH_SECRET_KEY")
    access_token_minutes: int = Field(default=30, alias="AUTH_ACCESS_TOKEN_MINUTES")
    token_algorithm: str = "HS256"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
