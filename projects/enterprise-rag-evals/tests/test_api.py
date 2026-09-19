from __future__ import annotations

from fastapi.testclient import TestClient

from app.api import create_app
from app.config import Settings
from app.service import RAGService


def test_api_exposes_health_ingestion_query_and_request_id(tmp_path):
    settings = Settings(db_path=tmp_path / "api.sqlite3")
    service = RAGService(settings)
    client = TestClient(create_app(settings, service))

    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"

    created = client.post(
        "/documents",
        json={
            "filename": "manual.md",
            "content": "La revisión de acceso debe hacerse cada 7 días.",
        },
    )
    assert created.status_code == 201
    assert created.json()["chunk_count"] == 1

    response = client.post(
        "/query",
        headers={"x-request-id": "test-request-123"},
        json={"query": "¿Cada cuánto se revisa el acceso?", "strategy": "hybrid", "top_k": 3},
    )
    assert response.status_code == 200
    assert response.headers["x-request-id"] == "test-request-123"
    assert response.json()["citations"]


def test_api_rejects_bad_document_type(tmp_path):
    settings = Settings(db_path=tmp_path / "api.sqlite3")
    client = TestClient(create_app(settings, RAGService(settings)))
    response = client.post("/documents", json={"filename": "malware.exe", "content": "x"})
    assert response.status_code == 415


def test_api_uploads_supported_text_file(tmp_path):
    settings = Settings(db_path=tmp_path / "api.sqlite3")
    client = TestClient(create_app(settings, RAGService(settings)))
    response = client.post(
        "/documents/upload",
        files={"file": ("uploaded.md", b"El procedimiento requiere dos aprobaciones.", "text/markdown")},
    )
    assert response.status_code == 201
    assert response.json()["filename"] == "uploaded.md"
