from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_get_appointments():
    response = client.get("/appointments")
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        assert isinstance(response.json(), list)
