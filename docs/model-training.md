# Model adaptation plan

Neither `zim-embed-small` nor `zim-reranker` is trained or released. Phase 1 ships
interfaces, card templates and a clearly marked planned hardware configuration.
There are no working `train` or `mining` CLI commands yet.

Start with reviewed, independently split query-positive pairs, then compare
MultipleNegativesRankingLoss and its cached variant with and without mined negatives.
Use current SentenceTransformerTrainer/TrainingArguments and HF Datasets. Avoid
duplicate/translation-family negatives within batches. Cached losses can improve the
negative pool under memory constraints; ordinary accumulation alone does not.

Wrap the current `mine_hard_negatives` helper: training corpus only, remove all known
positives, record model revision, top-k, margins/score ranges, output format and seed.
Audit false-negative risk, language/domain, length, cosine and lexical overlap. Version
the output independently. Compare cross-lingual contrastive training and distillation
as separate ablations, informed by AfriE5 without copying its training repository.

For the 8 GB RTX 4060 target, begin with length 128, micro-batch 4, FP16 where stable,
gradient checkpointing, cached loss mini-batch 2 and periodic resumable checkpoints.
Measure VRAM before increasing batch size. Fail clearly on OOM; never silently move
training to CPU. Keep optimizer/loss/base revision/data/checksum/hardware in experiment JSON.

For reranking, use CrossEncoder and CrossEncoderTrainer with reviewed pair labels or
ranking groups. Compare retrieval, generic reranking and adapted reranking on identical
candidate sets; measure added latency and candidate recall ceiling. No held-out test
examples or mined test negatives may become adaptation data.
