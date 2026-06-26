"""
Extracción del Objeto de Estudio a partir de la conversación del chat.

Cierra el ciclo: cuando el estudiante termina el Modelo de los 10 Pasos en el
chat (conversación libre, socrática), este módulo lee la transcripción y produce
el `ObjetoDeEstudio` estructurado que alimenta la generación de la tesis.
"""

from typing import List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import BaseMessage

from app.schemas.thesis import ObjetoDeEstudio
from app.llm.providers import get_llm


EXTRACT_SYSTEM = """Eres un extractor de datos académicos. A partir de la conversación entre el tutor "Polaris" y un estudiante que construyó su Objeto de Estudio con el Modelo de los 10 Pasos, extrae la información estructurada de cada paso.

REGLAS:
- Mapea: Paso 1 -> coordenadas; Paso 2 -> temáticas; Paso 3 -> hechos; Paso 4 -> síntomas; Paso 5 -> causas; Paso 6 -> consecuencias; Paso 7 -> pronóstico; Paso 8 -> control al pronóstico; Paso 9 -> pregunta general y preguntas específicas; Paso 10 -> título.
- Usa SOLO información presente en la conversación. No inventes contenido ajeno al tema.
- Si un paso no fue cubierto, deja el campo lo más fiel posible a lo conversado o vacío; no rellenes con suposiciones no relacionadas.
- Cuando el estudiante aceptó un ejemplo propuesto por Polaris, toma ese ejemplo como su respuesta.
- El Paso 10 (título) normalmente lo genera el tutor, no el estudiante. Si el título aparece en la conversación, úsalo; si NO aparece, genéralo tú sintetizando los pasos 1 a 9 (sobre todo la propuesta del Paso 8, las temáticas del Paso 2 y las coordenadas del Paso 1). El campo `titulo` nunca debe quedar vacío.
- Redacta cada campo de forma limpia y autocontenida (sin "Paso N:" ni marcas de chat)."""

EXTRACT_HUMAN = """Conversación entre el tutor (Polaris) y el estudiante:

{transcript}

A partir de ella, extrae el Objeto de Estudio construido con el Modelo de los 10 Pasos."""


def _transcript(history: List[BaseMessage]) -> str:
    lines: List[str] = []
    for m in history:
        who = "Estudiante" if m.type == "human" else "Polaris"
        lines.append(f"{who}: {m.content}")
    return "\n".join(lines)


async def extract_objeto(history: List[BaseMessage]) -> ObjetoDeEstudio:
    prompt = ChatPromptTemplate.from_messages(
        [("system", EXTRACT_SYSTEM), ("human", EXTRACT_HUMAN)]
    )
    chain = prompt | get_llm().with_structured_output(ObjetoDeEstudio)
    return await chain.ainvoke({"transcript": _transcript(history)})
