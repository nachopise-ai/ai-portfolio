from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Settings:
    """Runtime configuration with safe, deterministic defaults."""

    db_path: Path = PROJECT_ROOT / "var" / "rag.sqlite3"
    fixture_dir: Path = PROJECT_ROOT / "data" / "fixtures"
    eval_cases_path: Path = PROJECT_ROOT / "data" / "evals.json"
    max_upload_bytes: int = 5_000_000
    chunk_size: int = 900
    chunk_overlap: int = 120
    top_k: int = 5
    min_retrieval_score: float = 0.08
    log_level: str = "INFO"
    provider: str = "local"
    provider_base_url: str = ""
    provider_model: str = ""
    provider_api_key: str = ""

    @classmethod
    def from_env(cls) -> Settings:
        return cls(
            db_path=Path(os.getenv("RAG_DB_PATH", str(cls.db_path))),
            fixture_dir=Path(os.getenv("RAG_FIXTURE_DIR", str(cls.fixture_dir))),
            eval_cases_path=Path(os.getenv("RAG_EVAL_CASES", str(cls.eval_cases_path))),
            max_upload_bytes=int(os.getenv("RAG_MAX_UPLOAD_BYTES", cls.max_upload_bytes)),
            chunk_size=int(os.getenv("RAG_CHUNK_SIZE", cls.chunk_size)),
            chunk_overlap=int(os.getenv("RAG_CHUNK_OVERLAP", cls.chunk_overlap)),
            top_k=int(os.getenv("RAG_TOP_K", cls.top_k)),
            min_retrieval_score=float(
                os.getenv("RAG_MIN_RETRIEVAL_SCORE", cls.min_retrieval_score)
            ),
            log_level=os.getenv("RAG_LOG_LEVEL", cls.log_level),
            provider=os.getenv("RAG_PROVIDER", cls.provider),
            provider_base_url=os.getenv("RAG_PROVIDER_BASE_URL", cls.provider_base_url),
            provider_model=os.getenv("RAG_PROVIDER_MODEL", cls.provider_model),
            provider_api_key=os.getenv("RAG_PROVIDER_API_KEY", cls.provider_api_key),
        )
