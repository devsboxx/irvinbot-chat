from pydantic import BaseModel, Field
from typing import List, Optional


# ── Entrada: el Objeto de Estudio (resultado del Modelo de los 10 Pasos) ───────

class ObjetoDeEstudio(BaseModel):
    """Construcción completa del Objeto de Estudio que entrega el chat al
    finalizar el Paso 10. Es la materia prima para redactar la tesis.

    Las descripciones de campo guían la extracción estructurada desde la
    conversación del Modelo de los 10 Pasos."""

    coordenadas: str = Field(
        description="Paso 1: coordenadas espacio-temporales — organización/institución, ciudad/región y período (años)."
    )
    tematicas: List[str] = Field(
        default_factory=list,
        description="Paso 2: temáticas o áreas de conocimiento que enmarcan la investigación.",
    )
    hechos: List[str] = Field(
        default_factory=list,
        description="Paso 3: hechos — situación actual observable y verificable.",
    )
    sintomas: List[str] = Field(
        default_factory=list,
        description="Paso 4: síntomas — manifestaciones visibles del problema.",
    )
    causas: List[str] = Field(
        default_factory=list,
        description="Paso 5: causas que originan los síntomas.",
    )
    consecuencias: List[str] = Field(
        default_factory=list,
        description="Paso 6: consecuencias o efectos actuales del problema.",
    )
    pronostico: str = Field(
        description="Paso 7: pronóstico — escenario futuro negativo si no se interviene."
    )
    control_pronostico: str = Field(
        description="Paso 8: control al pronóstico — propuesta/intervención del investigador."
    )
    pregunta_general: str = Field(
        description="Paso 9: pregunta general de investigación."
    )
    preguntas_especificas: List[str] = Field(
        default_factory=list,
        description="Paso 9: preguntas específicas de investigación.",
    )
    titulo: str = Field(
        description="Paso 10: título tentativo de la investigación."
    )


# ── Datos institucionales (portada / encabezado del resumen — Anexo A y B) ─────

class DatosInstitucionales(BaseModel):
    universidad: str = "Universidad Nacional Experimental de Guayana"
    vicerrectorado: str = "Vicerrectorado Académico"
    coordinacion: str = "Coordinación General de Pregrado"
    carrera: str = "Ingeniería en Informática"
    titulo_a_optar: str = "Ingeniero en Informática"
    autores: List[str] = Field(default_factory=list)
    tutor: Optional[str] = None
    ciudad: str = "Ciudad Guayana"
    mes: Optional[str] = None
    anio: Optional[str] = None


class ThesisOptions(BaseModel):
    # Si es None, el modelo infiere la modalidad a partir del Paso 8.
    modalidad: Optional[str] = None           # p. ej. "Proyecto Factible"
    normas_estilo: str = "APA-UPEL"


# ── Petición / respuesta ───────────────────────────────────────────────────────

class ThesisGenerationRequest(BaseModel):
    objeto_de_estudio: ObjetoDeEstudio
    datos: DatosInstitucionales = Field(default_factory=DatosInstitucionales)
    opciones: ThesisOptions = Field(default_factory=ThesisOptions)


class ThesisSection(BaseModel):
    key: str
    titulo: str
    contenido: str            # Markdown listo para incorporar al documento


class ThesisDocument(BaseModel):
    titulo: str
    secciones: List[ThesisSection]


class SectionInfo(BaseModel):
    key: str
    titulo: str
