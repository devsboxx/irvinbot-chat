import json
from fastapi import APIRouter, Depends, Header
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_user_id_from_token
from app.schemas.chat import (
    SessionCreate, SessionOut, MessageOut,
    SendMessageRequest, SendMessageResponse,
)
from app.services import chat_service

router = APIRouter()


def current_user(authorization: str = Header(...)) -> str:
    return get_user_id_from_token(authorization)


@router.post("/sessions", response_model=SessionOut, status_code=201)
def create_session(
    payload: SessionCreate,
    user_id: str = Depends(current_user),
    db: Session = Depends(get_db),
):
    return chat_service.create_session(db, user_id, payload)


@router.get("/sessions", response_model=List[SessionOut])
def list_sessions(
    user_id: str = Depends(current_user),
    db: Session = Depends(get_db),
):
    return chat_service.list_sessions(db, user_id)


@router.get("/sessions/{session_id}/messages", response_model=List[MessageOut])
def get_messages(
    session_id: str,
    user_id: str = Depends(current_user),
    db: Session = Depends(get_db),
):
    return chat_service.get_session_messages(db, session_id, user_id)


@router.delete("/sessions/{session_id}", status_code=204)
def delete_session(
    session_id: str,
    user_id: str = Depends(current_user),
    db: Session = Depends(get_db),
):
    chat_service.delete_session(db, session_id, user_id)


@router.post("/sessions/{session_id}/message", response_model=SendMessageResponse)
async def send_message(
    session_id: str,
    payload: SendMessageRequest,
    user_id: str = Depends(current_user),
    db: Session = Depends(get_db),
):
    return await chat_service.send_message(db, session_id, user_id, payload.message)


@router.post("/sessions/{session_id}/stream")
async def stream_message(
    session_id: str,
    payload: SendMessageRequest,
    user_id: str = Depends(current_user),
    db: Session = Depends(get_db),
):
    async def event_generator():
        try:
            async for chunk in chat_service.stream_message(db, session_id, user_id, payload.message):
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"
        except Exception as exc:
            error_msg = _llm_error_message(exc)
            yield f"data: {json.dumps({'chunk': error_msg, 'error': True})}\n\n"
        finally:
            yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


def _llm_error_message(exc: Exception) -> str:
    from app.core.config import settings
    msg = str(exc)
    provider = settings.LLM_PROVIDER.lower()
    if "Connection refused" in msg or "ConnectError" in msg or "connect" in msg.lower():
        if provider == "ollama":
            return (
                "⚠️ No se pudo conectar al modelo de IA. "
                "Verifica que Ollama esté corriendo en tu máquina y que el modelo esté descargado "
                "(`ollama pull llama3.2`). "
                "Si prefieres usar Groq, cambia LLM_PROVIDER=groq en el .env de infra."
            )
        return f"⚠️ No se pudo conectar al proveedor de IA ({provider}). Verifica la API key y la conexión a internet."
    if "api_key" in msg.lower() or "authentication" in msg.lower() or "401" in msg:
        return f"⚠️ Error de autenticación con {provider}. Verifica que {provider.upper()}_API_KEY sea válida en el .env."
    return f"⚠️ Error al generar respuesta: {msg}"
