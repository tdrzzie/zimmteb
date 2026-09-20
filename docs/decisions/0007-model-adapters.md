# 0007 — Neutral encoder and reranker interfaces

Status: accepted.

Benchmark orchestration depends on `EmbeddingModelAdapter`, not a concrete ST model.
The primary implementation uses public `SentenceTransformer`, `encode_query` and
`encode_document`. Keep prompt whitespace, normalization, revision, truncation and
batch size explicit. Remote code is disabled. Local artifacts receive content hashes.

Phase 1 accepts FP32 output only; quantized embeddings need a calibrated scoring
policy and separate verification. SONAR, native FlagEmbedding and reranker execution
are deferred. Their protocol/configuration preparation does not imply implementation.
