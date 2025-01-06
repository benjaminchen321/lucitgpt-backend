# backend/tests/test_customers.py

from models.init_db import Client


def test_get_customers(client, auth_token, db):
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/customers", headers=headers)
    assert (
        response.status_code == 200
    ), f"Expected status code 200, got {response.status_code}"

    data = response.json()
    assert isinstance(data, list), "Response should be a list."
    assert len(data) >= 1, "There should be at least one customer."

    # Check if the test user is in the response
    test_user = db.query(Client).filter(Client.email == "testuser@example.com").first()
    assert any(
        customer["email"] == test_user.email for customer in data
    ), "Test user not found in customers."
