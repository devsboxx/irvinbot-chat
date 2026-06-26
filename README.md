# irvinbot-chat

Microservicio de conversación de Irvinbot. Gestiona sesiones de chat, historial de mensajes y ejecuta el pipeline de IA usando LangChain. Corre en el **puerto 8002**.

---

## Qué hace

- Crea y gestiona sesiones de chat por usuario
- Persiste el historial de mensajes en PostgreSQL
- Ejecuta un pipeline RAG (Retrieval-Augmented Generation) con LangChain:
  - Recupera fragmentos relevantes de ChromaDB (documentos PDF del usuario)
  - Construye el prompt con historial + contexto + pregunta
  - Llama al LLM (Claude de Anthropic u OpenAI GPT)
  - Devuelve la respuesta completa **o en streaming SSE**

---

## Cómo funciona el pipeline de IA

```
Mensaje del usuario
  └── services/chat_service.py
        ├── chain/memory.py      ← carga historial de DB como LangChain messages
        ├── chain/retriever.py   ← conecta a ChromaDB, busca los 4 chunks más relevantes
        ├── chain/prompts.py     ← construye el ChatPromptTemplate con personalidad Irvinbot
        └── chain/pipeline.py    ← ensambla la cadena LCEL y llama al LLM
              └── Respuesta → guarda en DB → devuelve al cliente
```

### Cadena LCEL (LangChain Expression Language)

```python
chain = (
    RunnablePassthrough.assign(
        context=lambda x: retriever.invoke(x["question"])  # busca en ChromaDB
    )
    | chat_prompt          # sistema + historial + pregunta + contexto
    | llm                  # Claude o GPT
    | StrOutputParser()    # extrae el string de la respuesta
)
```

### Soporte de LLMs

El LLM se selecciona en runtime según `LLM_PROVIDER`:

| `LLM_PROVIDER` | LLM por defecto | Variable requerida |
|----------------|----------------|-------------------|
| `anthropic` | `claude-sonnet-4-6` | `ANTHROPIC_API_KEY` |
| `openai` | `gpt-4o` | `OPENAI_API_KEY` |

> **Nota:** Los embeddings de ChromaDB siempre usan OpenAI (`text-embedding-ada-002`) porque Anthropic no ofrece API de embeddings. Se necesita `OPENAI_API_KEY` independientemente del LLM elegido.

### Streaming SSE

El endpoint `/stream` usa `astream()` de LangChain y envía cada chunk como evento SSE:

```
data: {"chunk": "La hipótesis"}\n\n
data: {"chunk": " es una"}\n\n
data: {"chunk": " afirmación"}\n\n
data: [DONE]\n\n
```

---

## Estructura de archivos

```
irvinbot-chat/
├── main.py
├── Dockerfile
├── requirements.txt
├── .env.example
└── app/
    ├── api/
    │   └── chat_router.py      ← 6 endpoints, extrae user_id del JWT
    ├── services/
    │   └── chat_service.py     ← create/list/delete session, send/stream message
    ├── models/
    │   └── chat.py             ← tablas "chat_sessions" y "messages"
    ├── schemas/
    │   └── chat.py             ← contratos Pydantic
    ├── core/
    │   ├── config.py
    │   ├── database.py
    │   └── security.py         ← decode JWT (no crea tokens, solo los lee)
    ├── chain/
    │   ├── pipeline.py         ← _get_llm(), build_chain(), invoke_chain(), stream_chain()
    │   ├── memory.py           ← load_history(): DB → List[BaseMessage]
    │   ├── retriever.py        ← Chroma HttpClient → vectorstore.as_retriever(k=4)
    │   └── prompts.py          ← ChatPromptTemplate con personalidad de Irvinbot
    └── tests/
        └── test_chat.py
```

---

## Variables de entorno

| Variable | Descripción | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Conexión PostgreSQL | `...irvinbot_chat` |
| `SECRET_KEY` | Para decodificar JWT (misma que auth) | — |
| `ALGORITHM` | Algoritmo JWT | `HS256` |
| `LLM_PROVIDER` | `anthropic` o `openai` | `anthropic` |
| `ANTHROPIC_API_KEY` | API key de Anthropic | — |
| `OPENAI_API_KEY` | API key de OpenAI (siempre requerida para embeddings) | — |
| `LLM_MODEL` | Override del modelo (opcional) | Default del provider |
| `CHROMA_HOST` | Host de ChromaDB | `localhost` |
| `CHROMA_PORT` | Puerto de ChromaDB | `8004` |
| `CHROMA_COLLECTION` | Nombre de la colección | `thesis_docs` |

---

## Endpoints

Todos requieren header `Authorization: Bearer <access_token>`.

| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/chat/sessions` | Crea sesión. Body: `{title?}` |
| `GET` | `/chat/sessions` | Lista sesiones del usuario |
| `GET` | `/chat/sessions/{id}/messages` | Historial de mensajes |
| `DELETE` | `/chat/sessions/{id}` | Elimina sesión |
| `POST` | `/chat/sessions/{id}/message` | Envía mensaje, espera respuesta completa |
| `POST` | `/chat/sessions/{id}/stream` | Envía mensaje, respuesta en SSE streaming |
| `POST` | `/chat/sessions/{id}/objeto-de-estudio` | Extrae el Objeto de Estudio estructurado (10 pasos) de la conversación |
| `GET` | `/thesis/sections` | Lista las secciones generables (público) |
| `POST` | `/thesis/generate` | Genera la tesis completa (Resumen, Introducción, Cap. I, II, III) |
| `POST` | `/thesis/sections/{key}` | Genera una sola sección |
| `POST` | `/thesis/sections/{key}/stream` | Genera una sección en SSE streaming |
| `GET` | `/health` | Health check |

### Generación de tesis (a partir del Modelo de los 10 Pasos)

Flujo completo: al terminar los 10 pasos en el chat, `POST /chat/sessions/{id}/objeto-de-estudio`
**extrae** (con `with_structured_output`) el Objeto de Estudio estructurado desde la
conversación (`app/chain/thesis_extract.py`). Ese objeto se envía a los endpoints
`/thesis/*` para **redactar** la tesis siguiendo los *Lineamientos para Elaborar
Trabajos de Grado* de la UNEG (estructura, APA-UPEL) y la estructura de una tesis
de ejemplo aprobada. La "base" de redacción vive en `app/chain/thesis_prompts.py`
(un prompt enfocado por sección). El frontend orquesta extraer → revisar → generar
por streaming → exportar a PDF.

Secciones (`key`): `resumen`, `introduccion`, `capitulo_1`, `capitulo_2`, `capitulo_3`.

```bash
curl -X POST http://localhost:8002/thesis/sections/capitulo_1 \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "objeto_de_estudio": {
      "coordenadas": "Alcaldía del Municipio Libertador, Caracas, 2024-2025",
      "tematicas": ["Gestión pública", "TIC"],
      "hechos": ["Trámites en papel con 15 días de espera"],
      "sintomas": ["Acumulación de expedientes"],
      "causas": ["Ausencia de sistema digital"],
      "consecuencias": ["Pérdida de ingresos"],
      "pronostico": "Colapso administrativo para 2027",
      "control_pronostico": "Diseñar una plataforma digital de trámites",
      "pregunta_general": "¿De qué manera la digitalización incide en la eficiencia?",
      "preguntas_especificas": ["¿Cuál es la situación actual?"],
      "titulo": "Gestión documental digital en la Alcaldía del Municipio Libertador, 2024-2025"
    },
    "datos": {"autores": ["Ana Pérez"], "tutor": "MSc. Roca", "anio": "2025"}
  }'
```

> Los antecedentes, citas y artículos legales generados llevan una nota
> `⚠️ Verificar y sustituir por fuentes reales` para no incurrir en plagio
> (los lineamientos UNEG lo penalizan con la no aprobación del trabajo).

### Ejemplo: enviar mensaje
```bash
curl -X POST http://localhost:8002/chat/sessions/{session_id}/message \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"message": "¿Cuál es la diferencia entre hipótesis nula y alternativa?"}'
```

### Ejemplo: consumir streaming (JavaScript)
```javascript
const res = await fetch(`http://localhost:8002/chat/sessions/${sessionId}/stream`, {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
  body: JSON.stringify({ message: '¿Qué es el marco teórico?' }),
})
const reader = res.body.getReader()
// leer chunks SSE: "data: {"chunk": "..."}\n\n"
```

---

## Modelo de datos

### Tabla `chat_sessions`
| Columna | Tipo | Descripción |
|---------|------|-------------|
| `id` | UUID | PK |
| `user_id` | UUID | FK lógico al usuario (sin FK real, cross-service) |
| `title` | VARCHAR(255) | Auto-generado del primer mensaje |
| `created_at` | TIMESTAMPTZ | — |

### Tabla `messages`
| Columna | Tipo | Descripción |
|---------|------|-------------|
| `id` | UUID | PK |
| `session_id` | UUID | FK → chat_sessions (CASCADE DELETE) |
| `role` | VARCHAR(20) | `user` o `assistant` |
| `content` | TEXT | Contenido del mensaje |
| `created_at` | TIMESTAMPTZ | — |

---

## Cómo correr localmente

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Editar .env con tus API keys y DATABASE_URL
uvicorn main:app --reload --port 8002
```

### Correr tests
```bash
pytest app/tests/ -v
# Los tests mockean el pipeline de LangChain, no llaman a la API real
```

---

## Cómo extender este servicio

**Cambiar el prompt del bot:**
Editar `app/chain/prompts.py`, variable `SYSTEM_TEMPLATE`. El prompt actual da el rol de asistente de tesis universitaria.

**Cambiar el número de documentos recuperados:**
En `app/chain/retriever.py`, modificar `search_kwargs={"k": 4}`.

**Filtrar documentos por usuario:**
En `retriever.py`, añadir `search_kwargs={"k": 4, "filter": {"user_id": user_id}}`. Esto requiere pasar el `user_id` al retriever desde `chat_service.py`.

**Añadir títulos automáticos con IA:**
En `chat_service._update_session_title()`, en lugar de truncar el texto, llamar al LLM con un prompt corto: `"Resume en 5 palabras: {question}"`.

**Agregar más proveedores LLM:**
En `chain/pipeline._get_llm()`, añadir un nuevo `elif settings.LLM_PROVIDER == "gemini":` con el cliente correspondiente.
