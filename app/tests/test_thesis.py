import os
# Usa SQLite para el create_all de import (no requiere Postgres).
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_thesis.db")

from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

from main import app
from app.api import thesis_router, chat_router
from app.services import thesis_service
from app.schemas.thesis import ObjetoDeEstudio
from app.chain.thesis_prompts import SECTIONS, build_section_prompt

TEST_USER_ID = "00000000-0000-0000-0000-000000000001"
AUTH_HEADER = {"authorization": "Bearer fake-token"}

# Sustituye la dependencia real de auth (no necesitamos un JWT válido en pruebas).
app.dependency_overrides[thesis_router.current_user] = lambda: TEST_USER_ID
app.dependency_overrides[chat_router.current_user] = lambda: TEST_USER_ID
client = TestClient(app)

PAYLOAD = {
    "objeto_de_estudio": {
        "coordenadas": "Alcaldía del Municipio Libertador, Caracas, 2024-2025",
        "tematicas": ["Gestión pública municipal", "TIC"],
        "hechos": ["Trámites en papel con 15 días de espera"],
        "sintomas": ["Acumulación de expedientes"],
        "causas": ["Ausencia de sistema digital"],
        "consecuencias": ["Pérdida de ingresos municipales"],
        "pronostico": "Colapso administrativo para 2027 si no se interviene",
        "control_pronostico": "Diseñar una plataforma digital de gestión de trámites",
        "pregunta_general": "¿De qué manera la digitalización incide en la eficiencia de los trámites?",
        "preguntas_especificas": ["¿Cuál es la situación actual de los procesos?"],
        "titulo": "Gestión documental digital en la Alcaldía del Municipio Libertador, 2024-2025",
    },
    "datos": {"autores": ["Ana Pérez"], "tutor": "MSc. Dubraska Roca", "anio": "2025"},
}


def test_list_sections():
    res = client.get("/thesis/sections")
    assert res.status_code == 200
    data = res.json()
    assert [s["key"] for s in data] == [
        "resumen", "introduccion", "capitulo_1", "capitulo_2", "capitulo_3",
    ]


def test_generate_single_section():
    with patch(
        "app.chain.thesis_pipeline.generate_section",
        new=AsyncMock(return_value="CONTENIDO GENERADO"),
    ):
        res = client.post("/thesis/sections/resumen", json=PAYLOAD, headers=AUTH_HEADER)
    assert res.status_code == 200
    body = res.json()
    assert body["key"] == "resumen"
    assert body["titulo"] == "Resumen"
    assert body["contenido"] == "CONTENIDO GENERADO"


def test_unknown_section_returns_404():
    res = client.post("/thesis/sections/inexistente", json=PAYLOAD, headers=AUTH_HEADER)
    assert res.status_code == 404


def test_generate_full_thesis():
    with patch(
        "app.chain.thesis_pipeline.generate_section",
        new=AsyncMock(return_value="X"),
    ):
        res = client.post("/thesis/generate", json=PAYLOAD, headers=AUTH_HEADER)
    assert res.status_code == 200
    body = res.json()
    assert body["titulo"] == PAYLOAD["objeto_de_estudio"]["titulo"]
    assert [s["key"] for s in body["secciones"]] == [
        "resumen", "introduccion", "capitulo_1", "capitulo_2", "capitulo_3",
    ]


def test_stream_section():
    async def fake_stream(key, objeto, datos):
        for c in ["Primer ", "fragmento"]:
            yield c

    with patch("app.chain.thesis_pipeline.stream_section", new=fake_stream):
        res = client.post(
            "/thesis/sections/introduccion/stream", json=PAYLOAD, headers=AUTH_HEADER
        )
    assert res.status_code == 200
    assert "Primer " in res.text
    assert "fragmento" in res.text
    assert "[DONE]" in res.text


def test_missing_required_field_returns_422():
    bad = {"objeto_de_estudio": {"tematicas": ["x"]}}  # faltan campos obligatorios
    res = client.post("/thesis/sections/resumen", json=bad, headers=AUTH_HEADER)
    assert res.status_code == 422


# ── Pruebas unitarias puras (sin LLM) ──────────────────────────────────────────

def test_format_objeto_includes_all_steps():
    from app.schemas.thesis import ObjetoDeEstudio
    o = ObjetoDeEstudio(**PAYLOAD["objeto_de_estudio"])
    text = thesis_service.format_objeto(o)
    for marker in ["PASO 1", "PASO 8", "PASO 9", "PASO 10"]:
        assert marker in text
    assert "Gestión documental digital" in text


def test_prompt_uses_objeto_and_datos_vars():
    prompt = build_section_prompt(SECTIONS["resumen"]["instruction"])
    assert sorted(prompt.input_variables) == ["datos", "objeto"]


# ── Puente chat -> tesis: extracción del Objeto de Estudio ─────────────────────

def test_extract_objeto_endpoint():
    """El endpoint de extracción devuelve el ObjetoDeEstudio estructurado.
    Se mockea el servicio para no tocar la BD ni el LLM."""
    fake = ObjetoDeEstudio(
        coordenadas="Alcaldía del Municipio Libertador, Caracas, 2024-2025",
        tematicas=["Gestión pública", "TIC"],
        pronostico="Colapso administrativo para 2027",
        control_pronostico="Diseñar una plataforma digital de trámites",
        pregunta_general="¿De qué manera la digitalización incide en la eficiencia?",
        preguntas_especificas=["¿Cuál es la situación actual?"],
        titulo="Gestión documental digital en la Alcaldía del Municipio Libertador, 2024-2025",
    )
    sid = "00000000-0000-0000-0000-0000000000aa"
    with patch(
        "app.services.chat_service.extract_objeto",
        new=AsyncMock(return_value=fake),
    ):
        res = client.post(f"/chat/sessions/{sid}/objeto-de-estudio", headers=AUTH_HEADER)
    assert res.status_code == 200
    body = res.json()
    assert body["titulo"].startswith("Gestión documental digital")
    assert body["tematicas"] == ["Gestión pública", "TIC"]


def test_transcript_formatter():
    from langchain_core.messages import HumanMessage, AIMessage
    from app.chain.thesis_extract import _transcript

    text = _transcript([
        HumanMessage(content="Mi tema es TIC"),
        AIMessage(content="Perfecto, ¿dónde y cuándo?"),
    ])
    assert "Estudiante: Mi tema es TIC" in text
    assert "Polaris: Perfecto" in text
