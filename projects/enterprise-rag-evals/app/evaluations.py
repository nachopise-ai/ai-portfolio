from __future__ import annotations

import json
import statistics
import tempfile
from pathlib import Path

from .config import Settings
from .models import EvaluationCase, EvaluationCaseResult, EvaluationMetrics, EvaluationReport
from .service import RAGService


def load_cases(path: Path) -> tuple[str, list[EvaluationCase]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    version = str(payload.get("dataset_version", "unknown"))
    cases = [EvaluationCase.model_validate(item) for item in payload.get("cases", [])]
    if not cases:
        raise ValueError("evaluation dataset is empty")
    return version, cases


def _p95(values: list[float]) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    index = max(0, min(len(ordered) - 1, round(0.95 * (len(ordered) - 1))))
    return ordered[index]


def run_fixture_evaluation(settings: Settings | None = None) -> EvaluationReport:
    base = settings or Settings.from_env()
    dataset_version, cases = load_cases(base.eval_cases_path)
    with tempfile.TemporaryDirectory(prefix="rag-evals-") as temporary_dir:
        fixture_settings = Settings(
            db_path=Path(temporary_dir) / "evaluation.sqlite3",
            fixture_dir=base.fixture_dir,
            eval_cases_path=base.eval_cases_path,
            max_upload_bytes=base.max_upload_bytes,
            chunk_size=base.chunk_size,
            chunk_overlap=base.chunk_overlap,
            top_k=base.top_k,
            min_retrieval_score=base.min_retrieval_score,
            provider=base.provider,
            provider_base_url=base.provider_base_url,
            provider_model=base.provider_model,
            provider_api_key=base.provider_api_key,
        )
        service = RAGService(fixture_settings)
        service.ingest_fixtures()
        results: list[EvaluationCaseResult] = []
        for case in cases:
            response = service.query(case.question, "hybrid", base.top_k)
            top_sources = [item.source_key for item in response.evidence]
            expected_hit = not case.expected_sources or any(
                source in case.expected_sources for source in top_sources
            )
            refusal_correct = response.refused is case.should_refuse
            if case.should_refuse:
                citation_coverage = 1.0 if not response.citations else 0.0
            else:
                citation_coverage = 1.0 if response.citations and response.grounded else 0.0
            results.append(
                EvaluationCaseResult(
                    id=case.id,
                    retrieved_expected_source=expected_hit,
                    refusal_correct=refusal_correct,
                    citation_coverage=citation_coverage,
                    refused=response.refused,
                    latency_ms=response.latency_ms,
                    top_sources=top_sources,
                )
            )

    latencies = [result.latency_ms for result in results]
    metrics = EvaluationMetrics(
        retrieval_hit_rate=round(
            sum(result.retrieved_expected_source for result in results) / len(results), 4
        ),
        refusal_accuracy=round(sum(result.refusal_correct for result in results) / len(results), 4),
        citation_coverage=round(
            sum(result.citation_coverage for result in results) / len(results), 4
        ),
        mean_latency_ms=round(statistics.fmean(latencies), 3),
        p95_latency_ms=round(_p95(latencies), 3),
    )
    passed = (
        metrics.retrieval_hit_rate >= 0.8
        and metrics.refusal_accuracy >= 1.0
        and metrics.citation_coverage >= 0.8
    )
    return EvaluationReport(
        dataset_version=dataset_version,
        provider="local-extractive",
        strategy="hybrid",
        cases=results,
        metrics=metrics,
        passed=passed,
        limitations=[
            "Fixture mode is deterministic and does not claim LLM quality.",
            "Semantic retrieval is a local TF-IDF baseline, not a neural embedding model.",
            "Latency is measured on the local process and is not a production SLA.",
        ],
    )
