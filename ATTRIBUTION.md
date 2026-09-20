# Attribution

ZimMTEB extends dependencies rather than rebranding their repositories.

- [MTEB](https://github.com/embeddings-benchmark/mteb): task abstractions, benchmark grouping,
  evaluation execution, retrieval metrics and native result serialization (Apache-2.0).
- [Sentence Transformers](https://github.com/huggingface/sentence-transformers): model loading
  and batched asymmetric encoding; future training and reranking foundation (Apache-2.0).
- [Hugging Face](https://huggingface.co/docs): Datasets, Transformers, Hub and model hosting.
- [pytrec-eval-terrier](https://github.com/terrierteam/pytrec_eval): per-query retrieval audit metrics,
  also used by MTEB.
- [AfriMTEB / AfriE5](https://arxiv.org/abs/2510.23896): research reference and configured future baseline.
- [BGE / FlagEmbedding](https://github.com/FlagOpen/FlagEmbedding): configured dense BGE baseline
  and retrieval research reference; no source fork incorporated.
- [Meta SONAR](https://github.com/facebookresearch/SONAR): optional future adapter research only.
- Model owners and exact revisions/licenses are recorded in `configs/models`.

No external benchmark dataset was copied. Synthetic fixtures were drafted for this
project and are not native-speaker-validated. Attribution does not imply endorsement.

Foundational papers: [MTEB](https://arxiv.org/abs/2210.07316),
[MMTEB](https://arxiv.org/abs/2502.13595),
[Sentence-BERT](https://aclanthology.org/D19-1410/).
