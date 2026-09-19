from __future__ import annotations

import math
import re
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass

from .storage import ChunkRecord, SQLiteStore

TOKEN_PATTERN = re.compile(r"[\wÀ-ÿ]+", re.UNICODE)
STOP_WORDS = {
    "a", "al", "algo", "como", "con", "cual", "cuales", "de", "del", "desde", "el",
    "en", "es", "esta", "este", "la", "las", "lo", "los", "me", "para", "por", "que",
    "se", "su", "sus", "un", "una", "y", "qué", "cuál", "cuáles",
}


def tokenize(text: str) -> list[str]:
    normalized = unicodedata.normalize("NFKD", text.lower())
    normalized = "".join(char for char in normalized if not unicodedata.combining(char))
    return [token for token in TOKEN_PATTERN.findall(normalized) if token not in STOP_WORDS]


def fts_query(text: str) -> str:
    terms = list(dict.fromkeys(tokenize(text)))
    return " OR ".join(f'"{term.replace(chr(34), "")}"' for term in terms) or '"__empty__"'


@dataclass(frozen=True)
class RetrievedEvidence:
    chunk: ChunkRecord
    score: float
    lexical_score: float
    semantic_score: float


class TfidfIndex:
    def __init__(self, chunks: list[ChunkRecord]):
        self.chunks = chunks
        self.term_counts = [Counter(tokenize(chunk.content)) for chunk in chunks]
        document_frequency: defaultdict[str, int] = defaultdict(int)
        for counts in self.term_counts:
            for term in counts:
                document_frequency[term] += 1
        self.idf = {
            term: math.log((1 + len(chunks)) / (1 + frequency)) + 1
            for term, frequency in document_frequency.items()
        }
        self.vectors = [self._vector(counts) for counts in self.term_counts]
        self.norms = [
            math.sqrt(sum(value * value for value in vector.values())) for vector in self.vectors
        ]

    def _vector(self, counts: Counter[str]) -> dict[str, float]:
        if not counts:
            return {}
        total = sum(counts.values())
        return {
            term: (count / total) * self.idf.get(term, 1.0)
            for term, count in counts.items()
            if term in self.idf
        }

    def search(self, query: str, limit: int) -> list[tuple[ChunkRecord, float]]:
        query_vector = self._vector(Counter(tokenize(query)))
        query_norm = math.sqrt(sum(value * value for value in query_vector.values()))
        if not query_norm:
            return []
        scored: list[tuple[ChunkRecord, float]] = []
        for chunk, vector, norm in zip(self.chunks, self.vectors, self.norms):
            if not norm:
                continue
            dot = sum(value * vector.get(term, 0.0) for term, value in query_vector.items())
            score = dot / (query_norm * norm)
            if score > 0:
                scored.append((chunk, score))
        return sorted(scored, key=lambda item: item[1], reverse=True)[:limit]


class HybridRetriever:
    def __init__(self, store: SQLiteStore):
        self.store = store

    def search(
        self, query: str, strategy: str = "hybrid", top_k: int = 5
    ) -> list[RetrievedEvidence]:
        lexical_rows = self.store.search_lexical(fts_query(query), max(top_k * 4, 20))
        all_chunks = self.store.all_chunks()
        semantic_rows = TfidfIndex(all_chunks).search(query, max(top_k * 4, 20))

        lexical_by_id = {
            chunk.id: (index, chunk, rank) for index, (chunk, rank) in enumerate(lexical_rows)
        }
        semantic_by_id = {
            chunk.id: (index, chunk, score) for index, (chunk, score) in enumerate(semantic_rows)
        }
        ids = set(lexical_by_id) | set(semantic_by_id)
        results: list[RetrievedEvidence] = []
        for chunk_id in ids:
            lexical_index, lexical_chunk, raw_rank = lexical_by_id.get(chunk_id, (None, None, 0.0))
            _semantic_index, semantic_chunk, semantic_score = semantic_by_id.get(
                chunk_id, (None, None, 0.0)
            )
            chunk = lexical_chunk or semantic_chunk
            if chunk is None:
                continue
            lexical_score = 1.0 / (1 + lexical_index) if lexical_index is not None else 0.0
            # A small rank-independent signal makes the result explainable in the API.
            del raw_rank
            if strategy == "lexical":
                combined = lexical_score
            elif strategy == "semantic":
                combined = semantic_score
            else:
                combined = 0.55 * lexical_score + 0.45 * semantic_score
            results.append(
                RetrievedEvidence(
                    chunk=chunk,
                    score=combined,
                    lexical_score=lexical_score,
                    semantic_score=semantic_score,
                )
            )
        results.sort(key=lambda item: item.score, reverse=True)
        return results[:top_k]
