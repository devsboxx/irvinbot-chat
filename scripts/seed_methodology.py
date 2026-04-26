#!/usr/bin/env python3
"""
Seed script: carga la guía metodológica del Modelo de los 10 Pasos en ChromaDB.

Uso:
    cd irvinbot-chat/
    python scripts/seed_methodology.py

Requisitos:
    - ChromaDB corriendo (configurado en CHROMA_HOST y CHROMA_PORT del .env)
    - Proveedor de embeddings configurado (EMBEDDING_PROVIDER en .env)

La colección destino se borra y recrea en cada ejecución para garantizar
que el contenido esté siempre sincronizado con este archivo.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import chromadb
from langchain_chroma import Chroma
from langchain_core.documents import Document

from app.core.config import settings
from app.llm.providers import get_embeddings


# ── Helpers ───────────────────────────────────────────────────────────────────

def _doc(step: int, name: str, doc_type: str, content: str) -> Document:
    return Document(
        page_content=content.strip(),
        metadata={
            "step": step,
            "step_name": name,
            "type": doc_type,
            "source": f"Modelo 10 Pasos — Paso {step}: {name} [{doc_type}]",
        },
    )


# ── Documentos de la guía metodológica ───────────────────────────────────────

DOCUMENTS: list[Document] = [

    # ── VISIÓN GENERAL ────────────────────────────────────────────────────────
    Document(
        page_content="""
El Modelo de los 10 Pasos es una metodología estructurada para la Construcción del
Objeto de Estudio en tesis universitarias. Guía al investigador desde la delimitación
del contexto hasta la formulación del título definitivo.

Relación con la investigación tradicional:
- Pasos 1 a 8  → Planteamiento del Problema (situación actual, síntomas, causas,
                  consecuencias, pronóstico y control al pronóstico)
- Paso 9        → Preguntas de Investigación (derivan en Objetivos y Justificación)
- Paso 10       → Título de la Investigación

Los 10 pasos son:
1. Coordenadas Espacio-Temporales: ¿Dónde y cuándo?
2. Temáticas: ¿Sobre qué campos del conocimiento?
3. Hechos: ¿Qué situación observable existe?
4. Síntomas: ¿Cuáles son las manifestaciones del problema?
5. Causas: ¿Qué origina los síntomas?
6. Consecuencias: ¿Qué pasa si el problema continúa?
7. Pronóstico: ¿Cuál es el escenario futuro sin intervención?
8. Control al Pronóstico: ¿Qué solución propone el investigador?
9. Preguntas de Investigación: pregunta general y específicas
10. Título de la Investigación: síntesis final

Principio fundamental: cada paso se construye sobre los anteriores.
No se puede avanzar sin consolidar el paso previo.
""".strip(),
        metadata={
            "step": 0,
            "step_name": "Visión General",
            "type": "overview",
            "source": "Modelo 10 Pasos — Visión General",
        },
    ),

    # ── PASO 1: COORDENADAS ESPACIO-TEMPORALES ────────────────────────────────
    _doc(1, "Coordenadas Espacio-Temporales", "guide", """
Propósito: Delimitar el contexto físico y temporal de la investigación.
Responde a ¿Dónde? y ¿Cuándo?

Esta delimitación es el primer acto científico: sin lugar y tiempo definidos,
la investigación no tiene alcance. Corresponde a la "Delimitación" en el modelo
de investigación tradicional.

Componentes obligatorios:
- Organización o institución específica (nombre concreto, no genérico)
- Ubicación geográfica: ciudad, municipio, región o país
- Período de tiempo: año de inicio y año de finalización

Importancia: define el alcance y evita que la investigación sea demasiado amplia
o irrealizable.
"""),

    _doc(1, "Coordenadas Espacio-Temporales", "criteria", """
Criterios para una respuesta de calidad en el Paso 1:

✓ CORRECTO:
- Menciona el nombre específico de la organización o institución
- Incluye la ciudad y/o región geográfica
- Define un período de tiempo concreto (ej: 2025-2026)
- Es realizable: el estudiante tiene acceso al contexto

✗ INCORRECTO / necesita mejora:
- "En Venezuela" → muy genérico, falta organización específica
- "En mi empresa" → falta nombre y ubicación
- Solo menciona la organización sin el período
- Período demasiado largo (más de 3 años) o ya concluido
- Varias organizaciones sin justificación de por qué se incluyen juntas

Si el estudiante responde de forma vaga, preguntarle:
"¿Puedes decirme exactamente en QUÉ organización trabajarás y en QUÉ año o período?"
"""),

    _doc(1, "Coordenadas Espacio-Temporales", "example_template", """
EJEMPLO COMPLETO:
"La investigación se realizará en las Empresas CVG (CABONORCA y CABELUM), ubicadas
en Ciudad Guayana, estado Bolívar, Venezuela, durante el período 2025-2026."

Otro ejemplo:
"El estudio se desarrollará en el Hospital Universitario Dr. Luis Razetti,
municipio Libertador, Caracas, durante el primer semestre de 2026."

PLANTILLA EDITABLE:
"La investigación se realizará en [NOMBRE DE LA ORGANIZACIÓN/INSTITUCIÓN],
ubicada en [CIUDAD], [ESTADO/REGIÓN], [PAÍS],
durante el período [AÑO INICIO]-[AÑO FIN]."
"""),

    # ── PASO 2: TEMÁTICAS ─────────────────────────────────────────────────────
    _doc(2, "Temáticas", "guide", """
Propósito: Identificar los campos del conocimiento que enmarcan la investigación.
Responde a ¿Sobre qué disciplinas o áreas académicas?

Las temáticas son los grandes "paraguas" teóricos bajo los cuales se estudia el
problema. Se conectan directamente con el Marco Teórico Conceptual y las Bases
Teóricas de la investigación tradicional.

Características:
- Son áreas del conocimiento académico con bibliografía disponible
- Deben estar relacionadas entre sí y con el Paso 1
- Anticipan las variables de la investigación
- Guían la búsqueda bibliográfica y documental

Cantidad recomendada: entre 2 y 4 temáticas principales.
"""),

    _doc(2, "Temáticas", "criteria", """
Criterios para una respuesta de calidad en el Paso 2:

✓ CORRECTO:
- Específica y académica: "Gestión del Talento Humano" en lugar de "Recursos Humanos"
- Relacionada con el contexto del Paso 1
- Existen libros, artículos y revistas académicas sobre el tema
- Las temáticas se conectan entre sí de forma lógica

✗ INCORRECTO / necesita mejora:
- Demasiado amplia: solo "Tecnología" o solo "Administración"
- No relacionada con el contexto: marketing digital en un hospital rural
- Confundir temática con objetivo: "Mejorar la gestión" no es una temática
- Una sola temática (la investigación necesita al menos 2 para tener variables)

Si el estudiante dice solo "Tecnología", orientarlo:
"Eso es muy amplio. ¿Qué aspecto de la tecnología en relación con tu organización?
Por ejemplo: Adopción de TIC, Sistemas de Información, Transformación Digital..."
"""),

    _doc(2, "Temáticas", "example_template", """
EJEMPLO COMPLETO:
Temática 1: Gerencia Pública
(Gestión y administración de organizaciones del Estado, eficiencia institucional,
liderazgo en el sector público)

Temática 2: TIC — Tecnologías de la Información y Comunicación
(Adopción tecnológica en organizaciones, sistemas de información,
transformación digital en el sector público)

Otro ejemplo (área educativa):
Temática 1: Estrategias Pedagógicas Innovadoras
Temática 2: Rendimiento Académico en Educación Media

PLANTILLA EDITABLE:
Temática 1: [ÁREA DE CONOCIMIENTO PRINCIPAL]
([descripción breve de qué abarca esta temática en el contexto de la investigación])

Temática 2: [ÁREA DE CONOCIMIENTO COMPLEMENTARIA]
([descripción breve])
"""),

    # ── PASO 3: HECHOS ────────────────────────────────────────────────────────
    _doc(3, "Hechos", "guide", """
Propósito: Describir la situación actual observable en el contexto de la
investigación. Responde a ¿Qué está pasando realmente?

Los hechos son datos de la realidad: situaciones concretas, verificables y
observables que ocurren en la organización del Paso 1.
En la investigación tradicional forman la base de la "Descripción de la Situación
Actual" dentro del Planteamiento del Problema.

Características esenciales:
- Observables: se pueden ver, medir o constatar directamente
- Verificables: otra persona puede confirmarlos independientemente
- Objetivos: no son opiniones ni interpretaciones personales
- Específicos del contexto del Paso 1

Diferencia clave con los síntomas:
Los hechos describen LA SITUACIÓN GENERAL.
Los síntomas señalan EL PROBLEMA ESPECÍFICO dentro de esa situación.
"""),

    _doc(3, "Hechos", "criteria", """
Criterios para una respuesta de calidad en el Paso 3:

✓ CORRECTO:
- Concreto: "Los procesos de aprobación superan los 30 días hábiles establecidos"
- Observable: puede ser visto o medido por alguien en la organización
- Neutro: sin juicios de valor ni interpretaciones subjetivas
- Relacionado con la organización del Paso 1
- Entre 3 y 6 hechos bien descritos

✗ INCORRECTO / necesita mejora:
- Opinión disfrazada de hecho: "El gerente no sabe trabajar"
- Demasiado vago: "Hay problemas en la empresa"
- Causa confundida con hecho: "La falta de capacitación es el problema"
  (eso es una causa, Paso 5, no un hecho)
- Más de 8 hechos irrelevantes que diluyen el foco

Pregunta guía al estudiante:
"¿Qué podrías ver, medir o registrar si visitaras esa organización hoy mismo?"
"""),

    _doc(3, "Hechos", "example_template", """
EJEMPLO COMPLETO (Empresas CVG):
1. Estructura funcional con roles y responsabilidades duplicados entre departamentos.
2. Procesos administrativos con tiempos de respuesta que superan lo establecido
   en el manual de normas.
3. Manejo inadecuado de los recursos materiales y presupuestarios asignados.
4. Quejas reiterativas de usuarios por deficiencias en la calidad del servicio.
5. Indicios de irregularidades en los procesos de contratación y adquisición.

Otro ejemplo (institución educativa):
1. Deserción escolar que alcanza el 35% en el tercer año de bachillerato.
2. Solo el 40% de los docentes aplica métodos de evaluación distintos al examen escrito.
3. Laboratorios de computación con equipos sin actualizar desde 2018.

PLANTILLA EDITABLE:
1. [SITUACIÓN OBSERVABLE 1 en la organización]
2. [SITUACIÓN OBSERVABLE 2 en la organización]
3. [SITUACIÓN OBSERVABLE 3 en la organización]
(Listar entre 3 y 6 hechos. Cada uno debe comenzar con un sustantivo o situación concreta.)
"""),

    # ── PASO 4: SÍNTOMAS ──────────────────────────────────────────────────────
    _doc(4, "Síntomas", "guide", """
Propósito: Identificar las manifestaciones directas y visibles del problema de
investigación. Responde a ¿Qué señales alertan al investigador?

Los síntomas son las señales de alarma que indican que algo no funciona bien.
Son más específicos que los hechos y apuntan directamente al núcleo del problema.
En la investigación tradicional son parte central del Planteamiento del Problema.

Regla de oro:
Si los hechos describen el escenario completo de la organización,
los síntomas son las "luces de alarma" dentro de ese escenario.

Relación con otros pasos:
- Se derivan de los Hechos (Paso 3)
- Son causados por las Causas (Paso 5)
- Si no se atienden, generan las Consecuencias (Paso 6)
"""),

    _doc(4, "Síntomas", "criteria", """
Criterios para una respuesta de calidad en el Paso 4:

✓ CORRECTO:
- Son manifestaciones observables del problema central
- Se derivan directamente de los hechos del Paso 3
- Son diferentes entre sí (no repiten el mismo problema de distintas formas)
- Apuntan al problema central que se investigará
- Entre 2 y 4 síntomas bien definidos

✗ INCORRECTO / necesita mejora:
- Repetir los mismos hechos del Paso 3 con otras palabras
- Confundir con causas: "La falta de liderazgo" ya es una causa (Paso 5)
- Síntomas sin conexión con los hechos previos
- Síntomas de un problema diferente al que se quiere investigar

Pregunta guía al estudiante:
"De todos los hechos que describiste, ¿cuáles son las señales más claras
de que hay un problema en la gestión de esa organización?"
"""),

    _doc(4, "Síntomas", "example_template", """
EJEMPLO COMPLETO (Empresas CVG):
1. Falta de adaptación organizacional a las nuevas normativas y regulaciones del sector.
2. Ausencia de mecanismos efectivos de control y seguimiento de los procesos internos.
3. Desarticulación entre las unidades gerenciales en la toma de decisiones.

Otro ejemplo (institución educativa):
1. Bajo rendimiento académico generalizado en las áreas de Matemáticas y Lengua.
2. Desmotivación observable en los estudiantes durante las actividades de aula.
3. Alta conflictividad entre pares en el ambiente escolar.

PLANTILLA EDITABLE:
1. [MANIFESTACIÓN VISIBLE DEL PROBLEMA 1]
2. [MANIFESTACIÓN VISIBLE DEL PROBLEMA 2]
3. [MANIFESTACIÓN VISIBLE DEL PROBLEMA 3]

Nota: cada síntoma debe conectarse directamente con al menos uno
de los hechos descritos en el Paso 3.
"""),

    # ── PASO 5: CAUSAS ────────────────────────────────────────────────────────
    _doc(5, "Causas", "guide", """
Propósito: Identificar los factores que originan los síntomas del problema.
Responde a ¿Por qué ocurre el problema?

Las causas son el nivel de análisis más profundo: van más allá de lo observable
para encontrar los factores raíz que generan la situación problemática.
Se conectan con las Bases Teóricas del Marco Conceptual, pues cada causa debe
tener respaldo en la literatura académica.

Tipos de causas:
- Causas directas: tienen relación inmediata con los síntomas identificados
- Causas estructurales: condiciones del sistema que facilitan el problema
- Causas contextuales: factores del entorno que influyen

Importancia: identificar bien las causas es fundamental para que el Paso 8
(Control al Pronóstico) sea coherente y viable.
"""),

    _doc(5, "Causas", "criteria", """
Criterios para una respuesta de calidad en el Paso 5:

✓ CORRECTO:
- Explican directamente los síntomas del Paso 4
- Son factores analizables académicamente (tienen teoría de respaldo)
- Son específicas: "Ausencia de planificación estratégica" en lugar de "mala gestión"
- Se conectan con las temáticas del Paso 2
- Entre 3 y 5 causas bien articuladas

✗ INCORRECTO / necesita mejora:
- Muy superficiales: "Falta de dinero", "Mala suerte"
- Confundidas con consecuencias: "El problema genera pérdidas" no es una causa
- Sin conexión con los síntomas del Paso 4
- Síntomas disfrazados de causas: repetir el Paso 4 con otras palabras

Pregunta guía al estudiante:
"¿Por qué existen esos síntomas que describiste?
¿Qué está fallando en el fondo de la organización?"
"""),

    _doc(5, "Causas", "example_template", """
EJEMPLO COMPLETO (Empresas CVG):
1. Incapacidad gerencial: ausencia de competencias técnicas y de liderazgo
   para conducir procesos de cambio organizacional.
2. Mala praxis gerencial: toma de decisiones sin base en datos,
   planificación ni normativa vigente.
3. Burocracia mal entendida: aplicación excesiva y rígida de procedimientos
   que frenan la operatividad.
4. Preminencia de criterios políticos sobre criterios técnicos
   en las decisiones estratégicas.

Otro ejemplo (institución educativa):
1. Formación docente desactualizada respecto a las metodologías de enseñanza activa.
2. Ausencia de diagnóstico de estilos de aprendizaje para adaptar la instrucción.
3. Recursos pedagógicos insuficientes y desactualizados en el aula.

PLANTILLA EDITABLE:
1. [CAUSA 1]: [explicación breve de cómo genera el síntoma]
2. [CAUSA 2]: [explicación breve]
3. [CAUSA 3]: [explicación breve]
"""),

    # ── PASO 6: CONSECUENCIAS ─────────────────────────────────────────────────
    _doc(6, "Consecuencias", "guide", """
Propósito: Describir los efectos que ya se producen o son inminentes como
resultado del problema. Responde a ¿Qué daño concreto ya está causando esto?

Las consecuencias son los impactos reales del problema sobre la organización,
sus usuarios y su entorno a corto plazo.
En la investigación tradicional forman parte de la Justificación e Importancia
del estudio, demostrando la urgencia de la intervención.

Diferencia clave con el Pronóstico:
- Consecuencias (Paso 6): impactos ya presentes o inminentes (0-1 año)
- Pronóstico (Paso 7): escenario negativo a largo plazo (3-5 años sin intervención)

Las consecuencias responden a: ¿Por qué es urgente hacer esta investigación ahora?
"""),

    _doc(6, "Consecuencias", "criteria", """
Criterios para una respuesta de calidad en el Paso 6:

✓ CORRECTO:
- Son impactos concretos, ya observables o inminentes en la organización
- Se derivan lógicamente de los síntomas y causas previos
- Demuestran la urgencia de la investigación
- Cubren distintas dimensiones: económica, humana e institucional
- Entre 3 y 5 consecuencias bien definidas

✗ INCORRECTO / necesita mejora:
- Repetir los síntomas del Paso 4 con otras palabras
- Confundir con el pronóstico (el pronóstico es más grave y más lejano en el tiempo)
- Exagerar sin sustento: "La organización quebrará mañana"
- No conectarse lógicamente con las causas identificadas

Pregunta guía al estudiante:
"¿Qué daños concretos ya está sufriendo (o sufrirá pronto) la organización,
sus trabajadores o sus usuarios por este problema?"
"""),

    _doc(6, "Consecuencias", "example_template", """
EJEMPLO COMPLETO (Empresas CVG):
1. Pérdidas económicas por ineficiencia operativa y posibles desvíos de recursos.
2. Deterioro progresivo de la calidad del servicio prestado a la comunidad.
3. Desmotivación y alta rotación del personal operativo y gerencial.
4. Pérdida de credibilidad institucional ante los entes reguladores del Estado.

Otro ejemplo (institución educativa):
1. Repitencia y deserción escolar que incrementan el costo educativo por alumno.
2. Egresados con deficiencias en competencias básicas para el mercado laboral.
3. Deterioro de la imagen institucional ante la comunidad y los entes supervisores.

PLANTILLA EDITABLE:
1. [CONSECUENCIA ECONÓMICA U OPERATIVA]
2. [CONSECUENCIA EN PERSONAS: trabajadores, usuarios o beneficiarios]
3. [CONSECUENCIA INSTITUCIONAL O SOCIAL]
4. [CONSECUENCIA ADICIONAL si aplica]
"""),

    # ── PASO 7: PRONÓSTICO ────────────────────────────────────────────────────
    _doc(7, "Pronóstico", "guide", """
Propósito: Proyectar el escenario futuro negativo a largo plazo si el problema
no es intervenido. Responde a ¿A dónde llegará la organización si nadie actúa?

El pronóstico lleva las consecuencias a su máxima expresión en el tiempo.
Mientras las consecuencias son impactos inminentes (0-1 año), el pronóstico
plantea el peor escenario posible en un horizonte de 3 a 5 años.
Refuerza la justificación de la investigación demostrando que actuar es necesario.

Función estratégica:
El pronóstico crea urgencia académica y social. Le da al investigador la razón
de ser de su trabajo.

Conexión directa:
El Paso 8 (Control al Pronóstico) será la respuesta a este escenario negativo.
"""),

    _doc(7, "Pronóstico", "criteria", """
Criterios para una respuesta de calidad en el Paso 7:

✓ CORRECTO:
- Proyección realista basada en las consecuencias del Paso 6
- Horizonte de 3 a 5 años sin intervención
- Suficientemente grave para justificar la investigación
- Conectado lógicamente con todos los pasos anteriores
- Específico para la organización del Paso 1

✗ INCORRECTO / necesita mejora:
- Repetir exactamente las consecuencias del Paso 6
- Escenario apocalíptico sin sustento lógico (exageración sin base)
- Escenario demasiado leve que no justifica la urgencia
- No conectado con el contexto organizacional del Paso 1

Pregunta guía al estudiante:
"Si dentro de 5 años nadie ha hecho nada para resolver este problema,
¿cuál sería el peor escenario realista para esa organización?"
"""),

    _doc(7, "Pronóstico", "example_template", """
EJEMPLO COMPLETO (Empresas CVG):
"De no intervenirse el problema, se prevé que en los próximos 3 a 5 años
las Empresas CVG experimenten un colapso progresivo de su capacidad operativa,
con incapacidad para cumplir su misión social ante las comunidades del estado
Bolívar, lo que podría derivar en una intervención estatal o en el cese de
sus actividades productivas."

Otro ejemplo (institución educativa):
"De mantenerse las condiciones actuales, en un horizonte de 4 años la institución
podría enfrentar cierre por incumplimiento de estándares de calidad educativa,
pérdida de matrícula superior al 60% y deterioro irreversible de su planta docente."

PLANTILLA EDITABLE:
"De no intervenirse el problema, se prevé que en los próximos [3-5 años]
[NOMBRE DE LA ORGANIZACIÓN] experimente [ESCENARIO NEGATIVO PRINCIPAL],
lo que comprometería gravemente [FUNCIÓN O MISIÓN CRÍTICA DE LA ORGANIZACIÓN]."
"""),

    # ── PASO 8: CONTROL AL PRONÓSTICO ─────────────────────────────────────────
    _doc(8, "Control al Pronóstico", "guide", """
Propósito: Proponer el enfoque o tipo de intervención que el investigador plantea
para evitar el escenario negativo del Pronóstico. Responde a ¿Qué puede hacer
el investigador para revertir ese escenario?

Aclaración importante: el Control al Pronóstico no es la solución definitiva
(eso lo desarrollará toda la investigación). Es el enfoque, estrategia o tipo
de intervención que orienta el trabajo.
Se conecta con el Objetivo General y el Tipo de Investigación.

Tipos de intervención frecuentes en tesis universitarias:
- Diseño de un modelo, sistema o estrategia
- Evaluación de una situación o programa existente
- Propuesta de mejora o reestructuración
- Diagnóstico con recomendaciones
- Implementación piloto y análisis de resultados
"""),

    _doc(8, "Control al Pronóstico", "criteria", """
Criterios para una respuesta de calidad en el Paso 8:

✓ CORRECTO:
- Coherente con las causas identificadas en el Paso 5 (ataca la raíz)
- Conectado con las temáticas del Paso 2
- Factible para un investigador universitario
- Expresa claramente el tipo de intervención
- Específico para la organización del Paso 1

✗ INCORRECTO / necesita mejora:
- Propuesta que no atiende las causas identificadas
- Demasiado vago: "Mejorar la gestión" sin especificar cómo
- Fuera del alcance universitario: "Reformar la ley nacional..."
- Repetir el pronóstico negativo sin proponer ninguna alternativa

Pregunta guía al estudiante:
"Con tus conocimientos y las temáticas que identificaste,
¿qué tipo de propuesta podrías desarrollar para atacar las causas del problema?"
"""),

    _doc(8, "Control al Pronóstico", "example_template", """
EJEMPLO COMPLETO (Empresas CVG):
"Para controlar el pronóstico, se propone el diseño de un modelo de gestión
gerencial basado en Tecnologías de la Información y Comunicación (TIC), que
permita optimizar los procesos administrativos, fortalecer los mecanismos de
control interno y promover una cultura organizacional orientada a la eficiencia
y la transparencia en las Empresas CVG."

Otro ejemplo (institución educativa):
"Se propone el diseño de una estrategia pedagógica basada en el aprendizaje
activo y colaborativo, orientada a mejorar el rendimiento académico de los
estudiantes de tercer año de bachillerato en el área de Matemáticas."

PLANTILLA EDITABLE:
"Para controlar el pronóstico, se propone el [TIPO DE INTERVENCIÓN:
diseño / evaluación / propuesta / diagnóstico] de [OBJETO: modelo / estrategia /
sistema / plan] basado en [TEMÁTICAS DEL PASO 2], orientado a [OBJETIVO CENTRAL:
resolver la causa principal], en [ORGANIZACIÓN DEL PASO 1]."
"""),

    # ── PASO 9: PREGUNTAS DE INVESTIGACIÓN ────────────────────────────────────
    _doc(9, "Preguntas de Investigación", "guide", """
Propósito: Formalizar el problema de investigación en preguntas científicas
respondibles. Responde a ¿Qué quiero saber exactamente?

Las Preguntas de Investigación son el corazón del objeto de estudio.
Se construyen sintetizando todos los pasos anteriores.

Estructura obligatoria:
- 1 Pregunta General: engloba toda la investigación (variables + espacio + tiempo)
- 3 a 5 Preguntas Específicas: desglosan la pregunta general en dimensiones investigables

Relación con la investigación tradicional:
- Cada pregunta específica deriva directamente en un Objetivo Específico
- La pregunta general deriva en el Objetivo General
- En conjunto justifican la Importancia y Justificación del estudio

Forma típica de la Pregunta General:
"¿De qué manera [Variable/Propuesta] puede [mejorar/optimizar/fortalecer]
[Situación] en [Organización] durante [Período]?"
"""),

    _doc(9, "Preguntas de Investigación", "criteria", """
Criterios para preguntas de investigación de calidad:

✓ CORRECTO — Pregunta General:
- Incluye las variables o temáticas principales de la investigación
- Menciona la organización y el período del Paso 1
- Es respondible con los recursos del investigador
- No tiene respuesta obvia de Sí/No

✓ CORRECTO — Preguntas Específicas:
- Cada una aborda una dimensión diferente de la pregunta general
- Son complementarias, no repetitivas entre sí
- En conjunto son suficientes para responder la pregunta general
- Siguen una lógica: diagnóstico → bases teóricas → análisis → propuesta

✗ INCORRECTO / necesita mejora:
- Preguntas con respuesta obvia: "¿Existe un problema en la empresa?" (sí/no)
- Preguntas específicas que repiten la misma idea
- Pregunta general sin espacio ni tiempo
- Más de 5 preguntas específicas que fragmentan demasiado la investigación

Pregunta guía al estudiante:
"¿Qué necesitas saber exactamente para poder proponer tu solución?
Empieza por lo más amplio y luego divídelo en partes."
"""),

    _doc(9, "Preguntas de Investigación", "example_template", """
EJEMPLO COMPLETO (Empresas CVG):

Pregunta General:
¿De qué manera el diseño de un modelo de gestión gerencial basado en TIC
contribuiría a optimizar los procesos administrativos de las Empresas CVG
(CABONORCA y CABELUM), Ciudad Guayana, durante el período 2025-2026?

Preguntas Específicas:
1. ¿Cuál es la situación actual de la gestión gerencial y el uso de TIC
   en las Empresas CVG? (→ Objetivo diagnóstico)
2. ¿Qué fundamentos teóricos sustentan la gestión gerencial basada en TIC
   en organizaciones públicas? (→ Objetivo de fundamentación)
3. ¿Cuáles son los factores gerenciales que inciden en la ineficiencia
   de los procesos administrativos en las Empresas CVG? (→ Objetivo analítico)
4. ¿Qué características debe tener un modelo de gestión gerencial basado
   en TIC para las Empresas CVG? (→ Objetivo propositivo)

PLANTILLA EDITABLE:
Pregunta General:
"¿De qué manera [VARIABLE INDEPENDIENTE / INTERVENCIÓN PROPUESTA] contribuiría
a [mejorar / optimizar / fortalecer] [VARIABLE DEPENDIENTE / SITUACIÓN]
en [ORGANIZACIÓN], [CIUDAD], durante [PERÍODO]?"

Preguntas Específicas:
1. ¿Cuál es la situación actual de [TEMA CENTRAL] en [ORGANIZACIÓN]?
2. ¿Qué bases teóricas sustentan [TEMÁTICA 1] y [TEMÁTICA 2]?
3. ¿Cuáles son los factores que [GENERAN EL PROBLEMA] en [ORGANIZACIÓN]?
4. ¿Cómo diseñar [LA PROPUESTA] para [ORGANIZACIÓN]?
"""),

    # ── PASO 10: TÍTULO DE LA INVESTIGACIÓN ───────────────────────────────────
    _doc(10, "Título de la Investigación", "guide", """
Propósito: Sintetizar todo el objeto de estudio en un título académico preciso
y completo. Es el resultado final del Modelo de los 10 Pasos.

El título debe expresar en 15 a 25 palabras:
- Las variables o temáticas centrales de la investigación
- El espacio: organización e institución (del Paso 1)
- El tiempo: período definido (del Paso 1)

Función del título: es la carta de presentación del trabajo de grado.
Cualquier lector debe entender el tema, el contexto y el propósito
de la investigación con una sola lectura.

Estructura típica:
[Variable/Enfoque Central] para/y [Complemento] en [Organización], [Ciudad], [Período]
"""),

    _doc(10, "Título de la Investigación", "criteria", """
Criterios para un buen título de investigación:

✓ CORRECTO:
- Incluye las variables principales o el enfoque central
- Menciona la organización y/o ciudad del Paso 1
- Indica el período del Paso 1
- Conciso: entre 15 y 25 palabras
- No usa verbos conjugados
- Comprensible para alguien fuera del área específica

✗ INCORRECTO / necesita mejora:
- Demasiado largo (más de 30 palabras con oraciones subordinadas)
- Omite la organización o el período de tiempo
- Lenguaje vago: "Mejora de la situación de la empresa..."
- Verbo conjugado: "Se mejorará la gestión de..."
- Demasiado corto y genérico: solo "Gestión y TIC"
- Siglas sin aclarar dentro del propio título

Pregunta guía al estudiante:
"Si alguien leyera solo el título de tu tesis,
¿entendería qué estudiaste, dónde y cuándo?"
"""),

    _doc(10, "Título de la Investigación", "example_template", """
EJEMPLO COMPLETO (basado en los pasos anteriores):

Título con propuesta de diseño:
"Modelo de Gestión Gerencial basado en Tecnologías de la Información y
Comunicación (TIC) para la Optimización de los Procesos Administrativos
en las Empresas CVG: CABONORCA y CABELUM, Ciudad Guayana, 2025-2026"

Título con dos variables relacionadas:
"Gestión Gerencial y su Relación con la Implementación de TIC en Empresas
del Sector Público, Ciudad Guayana, 2025-2026"

Ejemplo de área educativa:
"Estrategia Pedagógica Basada en Aprendizaje Activo para el Mejoramiento
del Rendimiento Académico en Matemáticas, Liceo Bolivariano Simón Rodríguez,
Caracas, 2026"

PLANTILLAS EDITABLES:

Opción 1 — Propuesta / Diseño:
"[Modelo/Estrategia/Sistema/Plan] de [TEMÁTICA CENTRAL] para [OBJETIVO]
en [ORGANIZACIÓN], [CIUDAD], [PERÍODO]"

Opción 2 — Dos variables:
"[VARIABLE 1] y su Relación con [VARIABLE 2] en [ORGANIZACIÓN], [CIUDAD], [PERÍODO]"

Opción 3 — Evaluación / Diagnóstico:
"[Evaluación/Diagnóstico/Análisis] de [OBJETO DE ESTUDIO]
en [ORGANIZACIÓN], [CIUDAD], [PERÍODO]"
"""),
]


# ── Script principal ──────────────────────────────────────────────────────────

def main() -> None:
    print(f"Conectando a ChromaDB en {settings.CHROMA_HOST}:{settings.CHROMA_PORT}...")
    client = chromadb.HttpClient(
        host=settings.CHROMA_HOST,
        port=settings.CHROMA_PORT,
    )

    print(f"Borrando colección existente '{settings.CHROMA_COLLECTION}' (si existe)...")
    try:
        client.delete_collection(settings.CHROMA_COLLECTION)
        print("  Colección anterior eliminada.")
    except Exception:
        print("  No existía colección previa, continuando.")

    print(f"Cargando {len(DOCUMENTS)} documentos con embeddings ({settings.EMBEDDING_PROVIDER})...")
    embeddings = get_embeddings()

    vectorstore = Chroma.from_documents(
        documents=DOCUMENTS,
        embedding=embeddings,
        client=client,
        collection_name=settings.CHROMA_COLLECTION,
    )

    print(f"\n✓ Seeding completado.")
    print(f"  Colección : {settings.CHROMA_COLLECTION}")
    print(f"  Documentos: {len(DOCUMENTS)}")
    print(f"  Pasos     : 0 (visión general) + 1 a 10 (guía, criterios, ejemplo/plantilla)")

    print("\nVerificando con consulta de prueba...")
    results = vectorstore.similarity_search("¿Qué son las coordenadas espacio-temporales?", k=2)
    for r in results:
        print(f"  [{r.metadata['source']}]")
    print("\n✓ Base de conocimiento lista.")


if __name__ == "__main__":
    main()
