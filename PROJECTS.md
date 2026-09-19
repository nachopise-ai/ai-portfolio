# Projects

El catálogo separa el valor profesional que debe demostrar cada proyecto de su estado real. Un proyecto marcado como diseño no se presenta como software terminado.

| Project | Role signal | Status | Evidence | Next gate |
| --- | --- | --- | --- | --- |
| `enterprise-rag-evals` | RAG, backend, evaluación, seguridad, observabilidad | Design approved | [Project brief](docs/projects/enterprise-rag-evals.md) | Implement fixture vertical slice |
| `agentops-ticket-resolver` | Tool use, approvals, reliability, auditability | Planned | Design only | Define tool contract after flagship baseline |
| `document-intelligence-es` | OCR, extraction, validation, human review | Planned | Design only | Select public/synthetic document set |
| `mlops-forecasting` | Classical ML, API serving, drift, retraining | Planned | Design only | Choose a reproducible public dataset |

## Existing work to audit

These projects may contribute software/product evidence, but their source, license, build instructions, and actual AI capability must be audited before they become featured AI projects:

- **ViralForge AI** — candidate for a genuine content-intelligence pipeline if it gains a measurable model/backend layer.
- **Kinepolis experience** — visual/product engineering evidence; not currently counted as AI evidence.
- **Webloom** — frontend/product engineering evidence; not currently counted as AI evidence.

## Evidence standard

For a project to move from `planned` to `locally verified`, it needs a reproducible local command, tests, a README using the project template, and an honest evaluation artifact. A public demo also needs a clear deployment boundary and no exposed credentials.
