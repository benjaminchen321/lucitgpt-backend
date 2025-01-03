import pytest
from fastapi.testclient import TestClient
from main import app, cursor, conn

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    # Create `chat_logs` table if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_logs (
            id SERIAL PRIMARY KEY,
            user_id VARCHAR(255) NOT NULL,
            query TEXT NOT NULL,
            response TEXT NOT NULL,
            response_time_ms INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()

def test_chat_endpoint_successful():
    response = client.post(
        "/chat",
        json={"query": "Tell me about Lucid cars.", "user_id": "test_user"}
    )
    assert response.status_code == 200
    assert "response" in response.json()

def test_chat_endpoint_invalid_payload():
    response = client.post("/chat", json={})
    assert response.status_code == 422  # Unprocessable Entity

def test_chat_endpoint_error_handling():
    response = client.post(
        "/chat",
        json={"query": "", "user_id": "test_user"}
    )
    assert response.status_code == 200  # Expecting a 200 since OpenAI handles empty queries
    assert "response" in response.json()
    assert response.json()["response"]  # Ensure the response contains a message
