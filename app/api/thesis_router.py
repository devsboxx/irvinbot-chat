import json
from fastapi import APIRouter, Depends, Header
from fastapi.responses import StreamingResponse
from typing import List

from app.core.security import get_user_id_from_token
from app.schemas.thesis import (
    ThesisGenerationRequest,
    ThesisSection,
    ThesisDocument,
    SectionInfo,
)
from app.services import thesis_service

router = APIRouter()


def current_user(authorization: str = Header(...)) -> str:
    return get_user_id_from_token(authorization)


@router.get("/sections", response_model=List[SectionInfo])
def list_sections():
    """Secciones disponibles para generar (en orden)."""
    return thesis_service.list_sections()


@router.post("/generate", response_model=ThesisDocument)
async def generate_full(
    payload: ThesisGenerationRequest,
    user_id: str = Depends(current_user),
):
    """Genera la tesis completa (Resumen, Introducción y Capítulos I, II y III).
    Operación pesada: para mejor UX, generar sección por sección con /sections/{key}/stream."""
    return await thesis_service.generate_full(payload)


@router.post("/sections/{key}", response_model=ThesisSection)
async def generate_section(
    key: str,
    payload: ThesisGenerationRequest,
    user_id: str = Depends(current_user),
):
    """Genera una sola sección de la tesis."""
    return await thesis_service.generate_section(payload, key)


@router.post("/sections/{key}/stream")
async def stream_section(
    key: str,
    payload: ThesisGenerationRequest,
    user_id: str = Depends(current_user),
):
    """Genera una sección con streaming (SSE), igual que el chat."""
    async def event_generator():
        try:
            async for chunk in thesis_service.stream_section(payload, key):
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"
        except Exception as exc:
            yield f"data: {json.dumps({'chunk': f'⚠️ Error al generar la sección: {exc}', 'error': True})}\n\n"
        finally:
            yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
