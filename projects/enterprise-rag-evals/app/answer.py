from __future__ import annotations

import re
from dataclasses import dataclass

from .retrieval import RetrievedEvidence, tokenize
from .security import detect_prompt_injection


@dataclass(frozen=True)
class AnswerResult:
    answer: str
    refused: bool
    refusal_reason: str | None
    grounded: bool
    citations: list[dict[str, str]]


class ExtractiveAnswerer:
    """A free, deterministic answerer used as a measured baseline."""

    _sentence_pattern = re.compile(r"(?<=[.!?])\s+|\n+")

    def __init__(self, min_retrieval_score: float = 0.08):
        self.min_retrieval_score = min_retrieval_score

    def answer(self, question: str, evidence: list[RetrievedEvidence]) -> AnswerResult:
        if detect_prompt_injection(question):
            return self._refusal("unsafe_query")
        if not evidence:
            return self._refusal("insufficient_evidence")

        safe_evidence = [item for item in evidence if not item.chunk.security_flags]
        if not safe_evidence:
            return self._refusal("prompt_injection_detected")
        if safe_evidence[0].score < self.min_retrieval_score:
            return self._refusal("insufficient_evidence")

        question_terms = set(tokenize(question))
        minimum_overlap = max(1, (len(question_terms) + 1) // 2)
        candidates: list[tuple[float, RetrievedEvidence, str]] = []
        for item in safe_evidence:
            for sentence in self._sentence_pattern.split(item.chunk.content):
                sentence = sentence.strip()
                if not sentence:
                    continue
                terms = set(tokenize(sentence))
                overlap = len(question_terms & terms)
                if overlap >= minimum_overlap:
                    candidates.append((overlap / max(len(question_terms), 1), item, sentence))
        if not candidates:
            return self._refusal("insufficient_evidence")

        candidates.sort(key=lambda row: (row[0], row[1].score), reverse=True)
        selected: list[tuple[RetrievedEvidence, str]] = []
        selected_chunk_ids: set[str] = set()
        for _, item, sentence in candidates:
            if item.chunk.id in selected_chunk_ids:
                continue
            selected.append((item, sentence))
            selected_chunk_ids.add(item.chunk.id)
            if len(selected) == 2:
                break

        citations: list[dict[str, str]] = []
        answer_parts: list[str] = []
        for index, (item, sentence) in enumerate(selected, start=1):
            marker = f"S{index}"
            answer_parts.append(f"{sentence} [{marker}]")
            citations.append(
                {
                    "marker": marker,
                    "chunk_id": item.chunk.id,
                    "document_id": item.chunk.document_id,
                    "filename": item.chunk.filename,
                    "source_key": item.chunk.source_key,
                }
            )
        return AnswerResult(
            answer=" ".join(answer_parts),
            refused=False,
            refusal_reason=None,
            grounded=True,
            citations=citations,
        )

    @staticmethod
    def _refusal(reason: str) -> AnswerResult:
        messages = {
            "unsafe_query": "No puedo procesar una petición que intenta cambiar las instrucciones del sistema.",
            "prompt_injection_detected": "No respondo porque la evidencia recuperada contiene instrucciones no confiables.",
            "insufficient_evidence": "No hay evidencia suficiente en los documentos cargados para responder con seguridad.",
        }
        return AnswerResult(
            answer=messages[reason],
            refused=True,
            refusal_reason=reason,
            grounded=False,
            citations=[],
        )
