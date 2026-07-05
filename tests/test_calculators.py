from fastapi.testclient import TestClient
import pytest

from app.main import app
from app.dependencies.auth import get_current_admin
from app.models.auth import User

client = TestClient(app)

def mock_get_current_admin():
    return User(id="test-admin-id", email="admin@test.com", is_superadmin=True)

app.dependency_overrides[get_current_admin] = mock_get_current_admin

def test_create_calculator():
    payload = {
        "name": "Test Calculator",
        "calculator_type": "finance",
        "inputs": [
            {
                "key": "principal",
                "label": "Principal Amount",
                "input_type": "number",
                "data_type": "number",
                "is_required": True
            }
        ],
        "outputs": [
            {
                "key": "total",
                "label": "Total Amount",
                "output_type": "number",
                "data_type": "number"
            }
        ]
    }
    response = client.post("/admin/calculators", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["name"] == "Test Calculator"
    assert data["data"]["slug"] == "test-calculator"
    assert len(data["data"]["inputs"]) == 1
    assert len(data["data"]["outputs"]) == 1
    
    return data["data"]["id"]

def test_get_calculator():
    calc_id = test_create_calculator()
    response = client.get(f"/admin/calculators/{calc_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["id"] == calc_id

def test_list_calculators():
    response = client.get("/admin/calculators")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert len(data["data"]) > 0

def test_publish_calculator():
    calc_id = test_create_calculator()
    response = client.post(f"/admin/calculators/{calc_id}/publish")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["status"] == "published"
    assert data["data"]["is_published"] is True

def test_public_calculators():
    calc_id = test_create_calculator()
    client.post(f"/admin/calculators/{calc_id}/publish")
    
    response = client.get("/calculators")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

def test_duplicate_calculator():
    calc_id = test_create_calculator()
    response = client.post(f"/admin/calculators/{calc_id}/duplicate")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["name"] == "Test Calculator (Copy)"
    assert data["data"]["slug"] == "test-calculator-1"
    assert data["data"]["id"] != calc_id
    assert len(data["data"]["inputs"]) == 1
