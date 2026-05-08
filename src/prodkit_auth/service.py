import sqlite3

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
        "SELECT id, email, password_hash FROM users WHERE email = ?",
        (email.lower(),),
    ).fetchone()


def get_user_by_id(connection: sqlite3.Connection, *, user_id: int) -> sqlite3.Row:
    user = connection.execute(
        "SELECT id, email, password_hash FROM users WHERE id = ?",
        (user_id,),
    ).fetchone()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    return user
