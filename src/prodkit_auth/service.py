import hashlib
import hmac
import json
import secrets
import sqlite3
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, status

from prodkit_auth.security import hash_password, verify_password

AUTH_ACTION_TOKEN_BYTES = 32
AUTH_ACTION_TOKEN_PURPOSES = {"email_verification", "password_reset"}
AUTH_EVENT_TYPES = {
    "email_verification_request",
    "login_failed",
    "password_reset_request",
    "registration_attempt",
}
DEFAULT_AUTH_EVENT_HASH_PEPPER = "dev-only-event-hash-pepper"


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
        """
        SELECT id, email, password_hash, verified_at, token_version
        FROM users
        WHERE email = ?
        """,
        (email.lower(),),
    ).fetchone()


def get_user_by_id(connection: sqlite3.Connection, *, user_id: int) -> sqlite3.Row:
    user = connection.execute(
        """
        SELECT id, email, password_hash, verified_at, token_version
        FROM users
        WHERE id = ?
        """,
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
        "UPDATE users SET password_hash = ?, token_version = token_version + 1 WHERE id = ?",
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


def hash_rate_limit_key(value: str, *, pepper: str = DEFAULT_AUTH_EVENT_HASH_PEPPER) -> str:
    return hmac.new(
        pepper.encode("utf-8"),
        value.strip().lower().encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


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
    used_at = checked_at.isoformat()
    cursor = connection.execute(
        """
        UPDATE auth_action_tokens
        SET used_at = ?
        WHERE token_hash = ?
          AND purpose = ?
          AND used_at IS NULL
          AND expires_at > ?
        """,
        (used_at, token_hash, purpose, checked_at.isoformat()),
    )
    connection.commit()
    if cursor.rowcount != 1:
        return None

    return connection.execute(
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


def record_auth_event(
    connection: sqlite3.Connection,
    *,
    event_type: str,
    email: str | None = None,
    ip_address: str | None = None,
    occurred_at: datetime | None = None,
    event_hash_pepper: str = DEFAULT_AUTH_EVENT_HASH_PEPPER,
    metadata: dict[str, str] | None = None,
) -> sqlite3.Row:
    if event_type not in AUTH_EVENT_TYPES:
        raise ValueError(f"Unsupported auth event type: {event_type}")

    event_time = (occurred_at or datetime.now(UTC)).astimezone(UTC)
    cursor = connection.execute(
        """
        INSERT INTO auth_events (
            event_type,
            email_hash,
            ip_hash,
            occurred_at,
            metadata
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            event_type,
            hash_rate_limit_key(email, pepper=event_hash_pepper) if email else None,
            hash_rate_limit_key(ip_address, pepper=event_hash_pepper) if ip_address else None,
            event_time.isoformat(),
            json.dumps(metadata, sort_keys=True) if metadata else None,
        ),
    )
    connection.commit()
    return get_auth_event_by_id(connection, event_id=cursor.lastrowid)


def get_auth_event_by_id(connection: sqlite3.Connection, *, event_id: int) -> sqlite3.Row:
    event = connection.execute(
        """
        SELECT
            id,
            event_type,
            email_hash,
            ip_hash,
            occurred_at,
            metadata
        FROM auth_events
        WHERE id = ?
        """,
        (event_id,),
    ).fetchone()
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found.")
    return event


def count_auth_events(
    connection: sqlite3.Connection,
    *,
    event_type: str,
    since: datetime,
    email: str | None = None,
    ip_address: str | None = None,
    event_hash_pepper: str = DEFAULT_AUTH_EVENT_HASH_PEPPER,
) -> int:
    if event_type not in AUTH_EVENT_TYPES:
        raise ValueError(f"Unsupported auth event type: {event_type}")
    if email is None and ip_address is None:
        raise ValueError("email or ip_address is required for auth event counting.")

    filters = ["event_type = ?", "occurred_at >= ?"]
    values: list[str] = [event_type, since.astimezone(UTC).isoformat()]
    if email is not None:
        filters.append("email_hash = ?")
        values.append(hash_rate_limit_key(email, pepper=event_hash_pepper))
    if ip_address is not None:
        filters.append("ip_hash = ?")
        values.append(hash_rate_limit_key(ip_address, pepper=event_hash_pepper))

    row = connection.execute(
        f"SELECT COUNT(*) AS total FROM auth_events WHERE {' AND '.join(filters)}",
        tuple(values),
    ).fetchone()
    return int(row["total"])


def is_auth_event_rate_limited(
    connection: sqlite3.Connection,
    *,
    event_type: str,
    limit: int,
    window_seconds: int,
    email: str | None = None,
    ip_address: str | None = None,
    event_hash_pepper: str = DEFAULT_AUTH_EVENT_HASH_PEPPER,
    now: datetime | None = None,
) -> bool:
    checked_at = now or datetime.now(UTC)
    since = checked_at - timedelta(seconds=window_seconds)
    return (
        count_auth_events(
            connection,
            event_type=event_type,
            since=since,
            email=email,
            ip_address=ip_address,
            event_hash_pepper=event_hash_pepper,
        )
        >= limit
    )
