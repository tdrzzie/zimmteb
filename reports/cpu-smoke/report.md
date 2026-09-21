# ZimMTEB retrieval report

Run: `20260921T051049Z-f9694d9c`

Model: `intfloat/multilingual-e5-small` @ `614241f622f53c4eeff9890bdc4f31cfecc418b3`

Dataset: `tiny-synthetic` 0.1.0; benchmark 0.1.0
Checksum: `aaa7303c3cab917c70d9967a0f2f7af61351fbef0e012fde121411aa855b3566`

**Synthetic infrastructure measurements only. No linguistic validity or model superiority is established.**

Scores are query macro-averages on a shared corpus; unjudged documents count as nonrelevant.
Other-language equivalents may be false negatives in this tiny fixture.

| Slice | Value | Queries | Recall@1 | Recall@5 | Recall@10 | Recall@20 | MRR@10 | nDCG@10 | MAP@10 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| overall | all | 13 | 0.7692 | 1.0000 | 1.0000 | 1.0000 | 0.8590 | 0.8947 | 0.8590 |
| query_language | eng | 3 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| query_language | eng-nde-codeswitch | 2 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| query_language | eng-sna-codeswitch | 2 | 0.0000 | 1.0000 | 1.0000 | 1.0000 | 0.4167 | 0.5655 | 0.4167 |
| query_language | nde | 3 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| query_language | sna | 3 | 0.6667 | 1.0000 | 1.0000 | 1.0000 | 0.7778 | 0.8333 | 0.7778 |
| code_switch | eng-nde-codeswitch | 2 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| code_switch | eng-sna-codeswitch | 2 | 0.0000 | 1.0000 | 1.0000 | 1.0000 | 0.4167 | 0.5655 | 0.4167 |
| code_switch | monolingual | 9 | 0.8889 | 1.0000 | 1.0000 | 1.0000 | 0.9259 | 0.9444 | 0.9259 |
| domain | agriculture | 5 | 0.6000 | 1.0000 | 1.0000 | 1.0000 | 0.7667 | 0.8262 | 0.7667 |
| domain | customer-support | 2 | 0.5000 | 1.0000 | 1.0000 | 1.0000 | 0.6667 | 0.7500 | 0.6667 |
| domain | education | 2 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| domain | mobile-payments | 3 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| domain | technology-support | 1 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| language_domain | eng-nde-codeswitch/agriculture | 1 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| language_domain | eng-nde-codeswitch/customer-support | 1 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| language_domain | eng-sna-codeswitch/agriculture | 1 | 0.0000 | 1.0000 | 1.0000 | 1.0000 | 0.5000 | 0.6309 | 0.5000 |
| language_domain | eng-sna-codeswitch/customer-support | 1 | 0.0000 | 1.0000 | 1.0000 | 1.0000 | 0.3333 | 0.5000 | 0.3333 |
| language_domain | eng/agriculture | 1 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| language_domain | eng/mobile-payments | 1 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| language_domain | eng/technology-support | 1 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| language_domain | nde/agriculture | 1 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| language_domain | nde/education | 1 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| language_domain | nde/mobile-payments | 1 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| language_domain | sna/agriculture | 1 | 0.0000 | 1.0000 | 1.0000 | 1.0000 | 0.3333 | 0.5000 | 0.3333 |
| language_domain | sna/education | 1 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| language_domain | sna/mobile-payments | 1 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| language_pair | eng->eng | 3 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| language_pair | eng-nde-codeswitch->eng-nde-codeswitch | 2 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| language_pair | eng-sna-codeswitch->eng-sna-codeswitch | 2 | 0.0000 | 1.0000 | 1.0000 | 1.0000 | 0.4167 | 0.5655 | 0.4167 |
| language_pair | nde->nde | 3 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| language_pair | sna->sna | 3 | 0.6667 | 1.0000 | 1.0000 | 1.0000 | 0.7778 | 0.8333 | 0.7778 |
| task | retrieval | 13 | 0.7692 | 1.0000 | 1.0000 | 1.0000 | 0.8590 | 0.8947 | 0.8590 |

Not evaluated (domain): financial-services, public-information, telecommunications. These are missing values, not zero scores.

## Efficiency

Indexing and query phases are measured separately. Cached runs measure cache reads, not inference speed.
Batch query timing is not single-request latency. RSS peak is sampled; CUDA peak is allocator memory.

```json
{
  "cache_hits": [],
  "precision": "float32",
  "batch_size": 8,
  "timing_scope": "batched phases; no single-request latency claim",
  "index_seconds": 0.11501579999981004,
  "documents_per_second": 139.11132209684604,
  "corpus_documents": 16,
  "embedding_dimension": 384,
  "query_encoding_seconds": 0.05664870000009614,
  "query_search_seconds": 0.0573335000001407,
  "queries_per_second": 226.74352690779557,
  "amortized_query_ms": 4.410269230780054,
  "ranking_seconds": 0.0006877999999232998,
  "model_load_seconds": 2.7321316999998544,
  "peak_rss_bytes_sampled": 1399058432,
  "peak_cuda_allocated_bytes": null,
  "model_disk_bytes": 492795290,
  "model_disk_bytes_note": "Logical bytes of files present in the selected local model or cached snapshot; excludes other revisions and filesystem deduplication."
}
```

## Failures

- `q-sna-1` (sna, agriculture): wrong-document-first; top result `d-sna-2`
- `q-eng-sna-codeswitch-0` (eng-sna-codeswitch, customer-support): wrong-document-first, code-switch-query-failure; top result `d-eng-nde-codeswitch-0`
- `q-eng-sna-codeswitch-1` (eng-sna-codeswitch, agriculture): wrong-document-first, code-switch-query-failure; top result `d-eng-nde-codeswitch-1`

These labels are mechanical ranking observations; lexical traps and semantic causes require human analysis.

## Reproducibility

Git commit: `4d2010c8a649e18bbe13dbfc7fba2bc0f88cec34`; dirty: `True`.
Seed: 42; review level: unreviewed.
Native MTEB results and the manifest accompany this report. No task or score was submitted upstream.

## Limitations

- Synthetic infrastructure fixture; not evidence of language competence
- Unreviewed text; linguistic validity is not established
- This dataset is too small and unreviewed for significance claims.
- No trained zim-embed-small or zim-reranker is supplied.
