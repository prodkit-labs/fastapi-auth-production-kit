import hashlib
import secrets
import sqlite3
from datetime import UTC, datetime

from fastapi import HTTPException, status

from prodkit_auth.security import hash_password, verify_password

AUTH_ACTION_TOKEN_BYTES = 32
AUTH_ACTION_TOKEN_PURPOSES = {"email_verification", "password_reset"}


def create_user(connection: sqlite3.Connection, *, email: str, password: str) -> sqlite3.Row:
    try:
        cursor = connection.execute(
            "INSERT INTO users (email, password_hash) VALUES (?, ?)",
            (email.lower(), hash_password(password)),
        )
        connection.commit()
    except sqlite3.IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists.",
        ) from exc

    return get_user_by_id(connection, user_id=cursor.lastrowid)


def authenticate_user(
    connection: sqlite3.Connection, *, email: str, password: str
) -> sqlite3.Row | None:
    user = get_user_by_email(connection, email=email)
    if user is None:
        return None
    if not verify_password(password, user["password_hash"]):
        return None
    return user


def get_user_by_email(connection: sqlite3.Connection, *, email: str) -> sqlite3.Row | None:
    return connection.execute(
        "SELECT id, email, password_hash, verified_at FROM users WHERE email = ?",
        (email.lower(),),
    ).fetchone()


def get_user_by_id(connection: sqlite3.Connection, *, user_id: int) -> sqlite3.Row:
    user = connection.execute(
        "SELECT id, email, password_hash, verified_at FROM users WHERE id = ?",
        (user_id,),
    ).fetchone()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    return user


def update_user_password(
    connection: sqlite3.Connection,
    *,
    user_id: int,
    new_password: str,
) -> None:
    cursor = connection.execute(
        "UPDATE users SET password_hash = ? WHERE id = ?",
        (hash_password(new_password), user_id),
    )
    connection.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")


def mark_user_email_verified(connection: sqlite3.Connection, *, user_id: int) -> sqlite3.Row:
    verified_at = datetime.now(UTC).isoformat()
    cursor = connection.execute(
        "UPDATE users SET verified_at = ? WHERE id = ?",
        (verified_at, user_id),
    )
    connection.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    return get_user_by_id(connection, user_id=user_id)


def is_user_verified(user: sqlite3.Row) -> bool:
    return user["verified_at"] is not None


def hash_auth_action_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_auth_action_token(
    connection: sqlite3.Connection,
    *,
    user_id: int,
    purpose: str,
    expires_at: datetime,
    request_ip_hash: str | None = None,
    user_agent_hash: str | None = None,
) -> tuple[str, sqlite3.Row]:
    if purpose not in AUTH_ACTION_TOKEN_PURPOSES:
        raise ValueError(f"Unsupported auth action token purpose: {purpose}")

    token = secrets.token_urlsafe(AUTH_ACTION_TOKEN_BYTES)
    token_hash = hash_auth_action_token(token)
    cursor = connection.execute(
        """
        INSERT INTO auth_action_tokens (
            user_id,
            token_hash,
            purpose,
            expires_at,
            request_ip_hash,
            user_agent_hash
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            token_hash,
            purpose,
            expires_at.astimezone(UTC).isoformat(),
            request_ip_hash,
            user_agent_hash,
        ),
    )
    connection.commit()
    return token, get_auth_action_token_by_id(connection, token_id=cursor.lastrowid)


def get_auth_action_token_by_id(
    connection: sqlite3.Connection,
    *,
    token_id: int,
) -> sqlite3.Row:
    token = connection.execute(
        """
        SELECT
            id,
            user_id,
            token_hash,
            purpose,
            expires_at,
            used_at,
            created_at,
            request_ip_hash,
            user_agent_hash
        FROM auth_action_tokens
        WHERE id = ?
        """,
        (token_id,),
    ).fetchone()
    if token is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Token not found.")
    return token


def consume_auth_action_token(
    connection: sqlite3.Connection,
    *,
    token: str,
    purpose: str,
    now: datetime | None = None,
) -> sqlite3.Row | None:
    if purpose not in AUTH_ACTION_TOKEN_PURPOSES:
        raise ValueError(f"Unsupported auth action token purpose: {purpose}")

    checked_at = (now or datetime.now(UTC)).astimezone(UTC)
    token_hash = hash_auth_action_token(token)
    row = connection.execute(
        """
        SELECT
            id,
            user_id,
            token_hash,
            purpose,
            expires_at,
            used_at,
            created_at,
            request_ip_hash,
            user_agent_hash
        FROM auth_action_tokens
        WHERE token_hash = ? AND purpose = ?
        """,
        (token_hash, purpose),
    ).fetchone()
    if row is None or row["used_at"] is not None:
        return None

    expires_at = datetime.fromisoformat(row["expires_at"])
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=UTC)
    if expires_at <= checked_at:
        return None

    used_at = checked_at.isoformat()
    connection.execute(
        "UPDATE auth_action_tokens SET used_at = ? WHERE id = ?",
        (used_at, row["id"]),
    )
    connection.commit()
    return get_auth_action_token_by_id(connection, token_id=row["id"])
