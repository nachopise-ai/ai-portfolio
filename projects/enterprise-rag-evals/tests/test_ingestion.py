from __future__ import annotations

import pytest

from app.security import UnsafeContentError, UnsupportedDocumentError


def test_ingestion_is_idempotent_and_chunks(loaded_service):
    documents = loaded_service.list_documents()
    assert len(documents) == 2
    response, duplicate = loaded_service.ingest_text(
        "security-handbook.md",
        "Las evidencias de un incidente deben conservarse durante 30 días desde el cierre. "
        "El acceso de emergencia requiere aprobación y caducidad.",
    )
    assert duplicate is True
    assert response.chunk_count == 1


def test_path_traversal_is_rejected(service):
    with pytest.raises(UnsafeContentError):
        service.ingest_text("../secrets.txt", "texto")


def test_unsupported_extension_is_rejected(service):
    with pytest.raises(UnsupportedDocumentError):
        service.ingest_text("image.png", "texto")


def test_secret_like_content_is_rejected(service):
    fake_token = "ghp_" + "x" * 24
    with pytest.raises(UnsafeContentError):
        service.ingest_text("notes.txt", f"token={fake_token}")
