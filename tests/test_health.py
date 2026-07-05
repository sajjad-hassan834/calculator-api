from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "FinanceCalculator" in data["data"]["app"]


def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["status"] == "healthy"


def test_version_endpoint():
    response = client.get("/api/v1/version")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["version"] is not None


def test_health_database_endpoint():
    response = client.get("/api/v1/health/database")
    assert response.status_code in [200, 503]


def test_health_storage_endpoint():
    response = client.get("/api/v1/health/storage")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
