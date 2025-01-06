# backend/tests/test_customers.py

def test_get_customers(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/customers", headers=headers)
    assert response.status_code == 200, \
        f"Expected status code 200, got {response.status_code}"
