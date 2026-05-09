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
    allow_sqlite_in_production: bool = Field(
        default=False,
        alias="AUTH_ALLOW_SQLITE_IN_PRODUCTION",
    )
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
    local_rate_limits: bool = Field(default=False, alias="AUTH_LOCAL_RATE_LIMITS")
    action_token_mode: Literal["jwt", "stateful"] = Field(
        default="jwt",
        alias="AUTH_ACTION_TOKEN_MODE",
    )
    registration_enumeration_mode: Literal["explicit", "generic"] = Field(
        default="explicit",
        alias="AUTH_REGISTRATION_ENUMERATION_MODE",
    )
    token_algorithm: str = "HS256"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", populate_by_name=True)


@lru_cache
def get_settings() -> Settings:
    return Settings()


def validate_production_settings(settings: Settings) -> None:
    if settings.environment != "production":
        return

    if settings.secret_key in {"dev-only-change-me", "change-me-before-production"}:
        raise RuntimeError("AUTH_SECRET_KEY must be changed in production.")

    if len(settings.secret_key) < 32:
        raise RuntimeError("AUTH_SECRET_KEY must be at least 32 characters in production.")

    if settings.access_token_minutes <= 0:
        raise RuntimeError("AUTH_ACCESS_TOKEN_MINUTES must be positive in production.")

    if settings.password_reset_token_minutes <= 0:
        raise RuntimeError("AUTH_PASSWORD_RESET_TOKEN_MINUTES must be positive in production.")

    if settings.email_verification_token_minutes <= 0:
        raise RuntimeError("AUTH_EMAIL_VERIFICATION_TOKEN_MINUTES must be positive in production.")

    if settings.expose_reset_token:
        raise RuntimeError("AUTH_EXPOSE_RESET_TOKEN must be false in production.")

    if settings.expose_email_verification_token:
        raise RuntimeError("AUTH_EXPOSE_EMAIL_VERIFICATION_TOKEN must be false in production.")

    if not settings.allow_sqlite_in_production:
        raise RuntimeError(
            "AUTH_ALLOW_SQLITE_IN_PRODUCTION must be true when the default SQLite routes "
            "run in production."
        )
