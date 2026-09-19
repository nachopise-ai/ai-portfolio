from __future__ import annotations

import hashlib
import json
import sqlite3
import threading
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path


@dataclass(frozen=True)
class DocumentRecord:
    id: str
    filename: str
    source_key: str
    content_hash: str
    created_at: str
    chunk_count: int


@dataclass(frozen=True)
class ChunkRecord:
    id: str
    document_id: str
    filename: str
    source_key: str
    content: str
    chunk_index: int
    start_char: int
    end_char: int
    security_flags: tuple[str, ...]


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class SQLiteStore:
    """Small SQLite persistence layer with an FTS5 lexical index."""

    def __init__(self, path: Path | str):
        self.path = str(path)
        self._lock = threading.RLock()
        self._memory_connection: sqlite3.Connection | None = None
        if self.path != ":memory:":
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        if self.path == ":memory:":
            if self._memory_connection is None:
                self._memory_connection = sqlite3.connect(self.path, check_same_thread=False)
            connection = self._memory_connection
        else:
            connection = sqlite3.connect(self.path, check_same_thread=False)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        with self._lock:
            connection = self._connect()
            try:
                yield connection
                connection.commit()
            except Exception:
                connection.rollback()
                raise
            finally:
                if self.path != ":memory:":
                    connection.close()

    def _initialize(self) -> None:
        with self._connection() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    filename TEXT NOT NULL,
                    source_key TEXT NOT NULL,
                    content_hash TEXT NOT NULL UNIQUE,
                    created_at TEXT NOT NULL,
                    metadata_json TEXT NOT NULL DEFAULT '{}'
                );
                CREATE TABLE IF NOT EXISTS chunks (
                    id TEXT PRIMARY KEY,
                    document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
                    chunk_index INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    start_char INTEGER NOT NULL,
                    end_char INTEGER NOT NULL,
                    security_flags_json TEXT NOT NULL DEFAULT '[]',
                    UNIQUE(document_id, chunk_index)
                );
                CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
                    chunk_id UNINDEXED,
                    document_id UNINDEXED,
                    content,
                    tokenize = 'unicode61'
                );
                """
            )

    def add_document(
        self,
        *,
        document_id: str,
        filename: str,
        source_key: str,
        text_hash: str,
        chunks: list[tuple[str, int, str, int, int, list[str]]],
        metadata: dict[str, str] | None = None,
    ) -> tuple[DocumentRecord, bool]:
        with self._connection() as connection:
            existing = connection.execute(
                "SELECT id FROM documents WHERE content_hash = ?", (text_hash,)
            ).fetchone()
            if existing:
                return self.get_document(existing["id"]), True
            created_at = datetime.now(UTC).isoformat()
            connection.execute(
                """INSERT INTO documents(id, filename, source_key, content_hash, created_at, metadata_json)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    document_id,
                    filename,
                    source_key,
                    text_hash,
                    created_at,
                    json.dumps(metadata or {}),
                ),
            )
            for chunk_id, index, content, start, end, flags in chunks:
                connection.execute(
                    """INSERT INTO chunks(id, document_id, chunk_index, content, start_char, end_char,
                       security_flags_json) VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (chunk_id, document_id, index, content, start, end, json.dumps(flags)),
                )
                connection.execute(
                    "INSERT INTO chunks_fts(chunk_id, document_id, content) VALUES (?, ?, ?)",
                    (chunk_id, document_id, content),
                )
            return DocumentRecord(
                id=document_id,
                filename=filename,
                source_key=source_key,
                content_hash=text_hash,
                created_at=created_at,
                chunk_count=len(chunks),
            ), False

    def get_document(self, document_id: str) -> DocumentRecord:
        with self._connection() as connection:
            row = connection.execute(
                """SELECT d.*, COUNT(c.id) AS chunk_count FROM documents d
                   LEFT JOIN chunks c ON c.document_id = d.id WHERE d.id = ? GROUP BY d.id""",
                (document_id,),
            ).fetchone()
        if not row:
            raise KeyError(document_id)
        return DocumentRecord(
            id=row["id"],
            filename=row["filename"],
            source_key=row["source_key"],
            content_hash=row["content_hash"],
            created_at=row["created_at"],
            chunk_count=row["chunk_count"],
        )

    def list_documents(self) -> list[DocumentRecord]:
        with self._connection() as connection:
            rows = connection.execute(
                """SELECT d.*, COUNT(c.id) AS chunk_count FROM documents d
                   LEFT JOIN chunks c ON c.document_id = d.id GROUP BY d.id ORDER BY d.created_at"""
            ).fetchall()
        return [
            DocumentRecord(
                id=row["id"],
                filename=row["filename"],
                source_key=row["source_key"],
                content_hash=row["content_hash"],
                created_at=row["created_at"],
                chunk_count=row["chunk_count"],
            )
            for row in rows
        ]

    @staticmethod
    def _to_chunk(row: sqlite3.Row) -> ChunkRecord:
        return ChunkRecord(
            id=row["id"],
            document_id=row["document_id"],
            filename=row["filename"],
            source_key=row["source_key"],
            content=row["content"],
            chunk_index=row["chunk_index"],
            start_char=row["start_char"],
            end_char=row["end_char"],
            security_flags=tuple(json.loads(row["security_flags_json"])),
        )

    def all_chunks(self) -> list[ChunkRecord]:
        with self._connection() as connection:
            rows = connection.execute(
                """SELECT c.*, d.filename, d.source_key FROM chunks c
                   JOIN documents d ON d.id = c.document_id ORDER BY c.document_id, c.chunk_index"""
            ).fetchall()
        return [self._to_chunk(row) for row in rows]

    def search_lexical(self, query: str, limit: int) -> list[tuple[ChunkRecord, float]]:
        with self._connection() as connection:
            rows = connection.execute(
                """SELECT f.chunk_id AS id, f.document_id, f.content, bm25(chunks_fts) AS rank,
                          c.chunk_index, c.start_char, c.end_char, c.security_flags_json,
                          d.filename, d.source_key
                   FROM chunks_fts f
                   JOIN chunks c ON c.id = f.chunk_id
                   JOIN documents d ON d.id = f.document_id
                   WHERE chunks_fts MATCH ?
                   ORDER BY rank ASC LIMIT ?""",
                (query, limit),
            ).fetchall()
        return [(self._to_chunk(row), float(row["rank"])) for row in rows]
