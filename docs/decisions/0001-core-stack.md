# 0001 — MTEB and Sentence Transformers

Status: accepted for Phase 1, 2026-09-20.

Use MTEB 2.21.0 for task conventions, retrieval evaluation and native results.
Use Sentence Transformers 6.1.0 for embedding inference and future embedding and
CrossEncoder training. Do not fork either library or FlagEmbedding.

This preserves benchmark neutrality, familiar upstream contribution paths and
Hugging Face integration. A small adapter boundary permits other model families;
our eventual models use the same boundary. ZimMTEB owns Zimbabwe-specific data,
governance, slicing and reproducibility rather than inherited training machinery.

The cost is tracking upstream API changes and maintaining a tested compatibility
boundary. Pin the integration versions and upgrade through tests. Training and
non-retrieval task families are roadmap work, not implied by installed dependencies.
