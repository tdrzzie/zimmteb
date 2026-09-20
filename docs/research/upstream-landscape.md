# Upstream landscape

Inspected 2026-09-20 before implementation. PyPI reports **MTEB 2.21.0** and
**Sentence Transformers 6.1.0**. These are the Phase 1 integration targets; the
lockfile captures transitive dependencies. Repository `main` is discovery material,
not a reproducibility pin. Installed release source is the final API authority.

## MTEB

[Repository](https://github.com/embeddings-benchmark/mteb),
[task contribution guide](https://docs.mteb.org/contributing/adding_a_dataset/),
[evaluation guide](https://github.com/embeddings-benchmark/mteb/blob/main/docs/get_started/usage/running_the_evaluation.md).

Current usage calls `mteb.evaluate(model, tasks=...)`. `AbsTaskRetrieval` represents
each subset/split as corpus and query Hugging Face Datasets with `id` and `text`,
plus relevance judgments and optional candidate rankings. `TaskMetadata` describes
languages using ISO/script tags, dataset revision, task type, splits and main score.
Custom local tasks override loading; no installed source edits are needed.

Retrieval accepts encoder, cross-encoder or search protocols. A ZimMTEB search bridge
can preserve model-neutral encoding and cache policy while MTEB executes evaluation.
MTEB owns ranking metrics and native TaskResult serialization. ZimMTEB keeps its
own versioned envelope for provenance, slices and resource measurements.

Benchmarks group task instances; upstream discovery is distinct from creating a
local Benchmark object. `get_benchmark("ZimMTEB")` must not be advertised as working
until upstream acceptance. STS, classification, reranking and bitext have dedicated
abstractions; merely renaming retrieval does not implement them. Upstream submission
requires reviewed data, stable hosted revisions, metadata, tests and maintainer
review. Local synthetic fixtures are not leaderboard submissions.

MTEB supports result caching and model wrappers; embedding-cache identities still
need model revision, prompts and exact data content. Saved predictions permit
per-query audits. Public result submissions follow the current MTEB results and
leaderboard process, not an automatic ZimMTEB upload.

## Sentence Transformers

[Repository](https://github.com/huggingface/sentence-transformers),
[inference](https://www.sbert.net/docs/sentence_transformer/usage/usage.html),
[CrossEncoder training](https://www.sbert.net/docs/cross_encoder/training_overview.html),
[hard-negative API](https://www.sbert.net/docs/package_reference/util/hard_negatives.html).

`SentenceTransformer` supports pinned Hub or local models, devices and batched
encoding. `encode_query` and `encode_document` select asymmetric routes/prompts;
explicit configuration must preserve model-specific prefixes. Normalization and
sequence truncation affect evaluation and cache identity. Integer embedding
quantization is not the same as FP16 weight inference.

Training uses `SentenceTransformerTrainer`, training arguments, HF Datasets,
losses and evaluators. Multiple-negatives losses need careful false-negative and
duplicate control; cached variants enable larger effective contrastive batches.
Gradient accumulation alone does not enlarge the negative pool of each loss call.
`CrossEncoder` scores pairs; its trainer supports pointwise and ranking losses.
`mine_hard_negatives` supports rank/score ranges, margins, reranker filtering and
multiple output formats. Mining must operate on training partitions only.
Sparse and multi-vector families are distinct extension points, deferred from the
first dense retrieval implementation. Model cards and Hub publishing are available,
but publication is a separate, explicit operation.

## AfriMTEB / AfriE5

[Paper, revision 2](https://arxiv.org/html/2510.23896v2),
[research implementation](https://github.com/LLMforLRL/FlagEmbedding-AfriE5),
[model card](https://huggingface.co/McGill-NLP/AfriE5-Large-instruct).

The paper describes 59 languages and 38 datasets; the balanced Lite subset covers
nine languages, excluding Shona and Northern Ndebele. AfriE5 adapts multilingual
E5 using cross-lingual contrastive learning and teacher scores. Translated NLI,
translation quality filtering and BGE reranker distillation are useful ablations
to compare, not assumptions about Zimbabwean retrieval quality. The study motivates
balanced language/task reporting. Zimbabwean domains and natural code-switching
remain a separate empirical question; this is not a claim that no existing dataset
contains any Shona. Do not substitute Southern Ndebele or Zulu for `nde`.

## BGE / FlagEmbedding

[Repository](https://github.com/FlagOpen/FlagEmbedding),
[BGE-M3 card](https://huggingface.co/BAAI/bge-m3).

BGE-M3 is a multilingual baseline supporting dense, sparse and multi-vector
retrieval. Phase 1 templates concern dense encoding only. Its extended retrieval
features warrant separate tracks; mixing them into the dense comparison would
change the system being measured. BGE rerankers are future candidate baselines.
FlagEmbedding is not the benchmark architecture and is not vendored.

## SONAR

[Repository](https://github.com/facebookresearch/SONAR),
[checkpoint language card](https://github.com/facebookresearch/SONAR/blob/main/sonar/cards/text_sonar_basic_encoder.yaml).

The inspected text encoder card contains `eng_Latn` and `sna_Latn`, but neither
`nde_Latn` nor `nbl_Latn`. No Northern Ndebele coverage is inferred from Zulu.
SONAR offers a shared multilingual speech/text representation, with Fairseq2 and
PyTorch/platform constraints. It remains a planned optional adapter, with no SONAR
dependency in the base install. Checkpoint weights have separate licensing from
the source package (see licensing ADR).
