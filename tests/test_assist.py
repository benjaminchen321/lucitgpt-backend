# backend/tests/test_assist.py
import openai


def test_assist_success(client, auth_token, db, mocker):
    headers = {"Authorization": f"Bearer {auth_token}"}
    mock_openai_completion = mocker.patch("openai.Completion.create")
    mock_openai_completion.return_value = type(
        "obj",
        (object,),
        {"choices": [type("obj", (object,), {"text": "This is a test response."})]},
    )

    response = client.post(
        "/assist", json={"query": "Tell me a joke."}, headers=headers
    )
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert "answer" in data, "Response should contain 'answer'."
    assert data["answer"] == "This is a test response.", "AI response mismatch."


def test_assist_empty_query(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.post("/assist", json={"query": "   "}, headers=headers)
    assert response.status_code == 400, f"Expected 400, got {response.status_code}"
    data = response.json()
    assert (
        data["detail"] == "Query cannot be empty."
    ), "Incorrect error message for empty query."


def test_assist_openai_error(client, auth_token, mocker):
    headers = {"Authorization": f"Bearer {auth_token}"}
    mock_openai_completion = mocker.patch("openai.Completion.create")
    mock_openai_completion.side_effect = openai.OpenAIError("API error")

    response = client.post(
        "/assist", json={"query": "Tell me a joke."}, headers=headers
    )
    assert response.status_code == 502, f"Expected 502, got {response.status_code}"
    data = response.json()
    assert (
        data["detail"] == "Error communicating with AI service."
    ), "Incorrect error message for OpenAI API error."


def test_assist_unexpected_error(client, auth_token, mocker):
    headers = {"Authorization": f"Bearer {auth_token}"}
    mock_openai_completion = mocker.patch("openai.Completion.create")
    mock_openai_completion.side_effect = Exception("Unexpected error")

    response = client.post(
        "/assist", json={"query": "Tell me a joke."}, headers=headers
    )
    assert response.status_code == 500, f"Expected 500, got {response.status_code}"
    data = response.json()
    assert (
        data["detail"] == "An unexpected error occurred."
    ), "Incorrect error message for unexpected error."
