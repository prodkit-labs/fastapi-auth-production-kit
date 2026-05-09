from pathlib import Path

from fastapi.testclient import TestClient

from prodkit_auth.config import Settings, get_settings, validate_production_settings
from prodkit_auth.main import create_app
from prodkit_auth.security import create_access_token


def make_client(
    tmp_path: Path,
    *,
    email_verification_token_minutes: int = 1440,
    password_reset_token_minutes: int = 15,
    require_verified_email_for_login: bool = False,
    local_rate_limits: bool = False,
    event_hash_pepper: str = "test-event-hash-pepper-value-32-chars",
    action_token_mode: str = "jwt",
    registration_enumeration_mode: str = "explicit",
) -> TestClient:
    app = create_app()

    def settings_override() -> Settings:
        return Settings(
            AUTH_DATABASE_PATH=str(tmp_path / "auth.sqlite3"),
            AUTH_SECRET_KEY="test-secret",
            AUTH_ACCESS_TOKEN_MINUTES=15,
            AUTH_PASSWORD_RESET_TOKEN_MINUTES=password_reset_token_minutes,
            AUTH_EXPOSE_RESET_TOKEN=True,
            AUTH_EMAIL_VERIFICATION_TOKEN_MINUTES=email_verification_token_minutes,
            AUTH_EXPOSE_EMAIL_VERIFICATION_TOKEN=True,
            AUTH_REQUIRE_VERIFIED_EMAIL_FOR_LOGIN=require_verified_email_for_login,
            AUTH_LOCAL_RATE_LIMITS=local_rate_limits,
            AUTH_EVENT_HASH_PEPPER=event_hash_pepper,
            AUTH_ACTION_TOKEN_MODE=action_token_mode,
            AUTH_REGISTRATION_ENUMERATION_MODE=registration_enumeration_mode,
        )

    app.dependency_overrides[get_settings] = settings_override
    return TestClient(app)


def test_register_login_and_read_current_user(tmp_path: Path) -> None:
    client = make_client(tmp_path)
    credentials = {"email": "Dev@Example.com", "password": "correct horse battery staple"}

    register_response = client.post("/auth/register", json=credentials)
    assert register_response.status_code == 201
    assert register_response.json()["email"] == "dev@example.com"
    assert register_response.json()["is_verified"] is False

    login_response = client.post("/auth/login", json=credentials)
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    me_response = client.get("/me", headers={"authorization": f"Bearer {token}"})
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "dev@example.com"


def test_duplicate_email_returns_conflict(tmp_path: Path) -> None:
    client = make_client(tmp_path)
    credentials = {"email": "dev@example.com", "password": "correct horse battery staple"}

    assert client.post("/auth/register", json=credentials).status_code == 201
    response = client.post("/auth/register", json=credentials)

    assert response.status_code == 409


def test_local_rate_limits_throttle_registration_attempts(tmp_path: Path) -> None:
    client = make_client(tmp_path, local_rate_limits=True)
    credentials = {"email": "dev@example.com", "password": "correct horse battery staple"}

    assert client.post("/auth/register", json=credentials).status_code == 201
    assert client.post("/auth/register", json=credentials).status_code == 409
    assert client.post("/auth/register", json=credentials).status_code == 409

    throttled_response = client.post("/auth/register", json=credentials)

    assert throttled_response.status_code == 429


def test_generic_registration_mode_normalizes_duplicate_email_response(
    tmp_path: Path,
) -> None:
    client = make_client(tmp_path, registration_enumeration_mode="generic")
    credentials = {"email": "Dev@Example.com", "password": "correct horse battery staple"}

    first_response = client.post("/auth/register", json=credentials)
    second_response = client.post("/auth/register", json=credentials)

    assert first_response.status_code == 201
    assert second_response.status_code == 201
    assert first_response.json() == {
        "id": 0,
        "email": "dev@example.com",
        "is_verified": False,
    }
    assert second_response.json() == first_response.json()

    login_response = client.post("/auth/login", json=credentials)
    assert login_response.status_code == 200


def test_register_rejects_password_over_bcrypt_byte_limit(tmp_path: Path) -> None:
    client = make_client(tmp_path)

    response = client.post(
        "/auth/register",
        json={"email": "dev@example.com", "password": "x" * 73},
    )

    assert response.status_code == 422


def test_login_rejects_bad_password(tmp_path: Path) -> None:
    client = make_client(tmp_path)
    client.post(
        "/auth/register",
        json={"email": "dev@example.com", "password": "correct horse battery staple"},
    )

    response = client.post(
        "/auth/login",
        json={"email": "dev@example.com", "password": "wrong-password"},
    )

    assert response.status_code == 401


def test_login_rejects_password_over_bcrypt_byte_limit(tmp_path: Path) -> None:
    client = make_client(tmp_path)
    password = "x" * 72
    client.post(
        "/auth/register",
        json={"email": "dev@example.com", "password": password},
    )

    response = client.post(
        "/auth/login",
        json={"email": "dev@example.com", "password": f"{password}y"},
    )

    assert response.status_code == 422


def test_local_rate_limits_throttle_failed_login_attempts(tmp_path: Path) -> None:
    client = make_client(tmp_path, local_rate_limits=True)
    client.post(
        "/auth/register",
        json={"email": "dev@example.com", "password": "correct horse battery staple"},
    )

    for _ in range(5):
        response = client.post(
            "/auth/login",
            json={"email": "dev@example.com", "password": "wrong-password"},
        )
        assert response.status_code == 401

    throttled_response = client.post(
        "/auth/login",
        json={"email": "dev@example.com", "password": "wrong-password"},
    )

    assert throttled_response.status_code == 429


def test_local_rate_limits_are_disabled_by_default(tmp_path: Path) -> None:
    client = make_client(tmp_path)
    client.post(
        "/auth/register",
        json={"email": "dev@example.com", "password": "correct horse battery staple"},
    )

    for _ in range(6):
        response = client.post(
            "/auth/login",
            json={"email": "dev@example.com", "password": "wrong-password"},
        )
        assert response.status_code == 401


def test_email_verification_marks_user_verified(tmp_path: Path) -> None:
    client = make_client(tmp_path)
    credentials = {"email": "dev@example.com", "password": "correct horse battery staple"}
    client.post("/auth/register", json=credentials)

    request_response = client.post(
        "/auth/email-verification/request",
        json={"email": credentials["email"]},
    )
    assert request_response.status_code == 200
    verification_token = request_response.json()["verification_token"]
    assert verification_token

    confirm_response = client.post(
        "/auth/email-verification/confirm",
        json={"token": verification_token},
    )
    assert confirm_response.status_code == 200
    assert confirm_response.json()["is_verified"] is True

    login_response = client.post("/auth/login", json=credentials)
    token = login_response.json()["access_token"]
    me_response = client.get("/me", headers={"authorization": f"Bearer {token}"})
    assert me_response.json()["is_verified"] is True


def test_verified_email_can_be_required_for_login(tmp_path: Path) -> None:
    client = make_client(tmp_path, require_verified_email_for_login=True)
    credentials = {"email": "dev@example.com", "password": "correct horse battery staple"}
    client.post("/auth/register", json=credentials)

    unverified_login = client.post("/auth/login", json=credentials)
    assert unverified_login.status_code == 403

    request_response = client.post(
        "/auth/email-verification/request",
        json={"email": credentials["email"]},
    )
    client.post(
        "/auth/email-verification/confirm",
        json={"token": request_response.json()["verification_token"]},
    )

    verified_login = client.post("/auth/login", json=credentials)
    assert verified_login.status_code == 200


def test_email_verification_request_does_not_error_for_unknown_or_verified_email(
    tmp_path: Path,
) -> None:
    client = make_client(tmp_path)

    missing_response = client.post(
        "/auth/email-verification/request",
        json={"email": "missing@example.com"},
    )
    assert missing_response.status_code == 200
    assert missing_response.json()["verification_token"] is None

    credentials = {"email": "dev@example.com", "password": "correct horse battery staple"}
    client.post("/auth/register", json=credentials)
    request_response = client.post(
        "/auth/email-verification/request",
        json={"email": credentials["email"]},
    )
    client.post(
        "/auth/email-verification/confirm",
        json={"token": request_response.json()["verification_token"]},
    )

    verified_response = client.post(
        "/auth/email-verification/request",
        json={"email": credentials["email"]},
    )
    assert verified_response.status_code == 200
    assert verified_response.json()["verification_token"] is None


def test_local_rate_limits_throttle_email_verification_requests(tmp_path: Path) -> None:
    client = make_client(tmp_path, local_rate_limits=True)
    credentials = {"email": "dev@example.com", "password": "correct horse battery staple"}
    client.post("/auth/register", json=credentials)

    first_response = client.post(
        "/auth/email-verification/request",
        json={"email": credentials["email"]},
    )
    second_response = client.post(
        "/auth/email-verification/request",
        json={"email": credentials["email"]},
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 429


def test_email_verification_rejects_invalid_and_wrong_purpose_tokens(tmp_path: Path) -> None:
    client = make_client(tmp_path)
    credentials = {"email": "dev@example.com", "password": "correct horse battery staple"}
    client.post("/auth/register", json=credentials)
    login_response = client.post("/auth/login", json=credentials)

    invalid_response = client.post(
        "/auth/email-verification/confirm",
        json={"token": "not-a-valid-token"},
    )
    assert invalid_response.status_code == 401

    access_token_response = client.post(
        "/auth/email-verification/confirm",
        json={"token": login_response.json()["access_token"]},
    )
    assert access_token_response.status_code == 401


def test_email_verification_rejects_expired_token(tmp_path: Path) -> None:
    client = make_client(tmp_path, email_verification_token_minutes=-1)
    credentials = {"email": "dev@example.com", "password": "correct horse battery staple"}
    client.post("/auth/register", json=credentials)
    request_response = client.post(
        "/auth/email-verification/request",
        json={"email": credentials["email"]},
    )

    response = client.post(
        "/auth/email-verification/confirm",
        json={"token": request_response.json()["verification_token"]},
    )

    assert response.status_code == 401


def test_stateful_email_verification_token_is_single_use(tmp_path: Path) -> None:
    client = make_client(tmp_path, action_token_mode="stateful")
    credentials = {"email": "dev@example.com", "password": "correct horse battery staple"}
    client.post("/auth/register", json=credentials)
    request_response = client.post(
        "/auth/email-verification/request",
        json={"email": credentials["email"]},
    )
    verification_token = request_response.json()["verification_token"]

    first_response = client.post(
        "/auth/email-verification/confirm",
        json={"token": verification_token},
    )
    second_response = client.post(
        "/auth/email-verification/confirm",
        json={"token": verification_token},
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 401


def test_stateful_email_verification_rejects_expired_token(tmp_path: Path) -> None:
    client = make_client(
        tmp_path,
        action_token_mode="stateful",
        email_verification_token_minutes=-1,
    )
    credentials = {"email": "dev@example.com", "password": "correct horse battery staple"}
    client.post("/auth/register", json=credentials)
    request_response = client.post(
        "/auth/email-verification/request",
        json={"email": credentials["email"]},
    )

    response = client.post(
        "/auth/email-verification/confirm",
        json={"token": request_response.json()["verification_token"]},
    )

    assert response.status_code == 401


def test_protected_route_requires_token(tmp_path: Path) -> None:
    client = make_client(tmp_path)

    response = client.get("/me")

    assert response.status_code == 401


def test_protected_route_rejects_signed_token_with_non_integer_subject(
    tmp_path: Path,
) -> None:
    client = make_client(tmp_path)
    token = create_access_token(
        subject="not-an-int",
        secret_key="test-secret",
        algorithm="HS256",
        expires_minutes=15,
    )

    response = client.get("/me", headers={"authorization": f"Bearer {token}"})

    assert response.status_code == 401


def test_password_reset_changes_password(tmp_path: Path) -> None:
    client = make_client(tmp_path)
    credentials = {"email": "dev@example.com", "password": "correct horse battery staple"}
    new_password = "new correct horse battery staple"
    client.post("/auth/register", json=credentials)
    before_reset_login = client.post("/auth/login", json=credentials)
    before_reset_token = before_reset_login.json()["access_token"]

    request_response = client.post(
        "/auth/password-reset/request",
        json={"email": credentials["email"]},
    )
    assert request_response.status_code == 200
    reset_token = request_response.json()["reset_token"]
    assert reset_token

    confirm_response = client.post(
        "/auth/password-reset/confirm",
        json={"token": reset_token, "new_password": new_password},
    )
    assert confirm_response.status_code == 204

    old_login = client.post("/auth/login", json=credentials)
    assert old_login.status_code == 401

    new_login = client.post(
        "/auth/login",
        json={"email": credentials["email"], "password": new_password},
    )
    assert new_login.status_code == 200
    new_token = new_login.json()["access_token"]

    old_me_response = client.get("/me", headers={"authorization": f"Bearer {before_reset_token}"})
    new_me_response = client.get("/me", headers={"authorization": f"Bearer {new_token}"})

    assert old_me_response.status_code == 401
    assert new_me_response.status_code == 200


def test_password_reset_request_does_not_error_for_unknown_email(tmp_path: Path) -> None:
    client = make_client(tmp_path)

    response = client.post(
        "/auth/password-reset/request",
        json={"email": "missing@example.com"},
    )

    assert response.status_code == 200
    assert response.json()["reset_token"] is None


def test_local_rate_limits_throttle_password_reset_requests(tmp_path: Path) -> None:
    client = make_client(tmp_path, local_rate_limits=True)
    credentials = {"email": "dev@example.com", "password": "correct horse battery staple"}
    client.post("/auth/register", json=credentials)

    first_response = client.post(
        "/auth/password-reset/request",
        json={"email": credentials["email"]},
    )
    second_response = client.post(
        "/auth/password-reset/request",
        json={"email": credentials["email"]},
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 429


def test_password_reset_rejects_invalid_token(tmp_path: Path) -> None:
    client = make_client(tmp_path)

    response = client.post(
        "/auth/password-reset/confirm",
        json={"token": "not-a-valid-token", "new_password": "new correct horse battery staple"},
    )

    assert response.status_code == 401


def test_password_reset_rejects_new_password_over_bcrypt_byte_limit(tmp_path: Path) -> None:
    client = make_client(tmp_path)
    credentials = {"email": "dev@example.com", "password": "correct horse battery staple"}
    client.post("/auth/register", json=credentials)
    request_response = client.post(
        "/auth/password-reset/request",
        json={"email": credentials["email"]},
    )

    response = client.post(
        "/auth/password-reset/confirm",
        json={"token": request_response.json()["reset_token"], "new_password": "x" * 73},
    )

    assert response.status_code == 422


def test_password_reset_rejects_expired_token(tmp_path: Path) -> None:
    client = make_client(tmp_path, password_reset_token_minutes=-1)
    credentials = {"email": "dev@example.com", "password": "correct horse battery staple"}
    client.post("/auth/register", json=credentials)
    request_response = client.post(
        "/auth/password-reset/request",
        json={"email": credentials["email"]},
    )

    response = client.post(
        "/auth/password-reset/confirm",
        json={
            "token": request_response.json()["reset_token"],
            "new_password": "new correct horse battery staple",
        },
    )

    assert response.status_code == 401


def test_stateful_password_reset_token_is_single_use(tmp_path: Path) -> None:
    client = make_client(tmp_path, action_token_mode="stateful")
    credentials = {"email": "dev@example.com", "password": "correct horse battery staple"}
    client.post("/auth/register", json=credentials)
    request_response = client.post(
        "/auth/password-reset/request",
        json={"email": credentials["email"]},
    )
    reset_token = request_response.json()["reset_token"]

    first_response = client.post(
        "/auth/password-reset/confirm",
        json={"token": reset_token, "new_password": "new correct horse battery staple"},
    )
    second_response = client.post(
        "/auth/password-reset/confirm",
        json={"token": reset_token, "new_password": "another correct horse battery staple"},
    )

    assert first_response.status_code == 204
    assert second_response.status_code == 401


def test_stateful_password_reset_rejects_expired_token(tmp_path: Path) -> None:
    client = make_client(
        tmp_path,
        action_token_mode="stateful",
        password_reset_token_minutes=-1,
    )
    credentials = {"email": "dev@example.com", "password": "correct horse battery staple"}
    client.post("/auth/register", json=credentials)
    request_response = client.post(
        "/auth/password-reset/request",
        json={"email": credentials["email"]},
    )

    response = client.post(
        "/auth/password-reset/confirm",
        json={
            "token": request_response.json()["reset_token"],
            "new_password": "new correct horse battery staple",
        },
    )

    assert response.status_code == 401


def test_production_settings_reject_unsafe_defaults() -> None:
    unsafe_settings = Settings(
        AUTH_ENV="production",
        AUTH_SECRET_KEY="dev-only-change-me",
        AUTH_EXPOSE_RESET_TOKEN=True,
        AUTH_EXPOSE_EMAIL_VERIFICATION_TOKEN=True,
    )

    try:
        validate_production_settings(unsafe_settings)
    except RuntimeError as exc:
        assert "AUTH_SECRET_KEY" in str(exc)
    else:
        raise AssertionError("Expected production settings to reject default secret.")


def test_production_settings_accept_safe_values() -> None:
    settings = Settings(
        AUTH_ENV="production",
        AUTH_SECRET_KEY="a-long-random-secret-value-for-production",
        AUTH_EXPOSE_RESET_TOKEN=False,
        AUTH_EXPOSE_EMAIL_VERIFICATION_TOKEN=False,
        AUTH_ALLOW_SQLITE_IN_PRODUCTION=True,
    )

    validate_production_settings(settings)


def test_production_settings_reject_short_secret() -> None:
    settings = Settings(
        AUTH_ENV="production",
        AUTH_SECRET_KEY="short-secret",
        AUTH_EXPOSE_RESET_TOKEN=False,
        AUTH_EXPOSE_EMAIL_VERIFICATION_TOKEN=False,
        AUTH_ALLOW_SQLITE_IN_PRODUCTION=True,
    )

    try:
        validate_production_settings(settings)
    except RuntimeError as exc:
        assert "at least 32 characters" in str(exc)
    else:
        raise AssertionError("Expected production settings to reject short secret.")


def test_production_settings_reject_non_positive_token_ttls() -> None:
    settings = Settings(
        AUTH_ENV="production",
        AUTH_SECRET_KEY="a-long-random-secret-value-for-production",
        AUTH_ACCESS_TOKEN_MINUTES=0,
        AUTH_EXPOSE_RESET_TOKEN=False,
        AUTH_EXPOSE_EMAIL_VERIFICATION_TOKEN=False,
        AUTH_ALLOW_SQLITE_IN_PRODUCTION=True,
    )

    try:
        validate_production_settings(settings)
    except RuntimeError as exc:
        assert "AUTH_ACCESS_TOKEN_MINUTES" in str(exc)
    else:
        raise AssertionError("Expected production settings to reject non-positive TTL.")


def test_production_settings_reject_non_positive_password_reset_ttl() -> None:
    settings = Settings(
        AUTH_ENV="production",
        AUTH_SECRET_KEY="a-long-random-secret-value-for-production",
        AUTH_PASSWORD_RESET_TOKEN_MINUTES=0,
        AUTH_EXPOSE_RESET_TOKEN=False,
        AUTH_EXPOSE_EMAIL_VERIFICATION_TOKEN=False,
        AUTH_ALLOW_SQLITE_IN_PRODUCTION=True,
    )

    try:
        validate_production_settings(settings)
    except RuntimeError as exc:
        assert "AUTH_PASSWORD_RESET_TOKEN_MINUTES" in str(exc)
    else:
        raise AssertionError("Expected production settings to reject non-positive reset TTL.")


def test_production_settings_reject_non_positive_email_verification_ttl() -> None:
    settings = Settings(
        AUTH_ENV="production",
        AUTH_SECRET_KEY="a-long-random-secret-value-for-production",
        AUTH_EMAIL_VERIFICATION_TOKEN_MINUTES=0,
        AUTH_EXPOSE_RESET_TOKEN=False,
        AUTH_EXPOSE_EMAIL_VERIFICATION_TOKEN=False,
        AUTH_ALLOW_SQLITE_IN_PRODUCTION=True,
    )

    try:
        validate_production_settings(settings)
    except RuntimeError as exc:
        assert "AUTH_EMAIL_VERIFICATION_TOKEN_MINUTES" in str(exc)
    else:
        raise AssertionError(
            "Expected production settings to reject non-positive verification TTL."
        )


def test_production_settings_require_explicit_sqlite_decision() -> None:
    settings = Settings(
        AUTH_ENV="production",
        AUTH_SECRET_KEY="a-long-random-secret-value-for-production",
        AUTH_EXPOSE_RESET_TOKEN=False,
        AUTH_EXPOSE_EMAIL_VERIFICATION_TOKEN=False,
    )

    try:
        validate_production_settings(settings)
    except RuntimeError as exc:
        assert "AUTH_ALLOW_SQLITE_IN_PRODUCTION" in str(exc)
    else:
        raise AssertionError("Expected production settings to require SQLite decision.")


def test_production_settings_require_event_hash_pepper_for_local_rate_limits() -> None:
    settings = Settings(
        AUTH_ENV="production",
        AUTH_SECRET_KEY="a-long-random-secret-value-for-production",
        AUTH_EXPOSE_RESET_TOKEN=False,
        AUTH_EXPOSE_EMAIL_VERIFICATION_TOKEN=False,
        AUTH_ALLOW_SQLITE_IN_PRODUCTION=True,
        AUTH_LOCAL_RATE_LIMITS=True,
        AUTH_EVENT_HASH_PEPPER="dev-only-event-hash-pepper",
    )

    try:
        validate_production_settings(settings)
    except RuntimeError as exc:
        assert "AUTH_EVENT_HASH_PEPPER" in str(exc)
    else:
        raise AssertionError("Expected production settings to reject default event pepper.")


def test_production_settings_accept_event_hash_pepper_for_local_rate_limits() -> None:
    settings = Settings(
        AUTH_ENV="production",
        AUTH_SECRET_KEY="a-long-random-secret-value-for-production",
        AUTH_EXPOSE_RESET_TOKEN=False,
        AUTH_EXPOSE_EMAIL_VERIFICATION_TOKEN=False,
        AUTH_ALLOW_SQLITE_IN_PRODUCTION=True,
        AUTH_LOCAL_RATE_LIMITS=True,
        AUTH_EVENT_HASH_PEPPER="a-long-random-event-hash-pepper-value",
    )

    validate_production_settings(settings)


def test_settings_accept_field_names() -> None:
    settings = Settings(
        environment="production",
        secret_key="a-long-random-secret-value-for-production",
        expose_reset_token=False,
        expose_email_verification_token=False,
        allow_sqlite_in_production=True,
    )

    assert settings.environment == "production"
    validate_production_settings(settings)
