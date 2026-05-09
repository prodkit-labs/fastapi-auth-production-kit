from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from prodkit_auth.database import database_session
from prodkit_auth.service import (
    count_auth_events,
    hash_rate_limit_key,
    is_auth_event_rate_limited,
    record_auth_event,
)


def test_auth_event_store_hashes_email_and_ip(tmp_path: Path) -> None:
    with database_session(str(tmp_path / "auth.sqlite3")) as connection:
        event = record_auth_event(
            connection,
            event_type="login_failed",
            email="Dev@Example.com",
            ip_address="203.0.113.10",
            metadata={"reason": "bad_password"},
        )

        assert event["email_hash"] == hash_rate_limit_key("dev@example.com")
        assert event["ip_hash"] == hash_rate_limit_key("203.0.113.10")
        assert "Dev@Example.com" not in event["email_hash"]
        assert "203.0.113.10" not in event["ip_hash"]


def test_failed_login_rate_limit_by_email(tmp_path: Path) -> None:
    now = datetime.now(UTC)
    with database_session(str(tmp_path / "auth.sqlite3")) as connection:
        for offset in (50, 30, 10):
            record_auth_event(
                connection,
                event_type="login_failed",
                email="dev@example.com",
                occurred_at=now - timedelta(seconds=offset),
            )

        assert (
            count_auth_events(
                connection,
                event_type="login_failed",
                email="dev@example.com",
                since=now - timedelta(seconds=60),
            )
            == 3
        )
        assert is_auth_event_rate_limited(
            connection,
            event_type="login_failed",
            email="dev@example.com",
            limit=3,
            window_seconds=60,
            now=now,
        )


def test_password_reset_request_cooldown_by_ip(tmp_path: Path) -> None:
    now = datetime.now(UTC)
    with database_session(str(tmp_path / "auth.sqlite3")) as connection:
        record_auth_event(
            connection,
            event_type="password_reset_request",
            ip_address="203.0.113.10",
            occurred_at=now - timedelta(seconds=20),
        )

        assert is_auth_event_rate_limited(
            connection,
            event_type="password_reset_request",
            ip_address="203.0.113.10",
            limit=1,
            window_seconds=60,
            now=now,
        )
        assert not is_auth_event_rate_limited(
            connection,
            event_type="password_reset_request",
            ip_address="203.0.113.11",
            limit=1,
            window_seconds=60,
            now=now,
        )


def test_email_verification_resend_window_expires(tmp_path: Path) -> None:
    now = datetime.now(UTC)
    with database_session(str(tmp_path / "auth.sqlite3")) as connection:
        record_auth_event(
            connection,
            event_type="email_verification_request",
            email="dev@example.com",
            occurred_at=now - timedelta(seconds=120),
        )

        assert not is_auth_event_rate_limited(
            connection,
            event_type="email_verification_request",
            email="dev@example.com",
            limit=1,
            window_seconds=60,
            now=now,
        )


def test_auth_event_count_requires_email_or_ip(tmp_path: Path) -> None:
    with database_session(str(tmp_path / "auth.sqlite3")) as connection:
        with pytest.raises(ValueError, match="email or ip_address"):
            count_auth_events(
                connection,
                event_type="login_failed",
                since=datetime.now(UTC) - timedelta(seconds=60),
            )
