from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_get_customers():
    response = client.get("/customers")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
