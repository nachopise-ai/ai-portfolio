from __future__ import annotations

import time
from pathlib import Path

from .answer import AnswerResult, ExtractiveAnswerer
from .config import Settings
from .models import DocumentResponse, DocumentSummary, Evidence, QueryResponse, SearchResponse
from .retrieval import HybridRetriever, RetrievedEvidence
from .security import detect_prompt_injection, ensure_no_obvious_secrets, validate_filename
from .storage import SQLiteStore, content_hash
from .text import chunk_text, extract_text, normalize_text


class RAGService:
    def __init__(self, settings: Settings, store: SQLiteStore | None = None):
        self.settings = settings
        self.store = store or SQLiteStore(settings.db_path)
        self.retriever = HybridRetriever(self.store)
        self.answerer = ExtractiveAnswerer(settings.min_retrieval_score)

    def ingest_text(
        self, filename: str, content: str, source_key: str | None = None
    ) -> tuple[DocumentResponse, bool]:
        safe_filename = validate_filename(filename)
        normalized = normalize_text(content)
        ensure_no_obvious_secrets(normalized)
        if not normalized:
            raise ValueError("document has no extractable text")
        chunks = chunk_text(normalized, self.settings.chunk_size, self.settings.chunk_overlap)
        text_hash = content_hash(normalized)
        document_id = f"doc_{text_hash[:20]}"
        resolved_source_key = source_key or safe_filename
        stored_chunks = [
            (
                f"{document_id}_chunk_{chunk.index:04d}",
                chunk.index,
                chunk.content,
                chunk.start_char,
                chunk.end_char,
                detect_prompt_injection(chunk.content),
            )
            for chunk in chunks
        ]
        record, duplicate = self.store.add_document(
            document_id=document_id,
            filename=safe_filename,
            source_key=resolved_source_key,
            text_hash=text_hash,
            chunks=stored_chunks,
            metadata={"source_key": resolved_source_key},
        )
        return (
            DocumentResponse(
                id=record.id,
                filename=record.filename,
                source_key=record.source_key,
                content_hash=record.content_hash,
                chunk_count=record.chunk_count,
                created_at=record.created_at,
                duplicate=duplicate,
            ),
            duplicate,
        )

    def ingest_bytes(
        self, filename: str, data: bytes, source_key: str | None = None
    ) -> tuple[DocumentResponse, bool]:
        if len(data) > self.settings.max_upload_bytes:
            raise ValueError("document exceeds configured upload limit")
        return self.ingest_text(filename, extract_text(filename, data), source_key)

    def list_documents(self) -> list[DocumentSummary]:
        return [
            DocumentSummary(
                id=record.id,
                filename=record.filename,
                source_key=record.source_key,
                content_hash=record.content_hash,
                chunk_count=record.chunk_count,
                created_at=record.created_at,
            )
            for record in self.store.list_documents()
        ]

    @staticmethod
    def _evidence(item: RetrievedEvidence) -> Evidence:
        return Evidence(
            chunk_id=item.chunk.id,
            document_id=item.chunk.document_id,
            filename=item.chunk.filename,
            source_key=item.chunk.source_key,
            content=item.chunk.content,
            score=round(item.score, 6),
            lexical_score=round(item.lexical_score, 6),
            semantic_score=round(item.semantic_score, 6),
            security_flags=list(item.chunk.security_flags),
        )

    def search(self, query: str, strategy: str, top_k: int) -> SearchResponse:
        evidence = self.retriever.search(query, strategy, top_k)
        return SearchResponse(
            query=query,
            strategy=strategy,
            evidence=[self._evidence(item) for item in evidence],
        )

    def query(
        self, query: str, strategy: str, top_k: int, request_id: str | None = None
    ) -> QueryResponse:
        started = time.perf_counter()
        evidence = self.retriever.search(query, strategy, top_k)
        answer: AnswerResult = self.answerer.answer(query, evidence)
        latency_ms = (time.perf_counter() - started) * 1000
        return QueryResponse(
            query=query,
            answer=answer.answer,
            refused=answer.refused,
            refusal_reason=answer.refusal_reason,
            grounded=answer.grounded,
            citations=answer.citations,
            evidence=[self._evidence(item) for item in evidence],
            request_id=request_id,
            latency_ms=round(latency_ms, 3),
        )

    def ingest_fixtures(self, fixture_dir: Path | None = None) -> list[DocumentResponse]:
        directory = fixture_dir or self.settings.fixture_dir
        responses: list[DocumentResponse] = []
        for path in sorted(directory.iterdir()):
            if path.suffix.lower() not in {".md", ".markdown", ".txt"}:
                continue
            response, _ = self.ingest_text(path.name, path.read_text(encoding="utf-8"), path.name)
            responses.append(response)
        return responses
