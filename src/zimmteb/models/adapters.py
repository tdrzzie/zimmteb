from typing import Any, Protocol

import numpy as np
from numpy.typing import NDArray

from zimmteb.config import ModelConfig

Embeddings = NDArray[np.float32]


class EmbeddingModelAdapter(Protocol):
    config: ModelConfig

    def load(self) -> None: ...
    def encode_queries(self, texts: list[str]) -> Embeddings: ...
    def encode_documents(self, texts: list[str]) -> Embeddings: ...
    def metadata(self) -> dict[str, Any]: ...
    def system_requirements(self) -> dict[str, Any]: ...
    def close(self) -> None: ...


class RerankerAdapter(Protocol):
    """Future boundary; no trained ZimMTEB reranker exists in Phase 1."""

    def load(self) -> None: ...
    def score(self, query: str, documents: list[str]) -> list[float]: ...
    def rerank(self, query: str, documents: list[str]) -> list[int]: ...
    def metadata(self) -> dict[str, Any]: ...
    def close(self) -> None: ...


class SentenceTransformerAdapter:
    def __init__(self, config: ModelConfig, device: str = "cpu") -> None:
        self.config, self.device = config, device
        self.model: Any = None

    def load(self) -> None:
        import re
        from pathlib import Path

        from sentence_transformers import SentenceTransformer

        if not Path(self.config.model_name).is_dir() and not re.fullmatch(r"[0-9a-f]{40}", self.config.revision):
            raise ValueError("Hub model revision must be an immutable 40-character commit SHA")
        self.model = SentenceTransformer(
            self.config.model_name, revision=self.config.revision,
            device=self.device, trust_remote_code=self.config.trust_remote_code,
        )
        self.model.max_seq_length = self.config.max_length
        self.model.eval()

    def _encode(self, texts: list[str], query: bool) -> Embeddings:
        if self.model is None:
            raise RuntimeError("Call load before encoding")
        method = self.model.encode_query if query else self.model.encode_document
        try:
            return np.asarray(method(
                texts, prompt=self.config.query_prefix if query else self.config.document_prefix,
                batch_size=self.config.batch_size, normalize_embeddings=self.config.normalize,
                precision=self.config.precision, convert_to_numpy=True, show_progress_bar=False,
            ), dtype=np.float32)
        except RuntimeError as error:
            if "out of memory" in str(error).lower():
                raise RuntimeError("Encoding ran out of memory. Lower --batch-size or max_length; explicitly select --device cpu if needed.") from error
            raise

    def encode_queries(self, texts: list[str]) -> Embeddings:
        return self._encode(texts, True)

    def encode_documents(self, texts: list[str]) -> Embeddings:
        return self._encode(texts, False)

    def metadata(self) -> dict[str, Any]:
        return {**self.config.model_dump(), "device": self.device,
                "parameter_count": sum(p.numel() for p in self.model.parameters()) if self.model is not None else None,
                "embedding_dimension": self.model.get_sentence_embedding_dimension() if self.model is not None else None}

    def system_requirements(self) -> dict[str, Any]:
        return {"backend": "pytorch", "device": self.device, "precision": self.config.precision}

    def close(self) -> None:
        self.model = None


class HashTestAdapter:
    """Stable lexical fixture for offline CI only; never a reported model baseline."""

    def __init__(self, config: ModelConfig, device: str = "cpu") -> None:
        self.config = config

    def load(self) -> None:
        pass

    def _encode(self, texts: list[str]) -> Embeddings:
        import hashlib
        import re

        output = np.zeros((len(texts), 128), dtype=np.float32)
        for row, text in zip(output, texts, strict=True):
            for token in re.findall(r"\w+", text.casefold()):
                row[int.from_bytes(hashlib.sha256(token.encode()).digest()[:4], "big") % 128] += 1
        if self.config.normalize:
            output /= np.maximum(np.linalg.norm(output, axis=1, keepdims=True), 1e-12)
        return output

    def encode_queries(self, texts: list[str]) -> Embeddings:
        return self._encode(texts)

    def encode_documents(self, texts: list[str]) -> Embeddings:
        return self._encode(texts)

    def metadata(self) -> dict[str, Any]:
        return {**self.config.model_dump(), "device": "cpu", "parameter_count": 0, "embedding_dimension": 128}

    def system_requirements(self) -> dict[str, Any]:
        return {"backend": "numpy", "device": "cpu"}

    def close(self) -> None:
        pass


def create_adapter(config: ModelConfig, device: str) -> EmbeddingModelAdapter:
    if config.adapter == "sentence-transformers":
        return SentenceTransformerAdapter(config, device)
    if config.adapter == "test-hash":
        return HashTestAdapter(config, device)
    raise ValueError(f"Adapter {config.adapter} is planned, not implemented; use a supported model")
