from datetime import UTC, datetime, timedelta
from pathlib import Path

from prodkit_auth.database import database_session
from prodkit_auth.service import (
    consume_auth_action_token,
    create_auth_action_token,
    create_user,
    hash_auth_action_token,
)


def test_auth_action_token_stores_hash_not_raw_token(tmp_path: Path) -> None:
    with database_session(str(tmp_path / "auth.sqlite3")) as connection:
        user = create_user(
            connection,
            email="dev@example.com",
            password="correct horse battery staple",
        )
        raw_token, stored_token = create_auth_action_token(
            connection,
            user_id=user["id"],
            purpose="password_reset",
            expires_at=datetime.now(UTC) + timedelta(minutes=15),
            request_ip_hash="ip-hash",
            user_agent_hash="ua-hash",
        )

        assert raw_token not in stored_token["token_hash"]
        assert stored_token["token_hash"] == hash_auth_action_token(raw_token)
        assert stored_token["request_ip_hash"] == "ip-hash"
        assert stored_token["user_agent_hash"] == "ua-hash"


def test_auth_action_token_is_single_use(tmp_path: Path) -> None:
    with database_session(str(tmp_path / "auth.sqlite3")) as connection:
        user = create_user(
            connection,
            email="dev@example.com",
            password="correct horse battery staple",
        )
        raw_token, _ = create_auth_action_token(
            connection,
            user_id=user["id"],
            purpose="email_verification",
            expires_at=datetime.now(UTC) + timedelta(minutes=15),
        )

        consumed = consume_auth_action_token(
            connection,
            token=raw_token,
            purpose="email_verification",
        )
        assert consumed is not None
        assert consumed["used_at"] is not None

        reused = consume_auth_action_token(
            connection,
            token=raw_token,
            purpose="email_verification",
        )
        assert reused is None


def test_auth_action_token_rejects_wrong_purpose(tmp_path: Path) -> None:
    with database_session(str(tmp_path / "auth.sqlite3")) as connection:
        user = create_user(
            connection,
            email="dev@example.com",
            password="correct horse battery staple",
        )
        raw_token, _ = create_auth_action_token(
            connection,
            user_id=user["id"],
            purpose="password_reset",
            expires_at=datetime.now(UTC) + timedelta(minutes=15),
        )

        consumed = consume_auth_action_token(
            connection,
            token=raw_token,
            purpose="email_verification",
        )

        assert consumed is None


def test_auth_action_token_rejects_expired_token(tmp_path: Path) -> None:
    with database_session(str(tmp_path / "auth.sqlite3")) as connection:
        user = create_user(
            connection,
            email="dev@example.com",
            password="correct horse battery staple",
        )
        raw_token, _ = create_auth_action_token(
            connection,
            user_id=user["id"],
            purpose="password_reset",
            expires_at=datetime.now(UTC) - timedelta(minutes=1),
        )

        consumed = consume_auth_action_token(
            connection,
            token=raw_token,
            purpose="password_reset",
        )

        assert consumed is None
