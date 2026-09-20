# Benchmark design

The research question is whether modern multilingual embeddings retrieve locally
relevant information across English, Shona, Northern Ndebele and code-switching,
and whether smaller adapted models can approach larger systems at lower cost.
Phase 1 validates infrastructure, not that hypothesis.

The synthetic test-only dataset has 13 queries and 16 documents. All five tracks
have queries, but not all eight declared domains do. Reports identify absent query
coverage. The shared corpus contains cross-language distractors; only explicitly
judged positives count as relevant. Semantically equivalent translations may be
unjudged, so scores must not be interpreted as a language-quality comparison.

The task uses dense dot products (cosine when normalized), top-20 retrieval and
binary relevance. Query slicing retains the same corpus. Macro-average over queries
is the overall statistic; uneven counts mean it is not an equal-language average.
Language, domain, code-switch and language/domain intersections remain visible.

Future experimental questions include cross-language directionality, natural switch
frequency, domain difficulty, hard-negative ablations, reranking quality/latency and
parameter/VRAM tradeoffs. STS, classification, bitext mining and reranking need their
own data schemas, MTEB tasks and controls. They are not implemented by this retrieval
fixture. Baseline rankings and scientific results are forthcoming.
