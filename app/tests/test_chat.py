import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, AsyncMock

from main import app
from app.core.database import Base, get_db
from app.core.security import get_user_id_from_token

SQLALCHEMY_TEST_URL = "sqlite:///./test_chat.db"
engine = create_engine(SQLALCHEMY_TEST_URL, connect_args={"check_same_thread": False})
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

TEST_USER_ID = "00000000-0000-0000-0000-000000000001"
AUTH_HEADER = {"authorization": "Bearer fake-token"}


def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


def override_current_user():
    return TEST_USER_ID


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_user_id_from_token] = override_current_user
Base.metadata.create_all(bind=engine)
client = TestClient(app)


def test_create_session():
    res = client.post("/chat/sessions", json={"title": "Mi tesis"}, headers=AUTH_HEADER)
    assert res.status_code == 201
    assert res.json()["title"] == "Mi tesis"


def test_list_sessions():
    client.post("/chat/sessions", json={"title": "Sesión A"}, headers=AUTH_HEADER)
    res = client.get("/chat/sessions", headers=AUTH_HEADER)
    assert res.status_code == 200
    assert len(res.json()) >= 1


def test_delete_session():
    create_res = client.post("/chat/sessions", json={}, headers=AUTH_HEADER)
    session_id = create_res.json()["id"]
    del_res = client.delete(f"/chat/sessions/{session_id}", headers=AUTH_HEADER)
    assert del_res.status_code == 204


def test_get_messages_empty():
    create_res = client.post("/chat/sessions", json={}, headers=AUTH_HEADER)
    session_id = create_res.json()["id"]
    res = client.get(f"/chat/sessions/{session_id}/messages", headers=AUTH_HEADER)
    assert res.status_code == 200
    assert res.json() == []


def test_send_message():
    create_res = client.post("/chat/sessions", json={}, headers=AUTH_HEADER)
    session_id = create_res.json()["id"]

    with patch("app.chain.pipeline.invoke_chain", new=AsyncMock(return_value="Respuesta de prueba")):
        with patch("app.chain.retriever.get_retriever", return_value=None):
            res = client.post(
                f"/chat/sessions/{session_id}/message",
                json={"message": "¿Qué es una hipótesis?"},
                headers=AUTH_HEADER,
            )
    assert res.status_code == 200
    assert res.json()["answer"] == "Respuesta de prueba"


def test_session_not_found():
    res = client.get(
        "/chat/sessions/00000000-0000-0000-0000-000000000099/messages",
        headers=AUTH_HEADER,
    )
    assert res.status_code == 404
