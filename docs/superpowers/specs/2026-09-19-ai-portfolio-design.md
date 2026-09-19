# AI Engineer Portfolio Design

## Purpose

Create a public GitHub portfolio aimed at junior roles titled **AI Engineer**, **AI Application Engineer**, or **AI Solutions Engineer**. The portfolio must demonstrate the ability to take a business problem from data and software design through evaluation, security, deployment, and maintenance.

The portfolio is not a collection of short chatbot demos. Each highlighted project must show a real system boundary, reproducible setup, evidence of quality, and an honest statement of what is and is not production-ready.

## User and success criteria

The portfolio is for Nacho's job applications and interviews in Spain or remote Europe. It should be understandable to a recruiter in one minute and technically credible to an AI/software engineer in ten minutes.

Success means:

1. A GitHub hub repository presents a coherent AI-engineering profile and links to focused project repositories.
2. The first flagship project proves backend engineering, data ingestion, retrieval, agent/tool integration, evaluation, observability, security, and deployment.
3. Every quantitative claim is backed by a reproducible script, test, trace, or documented experiment.
4. No repository contains credentials, personal documents, copied proprietary data, or claims of real integrations that are only mocks.
5. The repository can be run locally by a reviewer using documented commands and public or synthetic data.

## Portfolio architecture

### Hub repository

Provisional repository name: `ai-portfolio` until the GitHub username and preferred public name are known.

Responsibilities:

- Present the target role and technical profile.
- Link to each project and show its status: planned, in progress, verified, or public demo.
- Explain the engineering themes shared across projects: Python, APIs, data, evaluation, security, observability, Docker, and cloud readiness.
- Include a short CV-oriented project summary and a contact section that remains empty until the user supplies the preferred public contact.
- Keep the hub lightweight; source code belongs in project repositories.

### Planned project repositories

1. `enterprise-rag-evals` — flagship project. A Spanish-language enterprise knowledge and incident assistant with measurable retrieval and answer quality.
2. `agentops-ticket-resolver` — tool-using incident workflow with approvals, audit trails, replay, and regression tests.
3. `document-intelligence-es` — OCR and structured extraction with confidence scores and human review.
4. `mlops-forecasting` — conventional ML/time-series service with reproducible training, monitoring, and drift handling.

Existing personal projects may be linked from the hub only after their source, license, build instructions, and actual capabilities have been audited. Visual/product projects can be listed as software work but must not be presented as AI engineering evidence without an actual AI pipeline.

## Flagship project: `enterprise-rag-evals`

### User-visible problem

An operations team has internal procedures, product documentation, and incident records. A user asks a question or describes an incident. The system retrieves the relevant evidence, answers with citations, suggests the next safe action, and refuses to invent an answer when evidence is insufficient.

The data used in the public repository must be synthetic or from clearly reusable public sources. The project must never require the user's private documents.

### Functional requirements

- Ingest PDF, Markdown, and plain-text documents through a versioned pipeline.
- Normalize, chunk, index, and retrieve documents with source metadata.
- Support keyword and semantic retrieval, with a documented comparison against a simple baseline.
- Produce answers with source citations and an explicit insufficient-evidence response.
- Expose a typed HTTP API for ingestion, search, question answering, and evaluation runs.
- Store prompt/model/configuration versions with each evaluation result.
- Provide a small web UI only as a demonstration layer; the API and evaluation suite are the core deliverables.
- Include a deterministic fixture mode so the main tests do not require a paid external model.

### Quality and evaluation requirements

- Maintain a versioned evaluation set containing questions, expected evidence, expected refusal cases, and metadata.
- Measure at minimum retrieval hit rate, citation coverage, answer correctness on the fixture set, refusal behavior, latency, and estimated cost.
- Include tests for irrelevant documents, ambiguous questions, empty indexes, malformed files, and prompt-injection text inside retrieved documents.
- Run the evaluation suite in CI and fail when a protected regression exceeds the documented tolerance.
- Publish the command and artifact that produced every reported metric; never write an unsupported “accuracy” percentage in the README.

### Security and reliability requirements

- Treat retrieved documents as untrusted content and keep them separate from system instructions.
- Validate file types and size limits before processing.
- Redact or reject obvious secrets and personal identifiers in the public fixture pipeline.
- Implement request IDs, structured logs, rate-limit configuration, timeouts, retries, and safe error messages.
- Keep model/provider keys in environment variables and provide `.env.example` without values.
- Document the trust boundary, known failure modes, and the difference between demo mode and production deployment.

### Technical baseline

- Python 3.12 or newer.
- FastAPI, Pydantic, pytest, and a typed service boundary.
- PostgreSQL with pgvector for the production-shaped local path; a lightweight fixture adapter for tests.
- Docker Compose for the local stack.
- GitHub Actions for linting, tests, and evaluation regression checks.
- OpenTelemetry-compatible traces or an equivalent local trace format.
- Provider-neutral model adapter so the test suite does not depend on one vendor or a hidden API key.

The exact model, embedding provider, cloud service, and UI framework are implementation choices. The repository must make those choices replaceable and record their version and cost assumptions.

## Interview evidence required for every project

Each project README must include:

- The business problem and why a simpler rule-based solution is insufficient or useful as a baseline.
- An architecture diagram or clear data-flow explanation.
- A local quick start and a reproducible test command.
- A short evaluation report with dataset provenance and limitations.
- One failure mode found during development and the fix or mitigation.
- Security and privacy boundaries.
- Cost and latency considerations.
- What is a demo, what is verified locally, and what is not deployed publicly.
- A short “what I would improve next” section.

## Delivery boundaries

- Creating a local repository and documentation is authorized by the user's request.
- Publishing a repository or changing account settings requires the user's authenticated GitHub session and confirmation at the final external-action step.
- No credentials, tokens, OAuth keys, private files, or personal identifiers will be invented or committed.
- A local build or passing test is not described as production deployment.

## First implementation slice

The first slice creates the hub repository skeleton, the flagship project brief, a reusable project README template, a roadmap, and contribution/security hygiene files. It does not pretend that the flagship AI system already exists. The next slice implements a small vertical path: ingest a fixture document, retrieve evidence, answer in fixture mode, and run one evaluation regression.

## Out of scope for the first slice

- Publishing to GitHub before the user is authenticated and confirms the final repository action.
- Paid model/API integrations without an explicit user-provided key.
- Real company data, personal academic documents, or private work artifacts.
- Four complete projects at once.
- Claims of hiring outcomes or production readiness.
