from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return password_context.verify(password, password_hash)


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


def decode_access_token(*, token: str, secret_key: str, algorithm: str) -> str | None:
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
    except JWTError:
        return None
    subject = payload.get("sub")
    return subject if isinstance(subject, str) else None
