from pathlib import Path

import pytest

from prodkit_auth.sqlalchemy_track import (
    auth_session,
    authenticate_user_record,
    create_auth_engine,
    create_session_factory,
    create_user_record,
    database_url_from_settings,
    get_user_record_by_email,
    initialize_auth_schema,
    mark_user_record_verified,
)


def make_session_factory(tmp_path: Path):
    database_url = f"sqlite+pysqlite:///{tmp_path / 'auth-sqlalchemy.sqlite3'}"
    engine = create_auth_engine(database_url)
    initialize_auth_schema(engine)
    return create_session_factory(engine)


def test_sqlalchemy_track_creates_and_authenticates_user(tmp_path: Path) -> None:
    session_factory = make_session_factory(tmp_path)

    with auth_session(session_factory) as session:
        user = create_user_record(
            session,
            email="Dev@Example.com",
            password="correct horse battery staple",
        )
        assert user.email == "dev@example.com"

    with auth_session(session_factory) as session:
        authenticated = authenticate_user_record(
            session,
            email="dev@example.com",
            password="correct horse battery staple",
        )
        assert authenticated is not None
        assert authenticated.email == "dev@example.com"
        assert authenticated.verified_at is None


def test_sqlalchemy_track_rejects_over_limit_login_password(tmp_path: Path) -> None:
    session_factory = make_session_factory(tmp_path)
    password = "x" * 72

    with auth_session(session_factory) as session:
        create_user_record(
            session,
            email="dev@example.com",
            password=password,
        )

    with auth_session(session_factory) as session:
        authenticated = authenticate_user_record(
            session,
            email="dev@example.com",
            password=f"{password}y",
        )
        assert authenticated is None


def test_sqlalchemy_track_rejects_duplicate_email(tmp_path: Path) -> None:
    session_factory = make_session_factory(tmp_path)

    with auth_session(session_factory) as session:
        create_user_record(
            session,
            email="dev@example.com",
            password="correct horse battery staple",
        )

    with pytest.raises(ValueError, match="already exists"):
        with auth_session(session_factory) as session:
            create_user_record(
                session,
                email="dev@example.com",
                password="correct horse battery staple",
            )


def test_sqlalchemy_track_marks_user_verified(tmp_path: Path) -> None:
    session_factory = make_session_factory(tmp_path)

    with auth_session(session_factory) as session:
        user = create_user_record(
            session,
            email="dev@example.com",
            password="correct horse battery staple",
        )
        user_id = user.id

    with auth_session(session_factory) as session:
        verified_user = mark_user_record_verified(session, user_id=user_id)
        assert verified_user.verified_at is not None

    with auth_session(session_factory) as session:
        user = get_user_record_by_email(session, email="dev@example.com")
        assert user is not None
        assert user.verified_at is not None


def test_database_url_from_settings_prefers_explicit_url() -> None:
    assert (
        database_url_from_settings(
            database_url="postgresql+psycopg://app:secret@db.example.com:5432/app",
            sqlite_path="./auth.sqlite3",
        )
        == "postgresql+psycopg://app:secret@db.example.com:5432/app"
    )
    assert (
        database_url_from_settings(database_url=None, sqlite_path="./auth.sqlite3")
        == "sqlite+pysqlite:///./auth.sqlite3"
    )
