from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_path: str = Field(default="./prodkit-auth.sqlite3", alias="AUTH_DATABASE_PATH")
    secret_key: str = Field(default="dev-only-change-me", alias="AUTH_SECRET_KEY")
    access_token_minutes: int = Field(default=30, alias="AUTH_ACCESS_TOKEN_MINUTES")
    password_reset_token_minutes: int = Field(
        default=15,
        alias="AUTH_PASSWORD_RESET_TOKEN_MINUTES",
    )
    expose_reset_token: bool = Field(default=True, alias="AUTH_EXPOSE_RESET_TOKEN")
    email_verification_token_minutes: int = Field(
        default=1440,
        alias="AUTH_EMAIL_VERIFICATION_TOKEN_MINUTES",
    )
    expose_email_verification_token: bool = Field(
        default=True,
        alias="AUTH_EXPOSE_EMAIL_VERIFICATION_TOKEN",
    )
    require_verified_email_for_login: bool = Field(
        default=False,
        alias="AUTH_REQUIRE_VERIFIED_EMAIL_FOR_LOGIN",
    )
    token_algorithm: str = "HS256"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
