# Enterprise RAG Evals

Sistema RAG ejecutable para documentación empresarial en español. El objetivo no es
simular un chatbot, sino hacer visibles las partes que suelen romperse en producción:
ingestión, retrieval, citas, rechazo seguro, evaluación, trazabilidad y límites de
privacidad.

## Qué demuestra

- API tipada con FastAPI para ingestión, búsqueda, consulta y evaluaciones.
- Baseline léxica con SQLite FTS5 y baseline semántica local TF-IDF.
- Fusión híbrida reproducible, con scores separados para inspeccionar el resultado.
- Respuestas extractivas con citas `[S1]` y rechazo cuando no hay evidencia suficiente.
- Detección de prompt injection en documentos recuperados, tratados como datos no confiables.
- Dataset versionado, métricas de retrieval, cobertura de citas, rechazo y latencia.
- Adaptador OpenAI-compatible opcional, sin clave incluida ni llamada por defecto.
- Docker y CI listos para una ejecución sin tarjeta ni proveedor externo.

## Quick start

Requiere Python 3.11+.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m app.cli eval --output artifacts\evaluation.json
python -m app.cli serve
```

La evaluación debe terminar con `passed: true`. La API queda en
`http://127.0.0.1:8000`; su contrato interactivo está en
`http://127.0.0.1:8000/docs`.

## Probar la API

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health

Invoke-RestMethod http://127.0.0.1:8000/documents `
  -Method Post -ContentType 'application/json' `
  -Body (@{
    filename = 'manual-local.md'
    content = 'El equipo debe revisar los permisos cada 7 días.'
  } | ConvertTo-Json)

Invoke-RestMethod http://127.0.0.1:8000/query `
  -Method Post -ContentType 'application/json' `
  -Body (@{
    query = '¿Cada cuánto se revisan los permisos?'
    strategy = 'hybrid'
    top_k = 5
  } | ConvertTo-Json)
```

Endpoints principales:

| Método | Ruta | Propósito |
| --- | --- | --- |
| GET | `/health` | estado y proveedor activo |
| POST | `/documents` | ingesta de texto/Markdown |
| POST | `/documents/upload` | ingesta de Markdown, TXT o PDF |
| GET | `/documents` | inventario de documentos |
| POST | `/search` | evidencia lexical, semantic o híbrida |
| POST | `/query` | respuesta extractiva con citas o rechazo |
| POST | `/evaluations/run` | evaluación versionada de fixtures |

## Evaluación reproducible

```powershell
python -m app.cli eval --output artifacts\evaluation.json
pytest
```

El fixture incluye preguntas respondibles, una pregunta sin evidencia y una nota con
prompt injection. El informe no pretende ser una cifra de calidad de un LLM: mide esta
baseline local sobre este dataset concreto. Las limitaciones se guardan junto al
artefacto.

## Proveedor externo opcional

La implementación por defecto es local y determinista. `app/provider.py` contiene un
adaptador OpenAI-compatible para una siguiente fase. Si se usa, la URL, el modelo y la
clave deben llegar por variables de entorno; nunca se escriben en el repositorio ni se
incluyen en fixtures. No se ha probado aquí una llamada real ni se afirma que exista un
despliegue público.

## Docker

```powershell
docker compose up --build
```

Esto publica la API en `http://127.0.0.1:8000` y mantiene SQLite en un volumen local.

## Límites actuales

- TF-IDF es una baseline semántica ligera; todavía no es un embedding neural.
- SQLite sirve para la demo reproducible; producción requeriría PostgreSQL/pgvector,
  migraciones, autenticación y controles de red.
- El answerer extractivo prueba groundedness y citas, pero no sustituye una evaluación
  de un modelo generativo.
- No hay datos de clientes, PII, claves, SLA ni métricas de producción.
