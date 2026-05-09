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


def test_password_reset_request_does_not_error_for_unknown_email(tmp_path: Path) -> None:
    client = make_client(tmp_path)

    response = client.post(
        "/auth/password-reset/request",
        json={"email": "missing@example.com"},
    )

    assert response.status_code == 200
    assert response.json()["reset_token"] is None


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
    )

    validate_production_settings(settings)


def test_settings_accept_field_names() -> None:
    settings = Settings(
        environment="production",
        secret_key="a-long-random-secret-value-for-production",
        expose_reset_token=False,
        expose_email_verification_token=False,
    )

    assert settings.environment == "production"
    validate_production_settings(settings)
