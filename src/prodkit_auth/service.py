import sqlite3
from datetime import UTC, datetime

from fastapi import HTTPException, status

from prodkit_auth.security import hash_password, verify_password


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
