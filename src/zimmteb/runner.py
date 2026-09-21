"""Validate -> MTEB task -> model -> native and enriched results -> report."""

import random
import time
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np

from zimmteb.cache import content_key
from zimmteb.config import ModelConfig, model_config, registry
from zimmteb.datasets.registry import RetrievalDataset, load_dataset
from zimmteb.datasets.validation import validate
from zimmteb.hardware import MemorySampler, select_device, system_info
from zimmteb.metrics import ranking_metrics, slices
from zimmteb.models.adapters import EmbeddingModelAdapter, create_adapter
from zimmteb.reporting import generate_report
from zimmteb.results import QueryResult, RunConfig, RunResult, read_result, write_json


def local_model_fingerprint(config: ModelConfig) -> str | None:
    import hashlib

    directory = Path(config.model_name)
    if not directory.is_dir():
        return None
    digest = hashlib.sha256()
    for path in sorted(p for p in directory.rglob("*") if p.is_file()):
        digest.update(str(path.relative_to(directory)).replace("\\", "/").encode())
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
    return digest.hexdigest()


def run_benchmark(
    config: RunConfig,
    output: Path,
    cache: Path | None = None,
    resume: bool = False,
    adapter: EmbeddingModelAdapter | None = None,
) -> RunResult:
    import mteb
    import torch

    from zimmteb.tasks import MTEBSearchBridge, ZimRetrievalTask, local_benchmark

    start = time.perf_counter()
    data = load_dataset(config.dataset)
    validation = validate(data)
    if not validation.valid:
        raise ValueError("Dataset validation failed: " + "; ".join(validation.errors))
    if config.version != data.manifest.benchmark_version:
        raise ValueError("Benchmark config version differs from dataset benchmark version")
    for value, kind in (
        (config.language, "languages"),
        (config.document_language, "languages"),
        (config.domain, "domains"),
    ):
        if value is not None and value not in registry(kind):
            raise ValueError(f"Unknown {kind} filter: {value}")
    queries = [
        q
        for q in data.queries
        if q.split == config.split
        and (config.language is None or q.query_language == config.language)
        and (config.domain is None or q.domain == config.domain)
    ]
    if not queries:
        raise ValueError("No queries match the selected split/language/domain")
    eligible_query_ids = {query.id for query in queries}
    # Query filters keep the full corpus; an explicit target language defines a
    # different retrieval task over every document in that target language.
    task_data = data
    if config.document_language:
        documents = [d for d in data.documents if d.language == config.document_language]
        target_ids = {d.document_id for d in documents}
        selected_queries = []
        for query in queries:
            if not target_ids.intersection(query.positive_document_ids):
                continue
            updates = {
                field: [id_ for id_ in getattr(query, field) if id_ in target_ids]
                for field in (
                    "positive_document_ids",
                    "negative_document_ids",
                    "hard_negative_document_ids",
                )
            }
            selected_queries.append(query.model_copy(update=updates))
        queries = selected_queries
        if not queries:
            raise ValueError("No queries have positive judgments in the target document language")
        task_data = RetrievalDataset(data.manifest, documents, queries, data.actual_checksum)
    selected = model_config(config.model).model_copy(
        update={"batch_size": config.batch_size, "precision": config.precision}
    )
    if adapter is not None and adapter.config != selected:
        raise ValueError("Injected adapter configuration differs from recorded model configuration")
    device = select_device(config.device)
    environment = system_info()
    identity_parts = {
        "config": config.model_dump(),
        "model": selected.model_dump(),
        "local_model_checksum": local_model_fingerprint(selected),
        "dataset_checksum": data.actual_checksum,
        "manifest": data.manifest.model_dump(mode="json"),
        "device": device,
        "environment": environment,
        "implementation": "0.1.0",
    }
    # Dirty source changes must invalidate resume and embeddings even before a commit.
    source_files = sorted(Path(__file__).parent.rglob("*.py"))
    identity_parts["source_checksum"] = content_key(
        {
            str(p.relative_to(Path(__file__).parent)): p.read_text(encoding="utf-8")
            for p in source_files
        }
    )
    identity = content_key(identity_parts)
    if (output / "result.json").exists():
        existing = read_result(output)
        if resume and existing.identity == identity:
            if not all(
                (output / file).exists()
                for file in ("manifest.json", "mteb-results.json", "report.md")
            ):
                raise ValueError("Incomplete output directory; use a fresh output path")
            return existing
        raise ValueError(
            "Output already has a result; use a fresh directory or --resume with identical inputs"
        )
    output.mkdir(parents=True, exist_ok=True)
    random.seed(config.seed)
    np.random.seed(config.seed)
    torch.manual_seed(config.seed)
    if device == "cuda":
        torch.cuda.manual_seed_all(config.seed)
        torch.cuda.reset_peak_memory_stats()
    model = adapter or create_adapter(selected, device)
    run_id = f"{datetime.now(UTC):%Y%m%dT%H%M%SZ}-{uuid.uuid4().hex[:8]}"
    write_json(
        output / "manifest.json",
        {"run_id": run_id, "status": "running", "identity": identity, **identity_parts},
    )
    try:
        with MemorySampler() as memory:
            load_start = time.perf_counter()
            model.load()
            load_seconds = time.perf_counter() - load_start
            bridge = MTEBSearchBridge(model, cache, identity_parts, device)
            task = ZimRetrievalTask(
                task_data, queries, config.split, document_language=config.document_language
            )
            benchmark = local_benchmark(task)
            native = mteb.evaluate(
                bridge,
                tasks=benchmark.tasks,
                cache=None,
                co2_tracker=False,
                show_progress_bar=False,
                public_only=False,
                encode_kwargs={"batch_size": config.batch_size},
                prediction_folder=output / "predictions",
            )
            native.to_disk(output / "mteb-results.json")
            docs = {d.document_id: d for d in data.documents}
            query_results = []
            for query in queries:
                scores = bridge.rankings[query.id]
                ranking = sorted(scores, key=lambda id_: (scores[id_], id_), reverse=True)
                failures = []
                if ranking[0] not in query.positive_document_ids:
                    failures.append("wrong-document-first")
                if not set(ranking[:10]) & set(query.positive_document_ids):
                    failures.append("relevant-missing-top-10")
                if set(ranking[:5]) & set(query.hard_negative_document_ids):
                    failures.append("hard-negative-in-top-5")
                if failures and query.code_switch:
                    failures.append("code-switch-query-failure")
                query_results.append(
                    QueryResult(
                        query_id=query.id,
                        query_language=query.query_language,
                        document_languages=sorted(
                            {docs[id_].language for id_ in query.positive_document_ids}
                        ),
                        domain=query.domain,
                        code_switch=query.code_switch is not None,
                        metrics=ranking_metrics(query.positive_document_ids, scores),
                        ranking=ranking,
                        relevance_scores=[scores[id_] for id_ in ranking],
                        positive_document_ids=query.positive_document_ids,
                        failures=failures,
                    )
                )
            efficiency: dict[str, Any] = {
                **bridge.efficiency,
                "document_language": config.document_language,
                "evaluated_queries": len(queries),
                "queries_without_target_positives": sorted(
                    eligible_query_ids - {query.id for query in queries}
                ),
                "model_load_seconds": load_seconds,
                "peak_rss_bytes_sampled": memory.peak,
                "peak_cuda_allocated_bytes": torch.cuda.max_memory_allocated()
                if device == "cuda"
                else None,
                "model_disk_bytes": model.metadata().get("model_disk_bytes"),
                "model_disk_bytes_note": model.metadata().get(
                    "model_disk_bytes_note", "Not applicable to the test adapter."
                ),
            }
            result = RunResult(
                run_id=run_id,
                timestamp=datetime.now(UTC),
                identity=identity,
                benchmark_version=data.manifest.benchmark_version,
                config=config,
                dataset_id=data.manifest.dataset_id,
                dataset_version=data.manifest.version,
                dataset_checksum=data.actual_checksum,
                model=selected,
                model_metadata=model.metadata(),
                environment=environment,
                synthetic=any(q.synthetic for q in queries),
                human_review_status=data.manifest.human_review_level,
                efficiency=efficiency,
                runtime_seconds=time.perf_counter() - start,
                queries=query_results,
                slices=slices(query_results),
                warnings=validation.warnings,
            )
            write_json(output / "result.json", result.model_dump(mode="json"))
            generate_report(result, output / "report.md")
            write_json(
                output / "manifest.json",
                {"run_id": run_id, "status": "complete", "identity": identity, **identity_parts},
            )
            return result
    except Exception as error:
        write_json(
            output / "manifest.json",
            {
                "run_id": run_id,
                "status": "failed",
                "error": str(error),
                "identity": identity,
                **identity_parts,
            },
        )
        raise
    finally:
        model.close()
