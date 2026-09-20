# 0002 — Separate code, data and weight licenses

Status: accepted. Inspected 2026-09-20.

Original code is Apache-2.0; original synthetic fixtures are dedicated under CC0-1.0.
No external dataset is redistributed. License metadata is mandatory before registry
admission. Hub model cards were inspected at the exact revisions in model configs.

| Artifact | Reported license | Evidence |
|---|---|---|
| MTEB | Apache-2.0 | [LICENSE](https://github.com/embeddings-benchmark/mteb/blob/main/LICENSE) |
| Sentence Transformers | Apache-2.0 | [LICENSE](https://github.com/huggingface/sentence-transformers/blob/main/LICENSE) |
| multilingual-e5-small weights | MIT | [card](https://huggingface.co/intfloat/multilingual-e5-small) |
| multilingual MiniLM weights | Apache-2.0 | [card](https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2) |
| BGE-M3 weights | MIT | [card](https://huggingface.co/BAAI/bge-m3) |
| AfriE5-Large-instruct weights | MIT | [card](https://huggingface.co/McGill-NLP/AfriE5-Large-instruct) |
| SONAR source | MIT | [code license](https://github.com/facebookresearch/SONAR/blob/main/CODE_LICENSE.md) |
| SONAR text encoder/decoder weights | CC-BY-NC-4.0 | [artifact license mapping](https://github.com/facebookresearch/SONAR/blob/main/LICENSE.md) |

Dependencies do not transfer their license to all models/datasets. Model configuration
is not redistribution of weights. Recheck exact artifacts before publication or
commercial use, including upstream training-data restrictions. SONAR is not installed
or downloaded in Phase 1. Do not treat all SONAR speech and text checkpoints alike.
