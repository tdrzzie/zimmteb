"""MTEB 2.21 task integration. Local tasks are not registered globally upstream."""

import hashlib
import time
from pathlib import Path
from typing import Any

import numpy as np
from datasets.arrow_dataset import Dataset
from mteb import TaskMetadata
from mteb.abstasks import AbsTaskRetrieval
from mteb.benchmarks import Benchmark
from mteb.models import ModelMeta

from zimmteb.cache import EmbeddingCache, check_embeddings, content_key
from zimmteb.config import registry
from zimmteb.datasets.registry import RetrievalDataset
from zimmteb.datasets.schema import Query
from zimmteb.models.adapters import EmbeddingModelAdapter, Embeddings


class ZimRetrievalTask(AbsTaskRetrieval):
    def __init__(
        self,
        data: RetrievalDataset,
        queries: list[Query],
        split: str = "test",
        *,
        document_language: str | None = None,
    ) -> None:
        self.source = data
        self.selected_queries = queries
        self.selected_split = split
        languages = registry("languages")
        codes: set[str] = set()
        for query in queries:
            language = languages[query.query_language]
            codes.update(language.code_switch_partners or [language.code])
        for document in data.documents:
            language = languages[document.language]
            codes.update(language.code_switch_partners or [language.code])
        synthetic_queries = all(query.synthetic for query in queries)
        task_name = (
            "ZimMTEBTinyRetrieval"
            if data.manifest.dataset_id == "tiny-synthetic"
            else "ZimMTEBRetrieval"
            + hashlib.sha256(data.manifest.dataset_id.encode()).hexdigest()[:12]
        )
        self.metadata = TaskMetadata(
            name=task_name
            + ("To" + document_language.replace("-", "").title() if document_language else ""),
            description=f"Local retrieval dataset {data.manifest.dataset_id}; review level {data.manifest.human_review_level}. See dataset provenance; no upstream registration.",
            dataset={"path": "zimmteb/local-dataset", "revision": data.actual_checksum},
            type="Retrieval",
            category="t2t",
            eval_splits=[split],
            eval_langs={"default": [f"{code}-Latn" for code in sorted(codes)]},
            main_score="ndcg_at_10",
            license=data.manifest.license.lower(),
            domains=["Constructed"] if synthetic_queries else None,
            annotations_creators="LM-generated" if synthetic_queries else None,
            is_public=False,
        )
        super().__init__()
        self.k_values = [1, 5, 10, 20]
        self._top_k = 20

    def load_data(self, num_proc: int | None = None, *, timer: Any = None, **kwargs: Any) -> None:
        self.dataset = {
            "default": {
                self.selected_split: {
                    "corpus": Dataset.from_list(
                        [
                            {"id": d.document_id, "text": d.text, "title": d.title}
                            for d in self.source.documents
                        ]
                    ),
                    "queries": Dataset.from_list(
                        [{"id": q.id, "text": q.query} for q in self.selected_queries]
                    ),
                    "relevant_docs": {
                        q.id: {id_: 1 for id_ in q.positive_document_ids}
                        for q in self.selected_queries
                    },
                    "top_ranked": None,
                }
            }
        }
        self.data_loaded = True

    def unload_data(self) -> None:
        # Upstream resets instance metadata to a published class-level definition.
        # This local task constructs metadata from its manifest and selected queries.
        self.dataset = {}
        self.data_loaded = False


def local_benchmark(task: ZimRetrievalTask) -> Benchmark:
    return Benchmark(
        name=f"ZimMTEB(v{task.source.manifest.benchmark_version},local)",
        tasks=[task],
        description="Local retrieval benchmark. No upstream registration or language-validity claim.",
    )


class MTEBSearchBridge:
    """Exact dense dot-product search, batched by query; implements SearchProtocol."""

    def __init__(
        self,
        adapter: EmbeddingModelAdapter,
        cache: Path | None,
        identity: dict[str, Any],
        device: str,
    ) -> None:
        self.adapter = adapter
        self.cache = EmbeddingCache(cache) if cache else None
        self.identity = identity
        self.device = device
        meta = adapter.metadata()
        self.mteb_model_meta = ModelMeta.create_empty(
            overwrites={
                "name": adapter.config.model_name,
                "revision": adapter.config.revision,
                "framework": ["Sentence Transformers"]
                if adapter.config.adapter == "sentence-transformers"
                else [],
                "n_parameters": meta.get("parameter_count"),
                "embed_dim": meta.get("embedding_dimension"),
                "max_tokens": adapter.config.max_length,
                "similarity_fn_name": "dot",
            }
        )
        self.corpus_ids: list[str] = []
        self.corpus_embeddings: Embeddings = np.empty((0, 0), dtype=np.float32)
        self.rankings: dict[str, dict[str, float]] = {}
        self.efficiency: dict[str, Any] = {
            "cache_hits": [],
            "precision": adapter.config.precision,
            "batch_size": adapter.config.batch_size,
            "timing_scope": "batched phases; no single-request latency claim",
        }

    def _sync(self) -> None:
        if self.device == "cuda":
            import torch

            torch.cuda.synchronize()

    def _encode(self, texts: list[str], role: str, split: str) -> Embeddings:
        key = content_key(
            {
                **self.identity,
                "model": self.adapter.config.model_dump(),
                "role": role,
                "split": split,
                "texts": texts,
                "preprocessing": "title-space-text-v1",
            }
        )
        values = self.cache.get(key, len(texts)) if self.cache else None
        if values is not None:
            self.efficiency["cache_hits"].append(role)
            return values
        values = (
            self.adapter.encode_queries(texts)
            if role == "query"
            else self.adapter.encode_documents(texts)
        )
        check_embeddings(values, len(texts))
        if self.cache:
            self.cache.put(key, values)
        return values

    def index(self, corpus: Any, *, hf_split: str, **kwargs: Any) -> None:
        self.corpus_ids = list(corpus["id"])
        texts = [(row.get("title", "") + " " + row["text"]).strip() for row in corpus]
        self._sync()
        start = time.perf_counter()
        self.corpus_embeddings = self._encode(texts, "document", hf_split)
        self._sync()
        elapsed = time.perf_counter() - start
        self.efficiency.update(
            index_seconds=elapsed,
            documents_per_second=len(texts) / elapsed,
            corpus_documents=len(texts),
            embedding_dimension=self.corpus_embeddings.shape[1],
        )

    def search(
        self, queries: Any, *, hf_split: str, top_k: int, top_ranked: Any = None, **kwargs: Any
    ) -> dict[str, dict[str, float]]:
        if top_ranked is not None:
            raise ValueError("Reranking is not implemented in Phase 1")
        self._sync()
        start = time.perf_counter()
        embeddings = self._encode(list(queries["text"]), "query", hf_split)
        self._sync()
        encoded = time.perf_counter()
        if embeddings.shape[1] != self.corpus_embeddings.shape[1]:
            raise ValueError("Query/document embedding dimensions differ")
        query_ids = list(queries["id"])
        for offset in range(0, len(embeddings), self.adapter.config.batch_size):
            block = (
                embeddings[offset : offset + self.adapter.config.batch_size]
                @ self.corpus_embeddings.T
            )
            for id_, row in zip(query_ids[offset : offset + len(block)], block, strict=True):
                if not np.isfinite(row).all():
                    raise ValueError("Non-finite similarity scores")
                order = sorted(
                    range(len(row)), key=lambda i: (float(row[i]), self.corpus_ids[i]), reverse=True
                )[:top_k]
                self.rankings[id_] = {self.corpus_ids[i]: float(row[i]) for i in order}
        elapsed = time.perf_counter() - start
        self.efficiency.update(
            query_encoding_seconds=encoded - start,
            query_search_seconds=elapsed,
            queries_per_second=len(query_ids) / elapsed,
            amortized_query_ms=1000 * elapsed / len(query_ids),
            ranking_seconds=time.perf_counter() - encoded,
        )
        return self.rankings
