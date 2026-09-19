from __future__ import annotations

import logging
import time
import uuid

from fastapi import FastAPI, File, Request, UploadFile
from fastapi.responses import JSONResponse

from .config import Settings
from .evaluations import run_fixture_evaluation
from .models import (
    DocumentIn,
    DocumentResponse,
    DocumentSummary,
    EvaluationReport,
    QueryRequest,
    QueryResponse,
    SearchRequest,
    SearchResponse,
)
from .security import UnsafeContentError, UnsupportedDocumentError
from .service import RAGService

logger = logging.getLogger("enterprise_rag_evals")


def create_app(settings: Settings | None = None, service: RAGService | None = None) -> FastAPI:
    resolved_settings = settings or Settings.from_env()
    rag_service = service or RAGService(resolved_settings)
    app = FastAPI(
        title="Enterprise RAG Evals",
        version="0.1.0",
        description="Evaluated, citation-first retrieval for Spanish enterprise documents.",
    )
    app.state.service = rag_service
    app.state.settings = resolved_settings

    @app.middleware("http")
    async def request_context(request: Request, call_next):
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        started = time.perf_counter()
        request.state.request_id = request_id
        try:
            response = await call_next(request)
        except Exception:
            logger.exception(
                "request_failed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                },
            )
            raise
        response.headers["x-request-id"] = request_id
        logger.info(
            "request_completed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "latency_ms": round((time.perf_counter() - started) * 1000, 3),
            },
        )
        return response

    @app.exception_handler(UnsafeContentError)
    async def unsafe_content_handler(_: Request, exc: UnsafeContentError):
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    @app.exception_handler(UnsupportedDocumentError)
    async def unsupported_document_handler(_: Request, exc: UnsupportedDocumentError):
        return JSONResponse(status_code=415, content={"detail": str(exc)})

    @app.exception_handler(ValueError)
    async def value_error_handler(_: Request, exc: ValueError):
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "enterprise-rag-evals", "provider": "local-extractive"}

    @app.post("/documents", response_model=DocumentResponse, status_code=201)
    def create_document(payload: DocumentIn) -> DocumentResponse:
        response, _ = rag_service.ingest_text(payload.filename, payload.content, payload.source_key)
        return response

    @app.post("/documents/upload", response_model=DocumentResponse, status_code=201)
    async def upload_document(file: UploadFile = File(...)) -> DocumentResponse:  # noqa: B008
        filename = file.filename or "upload.txt"
        data = await file.read(resolved_settings.max_upload_bytes + 1)
        response, _ = rag_service.ingest_bytes(filename, data)
        return response

    @app.get("/documents", response_model=list[DocumentSummary])
    def list_documents() -> list[DocumentSummary]:
        return rag_service.list_documents()

    @app.post("/search", response_model=SearchResponse)
    def search(payload: SearchRequest) -> SearchResponse:
        return rag_service.search(payload.query, payload.strategy, payload.top_k)

    @app.post("/query", response_model=QueryResponse)
    def query(payload: QueryRequest, request: Request) -> QueryResponse:
        return rag_service.query(
            payload.query, payload.strategy, payload.top_k, request.state.request_id
        )

    @app.post("/evaluations/run", response_model=EvaluationReport)
    def evaluation() -> EvaluationReport:
        return run_fixture_evaluation(resolved_settings)

    return app


app = create_app()
