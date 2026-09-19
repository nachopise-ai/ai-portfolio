from __future__ import annotations

import pytest

from app.config import Settings
from app.service import RAGService


@pytest.fixture
def service(tmp_path):
    settings = Settings(
        db_path=tmp_path / "test.sqlite3",
        fixture_dir=tmp_path / "fixtures",
        eval_cases_path=tmp_path / "evals.json",
        min_retrieval_score=0.08,
    )
    return RAGService(settings)


@pytest.fixture
def loaded_service(service):
    service.ingest_text(
        "security-handbook.md",
        "Las evidencias de un incidente deben conservarse durante 30 días desde el cierre. "
        "El acceso de emergencia requiere aprobación y caducidad.",
    )
    service.ingest_text(
        "operations-handbook.md",
        "Una incidencia crítica debe escalarse al equipo de guardia en un máximo de 15 minutos.",
    )
    return service
