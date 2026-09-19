from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Strategy = Literal["lexical", "semantic", "hybrid"]


class DocumentIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    filename: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1, max_length=5_000_000)
    source_key: str | None = Field(default=None, max_length=255)


class DocumentResponse(BaseModel):
    id: str
    filename: str
    source_key: str
    content_hash: str
    chunk_count: int
    created_at: str
    duplicate: bool = False


class DocumentSummary(BaseModel):
    id: str
    filename: str
    source_key: str
    content_hash: str
    chunk_count: int
    created_at: str


class SearchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str = Field(min_length=2, max_length=2_000)
    strategy: Strategy = "hybrid"
    top_k: int = Field(default=5, ge=1, le=20)


class Citation(BaseModel):
    marker: str
    chunk_id: str
    document_id: str
    filename: str
    source_key: str


class Evidence(BaseModel):
    chunk_id: str
    document_id: str
    filename: str
    source_key: str
    content: str
    score: float
    lexical_score: float
    semantic_score: float
    security_flags: list[str] = Field(default_factory=list)


class SearchResponse(BaseModel):
    query: str
    strategy: Strategy
    evidence: list[Evidence]


class QueryRequest(SearchRequest):
    pass


class QueryResponse(BaseModel):
    query: str
    answer: str
    refused: bool
    refusal_reason: str | None = None
    grounded: bool
    citations: list[Citation]
    evidence: list[Evidence]
    request_id: str | None = None
    latency_ms: float


class EvaluationCase(BaseModel):
    id: str
    question: str
    expected_sources: list[str] = Field(default_factory=list)
    should_refuse: bool = False


class EvaluationCaseResult(BaseModel):
    id: str
    retrieved_expected_source: bool
    refusal_correct: bool
    citation_coverage: float
    refused: bool
    latency_ms: float
    top_sources: list[str]


class EvaluationMetrics(BaseModel):
    retrieval_hit_rate: float
    refusal_accuracy: float
    citation_coverage: float
    mean_latency_ms: float
    p95_latency_ms: float


class EvaluationReport(BaseModel):
    dataset_version: str
    provider: str
    strategy: str
    cases: list[EvaluationCaseResult]
    metrics: EvaluationMetrics
    passed: bool
    limitations: list[str]
