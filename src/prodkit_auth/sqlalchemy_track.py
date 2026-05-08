from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime

from sqlalchemy import DateTime, String, create_engine, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from prodkit_auth.security import hash_password, verify_password


class AuthBase(DeclarativeBase):
    pass


class UserModel(AuthBase):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )


def database_url_from_settings(*, database_url: str | None, sqlite_path: str) -> str:
    if database_url:
        return database_url
    return f"sqlite+pysqlite:///{sqlite_path}"


def create_auth_engine(database_url: str):
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    return create_engine(database_url, connect_args=connect_args)


def create_session_factory(engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def initialize_auth_schema(engine) -> None:
    AuthBase.metadata.create_all(bind=engine)


@contextmanager
def auth_session(session_factory: sessionmaker[Session]) -> Iterator[Session]:
    session = session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def create_user_record(session: Session, *, email: str, password: str) -> UserModel:
    user = UserModel(email=email.lower(), password_hash=hash_password(password))
    session.add(user)
    try:
        session.flush()
    except IntegrityError as exc:
        raise ValueError("A user with this email already exists.") from exc
    return user


def get_user_record_by_email(session: Session, *, email: str) -> UserModel | None:
    return session.scalar(select(UserModel).where(UserModel.email == email.lower()))


def get_user_record_by_id(session: Session, *, user_id: int) -> UserModel | None:
    return session.get(UserModel, user_id)


def authenticate_user_record(
    session: Session,
    *,
    email: str,
    password: str,
) -> UserModel | None:
    user = get_user_record_by_email(session, email=email)
    if user is None:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def mark_user_record_verified(session: Session, *, user_id: int) -> UserModel:
    user = get_user_record_by_id(session, user_id=user_id)
    if user is None:
        raise ValueError("User not found.")
    user.verified_at = datetime.now(UTC)
    session.flush()
    return user
