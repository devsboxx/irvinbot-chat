from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, AsyncIterator
import uuid

from app.models.chat import ChatSession, Message
from app.schemas.chat import SessionCreate, SessionOut, MessageOut, SendMessageResponse
from app.chain import memory as mem
from app.chain import pipeline
from app.chain.retriever import get_retriever


def create_session(db: Session, user_id: str, payload: SessionCreate) -> SessionOut:
    session = ChatSession(user_id=uuid.UUID(user_id), title=payload.title)
    db.add(session)
    db.commit()
    db.refresh(session)
    return SessionOut.model_validate(session)


def list_sessions(db: Session, user_id: str) -> List[SessionOut]:
    sessions = (
        db.query(ChatSession)
        .filter(ChatSession.user_id == uuid.UUID(user_id))
        .order_by(ChatSession.created_at.desc())
        .all()
    )
    return [SessionOut.model_validate(s) for s in sessions]


def get_session_messages(db: Session, session_id: str, user_id: str) -> List[MessageOut]:
    session = _get_owned_session(db, session_id, user_id)
    messages = (
        db.query(Message)
        .filter(Message.session_id == session.id)
        .order_by(Message.created_at)
        .all()
    )
    return [MessageOut.model_validate(m) for m in messages]


def delete_session(db: Session, session_id: str, user_id: str) -> None:
    session = _get_owned_session(db, session_id, user_id)
    db.delete(session)
    db.commit()


async def send_message(
    db: Session, session_id: str, user_id: str, question: str
) -> SendMessageResponse:
    session = _get_owned_session(db, session_id, user_id)
    history = mem.load_history(db, session.id)
    retriever = get_retriever()

    answer = await pipeline.invoke_chain(retriever, question, history)

    _save_messages(db, session.id, question, answer)
    _update_session_title(db, session, question)

    return SendMessageResponse(session_id=session.id, answer=answer)


async def stream_message(
    db: Session, session_id: str, user_id: str, question: str
) -> AsyncIterator[str]:
    session = _get_owned_session(db, session_id, user_id)
    history = mem.load_history(db, session.id)
    retriever = get_retriever()

    collected: List[str] = []
    async for chunk in pipeline.stream_chain(retriever, question, history):
        collected.append(chunk)
        yield chunk

    answer = "".join(collected)
    _save_messages(db, session.id, question, answer)
    _update_session_title(db, session, question)


# ── private helpers ──────────────────────────────────────────────────────────

def _get_owned_session(db: Session, session_id: str, user_id: str) -> ChatSession:
    session = db.query(ChatSession).filter(
        ChatSession.id == uuid.UUID(session_id),
        ChatSession.user_id == uuid.UUID(user_id),
    ).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return session


def _save_messages(db: Session, session_id: uuid.UUID, question: str, answer: str) -> None:
    db.add(Message(session_id=session_id, role="user", content=question))
    db.add(Message(session_id=session_id, role="assistant", content=answer))
    db.commit()


def _update_session_title(db: Session, session: ChatSession, question: str) -> None:
    if session.title == "Nueva conversación":
        session.title = question[:60] + ("…" if len(question) > 60 else "")
        db.commit()
