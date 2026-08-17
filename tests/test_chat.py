from fastapi.testclient import TestClient
from main import app, create_token, chat_history

client = TestClient(app)

def test_chat_requires_authentication():
    response = client.post(
        "/chat",
        json={
            "session_id": "vivek-01",
            "question": "Hello"
        }
    )

    assert response.status_code == 401

def test_chat_with_valid_token():
    token = create_token("vivek")

    response = client.post(
        "/chat",
        headers={
            "Authorization": f"Bearer {token}"
            },
            json={
                "session_id": "vivek-01",
                "question": "Hello"
            }        
        )

    assert response.status_code == 200

def test_chat_with_invalid_token():
    response = client.post(
        "/chat",
        headers={
            "Authorization": "Bearer invalid-token"
        },
        json={
            "session_id": "vivek-01",
            "question": "Hello"
        }
    )

    assert response.status_code == 401

def test_chat_empty_question():
    token = create_token("vivek")

    response = client.post(
        "/chat",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "session_id": "vivek-01",
            "question": ""
        }
    )

    assert response.status_code == 422

def test_chat_question_too_long():
    token = create_token("vivek")

    response = client.post(
        "/chat",
        headers={
            "Authorization":f"Bearer {token}",
        },
        json={
            "session_id": "vivek-01",
            "question": "a" *5001
        }
    )

    assert response.status_code == 422

def test_chat_with_other_users_session():
    token = create_token("vivek")

    response = client.post(
        "/chat",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "session_id": "rahul-01",
            "question": "Hello"
        }
    )

    assert response.status_code == 403


def test_delete_own_session():
    token = create_token("vivek")

    chat_history["vivek-01"] = [
        {
            "role": "user",
            "parts": [
                {"text": "Hello"}
            ]
        }
    ]

    response = client.delete(
        "/chat/vivek-01",
        headers={
            "Authorization": f"Bearer {token}",
        }
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Chat history cleared successfully"
    assert "vivek-01" not in chat_history


def test_delete_other_users_session():
    token = create_token("vivek")

    chat_history["amit-01"] = [
        {
            "role" : "user",
            "parts" : [
                {"text": "Hello"}
            ]
        }
    ]

    response = client.delete(
        "/chat/amit-01",
        headers={
            "Authorization": f"Bearer {token}",
        }
    )

    assert response.status_code == 403