from fastapi import HTTPException, status
from typing import AsyncIterator, List

from app.schemas.thesis import (
    ThesisGenerationRequest,
    ObjetoDeEstudio,
    DatosInstitucionales,
    ThesisOptions,
    ThesisSection,
    ThesisDocument,
    SectionInfo,
)
from app.chain import thesis_pipeline as tp
from app.chain.thesis_prompts import SECTION_ORDER, SECTIONS


# ── Formateo del Objeto de Estudio y datos para los prompts ────────────────────

def _bullets(items: List[str]) -> str:
    items = [i.strip() for i in (items or []) if i and i.strip()]
    if not items:
        return "(no especificado)"
    return "\n".join(f"- {i}" for i in items)


def format_objeto(o: ObjetoDeEstudio) -> str:
    return f"""PASO 1 — Coordenadas espacio-temporales (delimitación):
{o.coordenadas.strip() or "(no especificado)"}

PASO 2 — Temáticas (áreas de conocimiento / variables):
{_bullets(o.tematicas)}

PASO 3 — Hechos (situación actual observable):
{_bullets(o.hechos)}

PASO 4 — Síntomas (manifestaciones del problema):
{_bullets(o.sintomas)}

PASO 5 — Causas:
{_bullets(o.causas)}

PASO 6 — Consecuencias:
{_bullets(o.consecuencias)}

PASO 7 — Pronóstico (escenario sin intervención):
{o.pronostico.strip() or "(no especificado)"}

PASO 8 — Control al pronóstico (propuesta del investigador):
{o.control_pronostico.strip() or "(no especificado)"}

PASO 9 — Pregunta general:
{o.pregunta_general.strip() or "(no especificado)"}

PASO 9 — Preguntas específicas:
{_bullets(o.preguntas_especificas)}

PASO 10 — Título de la investigación:
{o.titulo.strip() or "(no especificado)"}"""


def format_datos(d: DatosInstitucionales, opts: ThesisOptions) -> str:
    autores = ", ".join(d.autores) if d.autores else "(no especificado)"
    fecha = " ".join(p for p in [d.mes, d.anio] if p) or "(no especificada)"
    modalidad = opts.modalidad or "(inferir del Paso 8)"
    return f"""Universidad: {d.universidad}
Vicerrectorado: {d.vicerrectorado}
Coordinación: {d.coordinacion}
Proyecto de Carrera: {d.carrera}
Título a optar: {d.titulo_a_optar}
Autores: {autores}
Tutor(a): {d.tutor or "(no especificado)"}
Ciudad: {d.ciudad}
Fecha: {fecha}
Normas de estilo: {opts.normas_estilo}
Modalidad de investigación: {modalidad}"""


# ── Operaciones ────────────────────────────────────────────────────────────────

def list_sections() -> List[SectionInfo]:
    return [SectionInfo(key=k, titulo=SECTIONS[k]["titulo"]) for k in SECTION_ORDER]


def _validate_key(key: str) -> None:
    if key not in SECTIONS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sección '{key}' no existe. Opciones: {', '.join(SECTION_ORDER)}",
        )


async def generate_section(req: ThesisGenerationRequest, key: str) -> ThesisSection:
    _validate_key(key)
    objeto = format_objeto(req.objeto_de_estudio)
    datos = format_datos(req.datos, req.opciones)
    contenido = await tp.generate_section(key, objeto, datos)
    return ThesisSection(key=key, titulo=SECTIONS[key]["titulo"], contenido=contenido)


async def stream_section(req: ThesisGenerationRequest, key: str) -> AsyncIterator[str]:
    _validate_key(key)
    objeto = format_objeto(req.objeto_de_estudio)
    datos = format_datos(req.datos, req.opciones)
    async for chunk in tp.stream_section(key, objeto, datos):
        yield chunk


async def generate_full(req: ThesisGenerationRequest) -> ThesisDocument:
    objeto = format_objeto(req.objeto_de_estudio)
    datos = format_datos(req.datos, req.opciones)
    secciones: List[ThesisSection] = []
    for key in SECTION_ORDER:
        contenido = await tp.generate_section(key, objeto, datos)
        secciones.append(
            ThesisSection(key=key, titulo=SECTIONS[key]["titulo"], contenido=contenido)
        )
    return ThesisDocument(titulo=req.objeto_de_estudio.titulo, secciones=secciones)
