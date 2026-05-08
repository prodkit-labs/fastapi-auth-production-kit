from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
argon2id_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return password_context.verify(password, password_hash)


def hash_password_argon2id(password: str) -> str:
    return argon2id_context.hash(password)


def verify_password_argon2id(password: str, password_hash: str) -> bool:
    return argon2id_context.verify(password, password_hash)


def verify_password_any(password: str, password_hash: str) -> bool:
    if password_hash.startswith("$argon2"):
        return verify_password_argon2id(password, password_hash)
    return verify_password(password, password_hash)


def create_access_token(
    *,
    subject: str,
    secret_key: str,
    algorithm: str,
    expires_minutes: int,
) -> str:
    expires_at = datetime.now(UTC) + timedelta(minutes=expires_minutes)
    payload: dict[str, Any] = {"sub": subject, "exp": expires_at}
    return jwt.encode(payload, secret_key, algorithm=algorithm)


def create_password_reset_token(
    *,
    subject: str,
    secret_key: str,
    algorithm: str,
    expires_minutes: int,
) -> str:
    expires_at = datetime.now(UTC) + timedelta(minutes=expires_minutes)
    payload: dict[str, Any] = {"sub": subject, "purpose": "password_reset", "exp": expires_at}
    return jwt.encode(payload, secret_key, algorithm=algorithm)


def create_email_verification_token(
    *,
    subject: str,
    secret_key: str,
    algorithm: str,
    expires_minutes: int,
) -> str:
    expires_at = datetime.now(UTC) + timedelta(minutes=expires_minutes)
    payload: dict[str, Any] = {
        "sub": subject,
        "purpose": "email_verification",
        "exp": expires_at,
    }
    return jwt.encode(payload, secret_key, algorithm=algorithm)


def decode_access_token(*, token: str, secret_key: str, algorithm: str) -> str | None:
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
    except JWTError:
        return None
    subject = payload.get("sub")
    return subject if isinstance(subject, str) else None


def decode_password_reset_token(*, token: str, secret_key: str, algorithm: str) -> str | None:
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
    except JWTError:
        return None
    if payload.get("purpose") != "password_reset":
        return None
    subject = payload.get("sub")
    return subject if isinstance(subject, str) else None


def decode_email_verification_token(*, token: str, secret_key: str, algorithm: str) -> str | None:
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
    except JWTError:
        return None
    if payload.get("purpose") != "email_verification":
        return None
    subject = payload.get("sub")
    return subject if isinstance(subject, str) else None
