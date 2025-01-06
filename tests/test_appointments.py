# backend/tests/test_appointments.py

def test_get_appointments(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/appointments", headers=headers)
    assert response.status_code in [200, 404], \
        f"Unexpected status code: {response.status_code}"
