import sqlite3
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from prodkit_auth.config import Settings, get_settings
from prodkit_auth.database import database_session
from prodkit_auth.schemas import (
    EmailVerificationConfirmRequest,
    EmailVerificationRequest,
    EmailVerificationRequestResponse,
    LoginRequest,
    PasswordResetConfirmRequest,
    PasswordResetRequest,
    PasswordResetRequestResponse,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from prodkit_auth.security import (
    create_access_token,
    create_email_verification_token,
    create_password_reset_token,
    decode_access_token,
    decode_email_verification_token,
    decode_password_reset_token,
)
from prodkit_auth.service import (
    authenticate_user,
    consume_auth_action_token,
    create_auth_action_token,
    create_user,
    get_user_by_email,
    get_user_by_id,
    is_user_verified,
    mark_user_email_verified,
    update_user_password,
)

router = APIRouter()
bearer_scheme = HTTPBearer(auto_error=False)

EMAIL_VERIFICATION_PURPOSE = "email_verification"
PASSWORD_RESET_PURPOSE = "password_reset"


def get_database(settings: Settings = Depends(get_settings)) -> Iterator[sqlite3.Connection]:
    with database_session(settings.database_path) as connection:
        yield connection


def _expires_at(minutes: int) -> datetime:
    return datetime.now(UTC) + timedelta(minutes=minutes)


def _decode_action_token_subject(
    *,
    connection: sqlite3.Connection,
    settings: Settings,
    token: str,
    purpose: str,
) -> str | None:
    if settings.action_token_mode == "stateful":
        consumed_token = consume_auth_action_token(
            connection,
            token=token,
            purpose=purpose,
        )
        return str(consumed_token["user_id"]) if consumed_token is not None else None

    if purpose == EMAIL_VERIFICATION_PURPOSE:
        return decode_email_verification_token(
            token=token,
            secret_key=settings.secret_key,
            algorithm=settings.token_algorithm,
        )
    return decode_password_reset_token(
        token=token,
        secret_key=settings.secret_key,
        algorithm=settings.token_algorithm,
    )


@router.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    payload: RegisterRequest,
    settings: Settings = Depends(get_settings),
    connection: sqlite3.Connection = Depends(get_database),
) -> UserResponse:
    if settings.registration_enumeration_mode == "generic":
        normalized_email = str(payload.email).lower()
        try:
            create_user(connection, email=normalized_email, password=payload.password)
        except HTTPException as exc:
            if exc.status_code != status.HTTP_409_CONFLICT:
                raise
        return UserResponse(id=0, email=normalized_email, is_verified=False)

    user = create_user(connection, email=str(payload.email), password=payload.password)
    return UserResponse(id=user["id"], email=user["email"], is_verified=is_user_verified(user))


@router.post("/auth/login", response_model=TokenResponse)
def login(
    payload: LoginRequest,
    settings: Settings = Depends(get_settings),
    connection: sqlite3.Connection = Depends(get_database),
) -> TokenResponse:
    user = authenticate_user(connection, email=str(payload.email), password=payload.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )
    if settings.require_verified_email_for_login and not is_user_verified(user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email verification is required before login.",
        )

    token = create_access_token(
        subject=str(user["id"]),
        secret_key=settings.secret_key,
        algorithm=settings.token_algorithm,
        expires_minutes=settings.access_token_minutes,
    )
    return TokenResponse(access_token=token)


@router.post("/auth/email-verification/request", response_model=EmailVerificationRequestResponse)
def request_email_verification(
    payload: EmailVerificationRequest,
    settings: Settings = Depends(get_settings),
    connection: sqlite3.Connection = Depends(get_database),
) -> EmailVerificationRequestResponse:
    user = get_user_by_email(connection, email=str(payload.email))
    message = "If an account exists for this email, a verification link will be sent."
    if user is None or is_user_verified(user):
        return EmailVerificationRequestResponse(message=message)

    if settings.action_token_mode == "stateful":
        verification_token, _ = create_auth_action_token(
            connection,
            user_id=user["id"],
            purpose=EMAIL_VERIFICATION_PURPOSE,
            expires_at=_expires_at(settings.email_verification_token_minutes),
        )
    else:
        verification_token = create_email_verification_token(
            subject=str(user["id"]),
            secret_key=settings.secret_key,
            algorithm=settings.token_algorithm,
            expires_minutes=settings.email_verification_token_minutes,
        )
    return EmailVerificationRequestResponse(
        message=message,
        verification_token=(
            verification_token if settings.expose_email_verification_token else None
        ),
    )


@router.post("/auth/email-verification/confirm", response_model=UserResponse)
def confirm_email_verification(
    payload: EmailVerificationConfirmRequest,
    settings: Settings = Depends(get_settings),
    connection: sqlite3.Connection = Depends(get_database),
) -> UserResponse:
    subject = _decode_action_token_subject(
        connection=connection,
        settings=settings,
        token=payload.token,
        purpose=EMAIL_VERIFICATION_PURPOSE,
    )
    if subject is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired email verification token.",
        )

    try:
        user_id = int(subject)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired email verification token.",
        ) from exc

    user = mark_user_email_verified(connection, user_id=user_id)
    return UserResponse(id=user["id"], email=user["email"], is_verified=is_user_verified(user))


@router.post("/auth/password-reset/request", response_model=PasswordResetRequestResponse)
def request_password_reset(
    payload: PasswordResetRequest,
    settings: Settings = Depends(get_settings),
    connection: sqlite3.Connection = Depends(get_database),
) -> PasswordResetRequestResponse:
    user = get_user_by_email(connection, email=str(payload.email))
    message = "If an account exists for this email, a password reset link will be sent."
    if user is None:
        return PasswordResetRequestResponse(message=message)

    if settings.action_token_mode == "stateful":
        reset_token, _ = create_auth_action_token(
            connection,
            user_id=user["id"],
            purpose=PASSWORD_RESET_PURPOSE,
            expires_at=_expires_at(settings.password_reset_token_minutes),
        )
    else:
        reset_token = create_password_reset_token(
            subject=str(user["id"]),
            secret_key=settings.secret_key,
            algorithm=settings.token_algorithm,
            expires_minutes=settings.password_reset_token_minutes,
        )
    return PasswordResetRequestResponse(
        message=message,
        reset_token=reset_token if settings.expose_reset_token else None,
    )


@router.post("/auth/password-reset/confirm", status_code=status.HTTP_204_NO_CONTENT)
def confirm_password_reset(
    payload: PasswordResetConfirmRequest,
    settings: Settings = Depends(get_settings),
    connection: sqlite3.Connection = Depends(get_database),
) -> None:
    subject = _decode_action_token_subject(
        connection=connection,
        settings=settings,
        token=payload.token,
        purpose=PASSWORD_RESET_PURPOSE,
    )
    if subject is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired password reset token.",
        )

    try:
        user_id = int(subject)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired password reset token.",
        ) from exc

    update_user_password(connection, user_id=user_id, new_password=payload.new_password)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    settings: Settings = Depends(get_settings),
    connection: sqlite3.Connection = Depends(get_database),
) -> UserResponse:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token.")

    subject = decode_access_token(
        token=credentials.credentials,
        secret_key=settings.secret_key,
        algorithm=settings.token_algorithm,
    )
    if subject is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token.")

    try:
        user_id = int(subject)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token.",
        ) from exc

    user = get_user_by_id(connection, user_id=user_id)
    return UserResponse(id=user["id"], email=user["email"], is_verified=is_user_verified(user))


@router.get("/me", response_model=UserResponse)
def read_me(current_user: UserResponse = Depends(get_current_user)) -> UserResponse:
    return current_user
