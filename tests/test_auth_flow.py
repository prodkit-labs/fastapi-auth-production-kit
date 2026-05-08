from pathlib import Path

from fastapi.testclient import TestClient

from prodkit_auth.config import Settings, get_settings
from prodkit_auth.main import create_app


def make_client(tmp_path: Path) -> TestClient:
    app = create_app()

    def settings_override() -> Settings:
        return Settings(
            AUTH_DATABASE_PATH=str(tmp_path / "auth.sqlite3"),
            AUTH_SECRET_KEY="test-secret",
            AUTH_ACCESS_TOKEN_MINUTES=15,
        )

    app.dependency_overrides[get_settings] = settings_override
    return TestClient(app)


def test_register_login_and_read_current_user(tmp_path: Path) -> None:
    client = make_client(tmp_path)
    credentials = {"email": "Dev@Example.com", "password": "correct horse battery staple"}

    register_response = client.post("/auth/register", json=credentials)
    assert register_response.status_code == 201
    assert register_response.json()["email"] == "dev@example.com"

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


def test_protected_route_requires_token(tmp_path: Path) -> None:
    client = make_client(tmp_path)

    response = client.get("/me")

    assert response.status_code == 401
