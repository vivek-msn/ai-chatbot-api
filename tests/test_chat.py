from fastapi.testclient import TestClient
from main import app, create_token
from database import SessionLocal
from models import ChatSession, ChatMessage

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

    db = SessionLocal()

    try:
        chat_session = ChatSession(
            session_id="vivek-test-delete",
            user_id=1
        )

        db.add(chat_session)
        db.commit()
        db.refresh(chat_session)

        message = ChatMessage(
            session_id=chat_session.id,
            role="user",
            message="Hello"
        )

        db.add(message)
        db.commit()

    finally:
        db.close()

    response = client.delete(
        "/chat/vivek-test-delete",
        headers={
            "Authorization": f"Bearer {token}",
        }
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Chat history cleared successfully"

    db = SessionLocal()

    try:
        deleted_session = db.query(ChatSession).filter(
            ChatSession.session_id == "vivek-test-delete"
        ).first()

        assert deleted_session is None

    finally:
        db.close()


def test_delete_other_users_session():
    token = create_token("vivek")

    response = client.delete(
        "/chat/amit-01",
        headers={
            "Authorization": f"Bearer {token}",
        }
    )

    assert response.status_code == 403