# Evaluation and interpretation

MTEB executes `ZimRetrievalTask` using the ZimMTEB search bridge. Corpus and query
encoding remain distinct, with explicit prefixes and truncation. Exact search avoids
approximate-index recall confounds in Phase 1. Search scores use FP32 vectors.

Recall@k is retrieved positive count divided by total positive count; it is not
hit-rate when multiple positives exist. MRR@10 is reciprocal first-positive rank,
or zero if absent from top 10. nDCG@10 discounts binary relevance by log rank.
MAP@10 averages precision at relevant ranks using trec_eval's cutoff convention.
Per-query metrics use pytrec_eval, the same engine used by MTEB, with an explicit
descending document-ID tie policy. Native MTEB MRR may use its own stable tie order;
the integration keeps rankings in the same order to avoid ambiguity.

Run output includes native MTEB scores, per-query rankings, sliced metrics, environment,
manifest and Markdown. `results validate` recomputes metrics and aggregates.
`failures inspect` exposes mechanical errors, not inferred linguistic diagnoses.

`--document-language` explicitly changes the candidate corpus to all documents in
the selected language. Queries without a judged positive in that corpus are listed
as excluded; remaining judgments are projected onto the target corpus. Reports and
native task names distinguish this setting, and paired comparison rejects different
target corpora. `--language` alone remains a query filter over the full corpus.

Timing separates model load, corpus encoding/indexing, query encoding and ranking.
The run timer starts after upstream imports and excludes cold process startup.
GPU timing synchronizes around encoding. Batched amortized query milliseconds are
not production request latency. Cache hits are labeled and unsuitable for cold
inference comparisons. RSS is sampled process memory; CUDA memory is PyTorch allocator
peak, not total device use. Model disk size counts logical bytes in the selected
local directory or cached revision snapshot, excluding other revisions. It includes
auxiliary files and does not measure filesystem deduplication or a complete remote
repository; it is null if that location is unavailable. Warmup, repeated trials and isolated hardware
loads remain necessary for serious efficiency claims.

`benchmark compare` performs a paired bootstrap only for matching benchmark/data
identity, split and query IDs. It reports right-minus-left nDCG and a 95% percentile
interval. On this tiny, correlated fixture it is a software check, not a significance
test. Future source-cluster bootstrap should account for dependent translations.
