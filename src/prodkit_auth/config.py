from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    environment: Literal["local", "staging", "production"] = Field(
        default="local",
        alias="AUTH_ENV",
    )
    database_path: str = Field(default="./prodkit-auth.sqlite3", alias="AUTH_DATABASE_PATH")
    database_url: str | None = Field(default=None, alias="AUTH_DATABASE_URL")
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
    registration_enumeration_mode: Literal["explicit", "generic"] = Field(
        default="explicit",
        alias="AUTH_REGISTRATION_ENUMERATION_MODE",
    )
    token_algorithm: str = "HS256"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()


def validate_production_settings(settings: Settings) -> None:
    if settings.environment != "production":
        return

    if settings.secret_key in {"dev-only-change-me", "change-me-before-production"}:
        raise RuntimeError("AUTH_SECRET_KEY must be changed in production.")

    if settings.expose_reset_token:
        raise RuntimeError("AUTH_EXPOSE_RESET_TOKEN must be false in production.")

    if settings.expose_email_verification_token:
        raise RuntimeError("AUTH_EXPOSE_EMAIL_VERIFICATION_TOKEN must be false in production.")
