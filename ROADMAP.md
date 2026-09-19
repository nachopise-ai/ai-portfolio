# AI Engineer Roadmap

La regla de este portfolio es profundidad antes que cantidad: **No se añade otro proyecto destacado hasta que el actual tenga README reproducible, tests y evidencia**.

## Phase 1 — Foundation

**Objetivo:** demostrar una base de software sobre la que una solución de IA pueda mantenerse.

**Artifact:** hub README, catálogo, plantilla de proyecto, repositorio limpio, Python tipado, FastAPI, SQL, Git y Docker documentados.

**Evidence required:** comandos locales reproducibles, validación de documentación, límites de privacidad y una explicación de las decisiones técnicas.

**Interview question enabled:** “¿Cómo haces que una aplicación de IA sea mantenible y revisable por otro ingeniero?”

## Phase 2 — Flagship vertical slice

**Objetivo:** convertir `enterprise-rag-evals` en software ejecutable sin depender de una clave de pago.

**Artifact:** [fixture document -> ingestion validada -> índice fixture -> pregunta -> respuesta con cita o rechazo -> test de regresión](projects/enterprise-rag-evals/README.md).

**Evidence required:** tests de ingestión y retrieval, un caso de respuesta grounded, un caso de rechazo y un artefacto de evaluación versionado.

**Estado actual:** implementado localmente y cubierto por pytest, evaluación versionada, API FastAPI y workflow de CI. Las métricas se refieren únicamente al dataset sintético incluido.

**Interview question enabled:** “¿Cómo sabes que tu RAG recupera la información correcta y no solo produce una respuesta convincente?”

## Phase 3 — Production-shaped AI engineering

**Objetivo:** demostrar que el sistema puede evolucionar hacia un servicio operable.

**Artifact:** PostgreSQL/pgvector, retrieval híbrido, adaptador de proveedor, trazas, request IDs, análisis de coste/latencia, pruebas de seguridad y gate de regresión en CI.

**Evidence required:** comparación con la baseline léxica, dataset y métricas reproducibles, fallo real encontrado y mitigado, logs/traces locales y documentación de lo que todavía no es producción.

**Interview question enabled:** “¿Qué harías si el coste sube, la latencia empeora o el modelo empieza a responder peor después de un cambio?”

## Phase 4 — Portfolio expansion

**Objetivo:** cubrir los otros bloques que aparecen en puestos de IA aplicada sin abandonar la calidad del proyecto insignia.

**Artifacts:**

- `agentops-ticket-resolver`: herramientas, aprobaciones humanas, permisos, reintentos, auditoría y replay.
- `document-intelligence-es`: OCR, extracción estructurada, confianza y revisión humana.
- `mlops-forecasting`: modelo tradicional, API, monitorización de drift y retraining reproducible.

**Evidence required:** cada repositorio debe tener un problema distinto, baseline, tests, dataset trazable, limitaciones y una demo local que no necesite credenciales ocultas.

**Interview question enabled:** “¿Cuándo usarías un LLM, un modelo clásico, una regla o una revisión humana?”

## Definition of ready for a featured project

Un proyecto solo entra en la portada cuando tiene:

1. README reproducible.
2. Tests que cubren el flujo principal y fallos importantes.
3. Evaluación o benchmark con dataset y comando.
4. Seguridad y privacidad documentadas.
5. Estado real claramente etiquetado.
6. Una explicación defendible de qué cambiaría en producción.
