from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_login_validation():
    response = client.post("/api/v1/auth/login", json={"email": "", "password": ""})
    assert response.status_code == 422


def test_login_invalid_credentials():
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "nonexistent@test.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401


def test_register_validation():
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "invalid-email", "password": "short"},
    )
    assert response.status_code == 422


def test_register_user():
    import uuid
    unique_email = f"test_{uuid.uuid4().hex[:8]}@test.com"
    response = client.post(
        "/api/v1/auth/register",
        json={"email": unique_email, "password": "strongpassword123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["email"] == unique_email


def test_me_unauthorized():
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 403


def test_refresh_token_invalid():
    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "invalid_token"},
    )
    assert response.status_code == 401
