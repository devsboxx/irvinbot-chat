"""
Prompts de generación de la tesis (Trabajo de Grado UNEG).

Esta es la "base" derivada de dos documentos:
  1. "Lineamientos para Elaborar Trabajos de Grado" — UNEG, CU-O-06-438 /
     RTGP-N-004 (Feb-2017, V-2): estructura, aspectos formales y normas de estilo.
  2. Tesis de ejemplo aprobada (mención honorífica) — referencia de la estructura
     real de Resumen, Introducción y Capítulos I, II y III.

El sistema toma el "Objeto de Estudio" construido con el Modelo de los 10 Pasos y
redacta cada sección de la tesis. Cada sección tiene su propio prompt enfocado
porque, en conjunto, superan con creces la ventana de contexto de un solo llamado.
"""

from langchain_core.prompts import ChatPromptTemplate


# ── Persona y reglas comunes a todas las secciones ────────────────────────────

THESIS_SYSTEM = """Eres "Polaris Redactor", un asistente académico experto en la redacción de Trabajos de Grado de pregrado de la Universidad Nacional Experimental de Guayana (UNEG), Proyecto de Carrera de Ingeniería en Informática.

Redactas siguiendo los "Lineamientos para Elaborar Trabajos de Grado" de la UNEG (CU-O-06-438, RTGP-N-004, Feb-2017, V-2) y las normas de estilo APA-UPEL.

PRINCIPIOS DE REDACCIÓN (obligatorios):
- Registro formal, académico, impersonal y en tercera persona ("se observa", "se realizó", "la presente investigación"). Nunca uses primera persona ("yo", "nosotros").
- Redacción clara, coherente y con cohesión entre párrafos; evita el lenguaje coloquial, las listas innecesarias y las frases de relleno.
- Toda afirmación teórica o dato tomado de una fuente debe llevar su cita en el texto en formato APA: (Apellido, Año). El plagio impide categóricamente la aprobación del trabajo de grado.
- ADVERTENCIA ÉTICA: cuando generes antecedentes, autores, citas, artículos legales o referencias que NO te fueron proporcionados, no los presentes como verificados. Redacta la estructura y la prosa con citas APA a modo de marcador y cierra esa sección con una nota en blockquote: "> ⚠️ Verificar y sustituir por fuentes reales consultadas; no inventar autores ni artículos." Es preferible un marcador honesto a una fuente falsa.
- Mantén coherencia absoluta con el OBJETO DE ESTUDIO recibido (los 10 pasos): no cambies el tema, el contexto, la organización ni el período.

MAPEO Modelo de los 10 Pasos -> Trabajo de Grado:
- Pasos 1 a 8 (coordenadas, temáticas, hechos, síntomas, causas, consecuencias, pronóstico y control al pronóstico) -> Capítulo I: Planteamiento del Problema.
- Paso 9 (preguntas de investigación) -> interrogantes y Objetivos (Capítulo I).
- Paso 8 (control al pronóstico) -> Objetivo General y enfoque/tipo de investigación (Capítulos I y III).
- Paso 2 (temáticas) -> Bases Teóricas y variables (Capítulo II).
- Paso 10 (título) -> título del trabajo.

FORMATO DE SALIDA:
- Devuelve ÚNICAMENTE el contenido de la sección solicitada, en Markdown, listo para incorporar al documento.
- Usa los títulos y subtítulos exactamente como los pide la sección.
- No incluyas comentarios meta ("aquí tienes", "espero que te sirva") ni repitas estas instrucciones."""


# ── Instrucciones por sección ─────────────────────────────────────────────────

RESUMEN = """Redacta la página de RESUMEN del Trabajo de Grado, siguiendo el Anexo B de los lineamientos UNEG.

ESTRUCTURA EXACTA:
1. Encabezado institucional, una línea por renglón, centrado y en MAYÚSCULAS:
   REPÚBLICA BOLIVARIANA DE VENEZUELA
   (universidad)
   (vicerrectorado)
   (coordinación)
   PROYECTO DE CARRERA: (carrera)
2. El TÍTULO del trabajo, en negrita.
3. Datos: "Autores: ...", "Tutor(a): ...", "Año: ...".
4. La palabra **RESUMEN**, centrada.
5. El cuerpo del resumen: UN bloque de MÁXIMO 300 palabras (uno o dos párrafos, prosa continua, sin viñetas) que exponga de forma sintética: (a) el problema y su contexto; (b) el objetivo general; (c) la metodología (tipo y diseño de investigación, población/muestra); (d) los resultados/hallazgos esperados o el producto desarrollado; y (e) las conclusiones principales.
6. Cierre: "**Descriptores:**" seguido de un MÁXIMO de 5 palabras clave separadas por comas.

REGLAS:
- No excedas las 300 palabras en el cuerpo del resumen.
- Deriva el objetivo del Paso 8 / Paso 10 e infiere la metodología del tipo de intervención del Paso 8.

OBJETO DE ESTUDIO:
{objeto}

DATOS DEL TRABAJO:
{datos}"""


INTRODUCCION = """Redacta la INTRODUCCIÓN del Trabajo de Grado (extensión orientativa: 600 a 900 palabras), en prosa continua y sin subtítulos internos. Encabézala con el título centrado: **INTRODUCCIÓN**.

DEBE CONTENER, EN ESTE ORDEN Y DE FORMA HILADA:
1. Contextualización general del tema (de lo global a lo particular), apoyada en el Paso 2 (temáticas) y el Paso 3 (hechos).
2. Enunciado breve del problema de investigación y su relevancia (Pasos 4 a 7).
3. Mención del objetivo general de la investigación (derivado del Paso 8 / Paso 10).
4. La justificación sintética: por qué es importante el estudio.
5. El enfoque teórico y la estrategia metodológica asumidos (en una o dos frases).
6. Un párrafo final que describa la organización del contenido: introduce con "En ese sentido, la presente investigación se estructura en los siguientes capítulos:" y describe el Capítulo I (El Problema), el Capítulo II (Marco Teórico), el Capítulo III (Marco Metodológico) y el Capítulo IV (Resultados); finaliza mencionando las conclusiones, recomendaciones, referencias y anexos.

OBJETO DE ESTUDIO:
{objeto}

DATOS DEL TRABAJO:
{datos}"""


CAPITULO_1 = """Redacta el CAPÍTULO I — EL PROBLEMA completo (extensión orientativa: 5 a 8 páginas). Usa exactamente estos títulos y subtítulos, en este orden:

# CAPÍTULO I
## EL PROBLEMA

### Planteamiento del Problema
Redacta una narrativa argumentativa tipo "embudo" (de lo general/mundial -> regional/nacional -> local/organizacional). Integra de forma hilada, en párrafos y con citas APA de apoyo:
- El contexto y la situación actual (Paso 1 coordenadas + Paso 3 hechos).
- Los síntomas observables del problema (Paso 4).
- Las causas que lo originan (Paso 5).
- Las consecuencias actuales o inminentes (Paso 6).
- El pronóstico de no intervenirse (Paso 7).
- El control al pronóstico: la alternativa o propuesta del investigador (Paso 8).
Cierra el planteamiento presentando las interrogantes de la investigación con la frase "Ante la situación planteada, surgen las siguientes interrogantes:" y a continuación la **pregunta general** (Paso 9) y luego las **preguntas específicas** (Paso 9).

### Objetivos de la Investigación
#### Objetivo General
Una sola oración en infinitivo, derivada del Paso 8 / Paso 10 y de la pregunta general (Paso 9).
#### Objetivos Específicos
Un objetivo por cada pregunta específica, redactado en infinitivo (Diagnosticar, Identificar, Caracterizar, Analizar, Determinar, Diseñar, Desarrollar...). Deben seguir una secuencia lógica: diagnóstico -> fundamentación -> análisis -> propuesta/diseño.

### Justificación de la Investigación
Desarrolla la justificación en cuatro párrafos, uno por dimensión: teórica, práctica, metodológica y social.

### Alcance de la Investigación
Delimita qué abarca el estudio en espacio, tiempo y temática con base en el Paso 1, y enuncia sus limitaciones si aplican.

OBJETO DE ESTUDIO:
{objeto}

DATOS DEL TRABAJO:
{datos}"""


CAPITULO_2 = """Redacta el CAPÍTULO II — MARCO TEÓRICO completo (extensión orientativa: 8 a 15 páginas). Usa exactamente estos títulos y subtítulos:

# CAPÍTULO II
## MARCO TEÓRICO

Un párrafo introductorio breve sobre la función del marco teórico (puedes apoyarte en Hernández-Sampieri o Arias).

### Antecedentes de la Investigación
Presenta TRES (3) antecedentes (trabajos de grado o investigaciones previas relacionadas), ordenados del más reciente al más antiguo. Para cada uno redacta un párrafo con: autor (Apellido, Año), título del trabajo, institución, objetivo del estudio, metodología empleada, principales resultados y una oración final de "aporte a la presente investigación".

### Bases Teóricas
Desarrolla los constructos y conceptos centrales derivados de las temáticas (Paso 2) y del problema. Crea un subtítulo (####) por cada concepto clave (incluye entre 4 y 6 conceptos) y desarróllalo con definiciones citadas en APA y su relación con la investigación.

### Bases Legales
Selecciona y desarrolla la normativa venezolana pertinente al tema (elige entre: Constitución de la República Bolivariana de Venezuela; Ley de Infogobierno; Ley Orgánica de Ciencia, Tecnología e Innovación; Ley sobre Mensajes de Datos y Firmas Electrónicas; Ley Especial contra los Delitos Informáticos; u otras según el tema). Para cada ley indica el artículo pertinente y explica su relación con la investigación.

> ⚠️ Verificar y sustituir antecedentes, citas y artículos legales por fuentes reales consultadas; no inventar autores ni artículos.

OBJETO DE ESTUDIO:
{objeto}

DATOS DEL TRABAJO:
{datos}"""


CAPITULO_3 = """Redacta el CAPÍTULO III — MARCO METODOLÓGICO completo (extensión orientativa: 4 a 8 páginas). Usa exactamente estos títulos y subtítulos:

# CAPÍTULO III
## MARCO METODOLÓGICO

Un párrafo introductorio breve (puedes apoyarte en Arias o en Palella y Martins sobre qué es el marco metodológico).

### Tipo de Investigación
Determina el tipo a partir del Paso 8 (tipo de intervención). Si la propuesta consiste en diseñar o desarrollar un modelo, sistema o estrategia, clasifícala como Proyecto Factible (apoyado en investigación de campo y/o documental) o como investigación aplicada/tecnológica, según corresponda; justifícalo con cita (Arias, 2012; UPEL).

### Diseño de la Investigación
Indica y justifica el diseño (por ejemplo: no experimental, de campo, transeccional), con cita (Hernández-Sampieri; Palella y Martins).

### Población y Muestra
Define la población con base en el contexto del Paso 1; define la muestra y el tipo de muestreo (probabilístico o no probabilístico/intencional), con cita.

### Técnicas e Instrumentos de Recolección de Datos
Describe las técnicas (observación, encuesta, entrevista, revisión documental) y sus instrumentos (cuestionario, guía de entrevista, lista de cotejo, cuaderno de notas), con cita (Arias, 2012).

### Técnicas de Análisis de Datos
Describe cómo se analizarán los datos recolectados (análisis cuantitativo/estadístico descriptivo y/o cualitativo).

### Procedimiento Metodológico de la Investigación
Organiza el procedimiento en fases, una por cada Objetivo Específico del Capítulo I, describiendo las actividades de cada fase.

> ⚠️ Verificar y sustituir las referencias metodológicas por las ediciones reales consultadas.

OBJETO DE ESTUDIO:
{objeto}

DATOS DEL TRABAJO:
{datos}"""


# ── Registro de secciones ──────────────────────────────────────────────────────

SECTION_ORDER: list[str] = [
    "resumen",
    "introduccion",
    "capitulo_1",
    "capitulo_2",
    "capitulo_3",
]

SECTIONS: dict[str, dict[str, str]] = {
    "resumen":      {"titulo": "Resumen", "instruction": RESUMEN},
    "introduccion": {"titulo": "Introducción", "instruction": INTRODUCCION},
    "capitulo_1":   {"titulo": "Capítulo I — El Problema", "instruction": CAPITULO_1},
    "capitulo_2":   {"titulo": "Capítulo II — Marco Teórico", "instruction": CAPITULO_2},
    "capitulo_3":   {"titulo": "Capítulo III — Marco Metodológico", "instruction": CAPITULO_3},
}


def build_section_prompt(instruction: str) -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages([
        ("system", THESIS_SYSTEM),
        ("human", instruction),
    ])
