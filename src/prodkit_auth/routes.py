import sqlite3
from collections.abc import Iterator

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from prodkit_auth.config import Settings, get_settings
from prodkit_auth.database import database_session
from prodkit_auth.schemas import (
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
    create_password_reset_token,
    decode_access_token,
    decode_password_reset_token,
)
from prodkit_auth.service import (
    authenticate_user,
    create_user,
    get_user_by_email,
    get_user_by_id,
    update_user_password,
)

router = APIRouter()
bearer_scheme = HTTPBearer(auto_error=False)


def get_database(settings: Settings = Depends(get_settings)) -> Iterator[sqlite3.Connection]:
    with database_session(settings.database_path) as connection:
        yield connection


@router.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    payload: RegisterRequest,
    connection: sqlite3.Connection = Depends(get_database),
) -> UserResponse:
    user = create_user(connection, email=str(payload.email), password=payload.password)
    return UserResponse(id=user["id"], email=user["email"])


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

    token = create_access_token(
        subject=str(user["id"]),
        secret_key=settings.secret_key,
        algorithm=settings.token_algorithm,
        expires_minutes=settings.access_token_minutes,
    )
    return TokenResponse(access_token=token)


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
    subject = decode_password_reset_token(
        token=payload.token,
        secret_key=settings.secret_key,
        algorithm=settings.token_algorithm,
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

    user = get_user_by_id(connection, user_id=int(subject))
    return UserResponse(id=user["id"], email=user["email"])


@router.get("/me", response_model=UserResponse)
def read_me(current_user: UserResponse = Depends(get_current_user)) -> UserResponse:
    return current_user
